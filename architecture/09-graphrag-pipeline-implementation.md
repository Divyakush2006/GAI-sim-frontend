# GovernAI Studio — GraphRAG Pipeline Implementation Guide
## v3.0 · May 2026

> **Priority:** This is the FIRST thing to build. The entire Whisperer, Coach, and Drafting Partner depend on it.
> **Cost:** ₹0. All tools are open-source or free-tier.

---

## 1. Pipeline Overview

```
PHASE 1: Corpus Assembly (Manual + Script)
    53 source documents → cleaned text files
        │
PHASE 2: Graph Construction (LightRAG + Gemini Free)
    text files → entity extraction → relationship mapping → knowledge graph
        │
PHASE 3: Embedding + Indexing (Custom or Gemini Free)
    graph + chunks → vector embeddings → hybrid index
        │
PHASE 4: Query Engine (Hybrid Retrieval)
    officer query → classify → vector OR graph traversal → rerank → response
        │
PHASE 5: Integration (FastAPI endpoints)
    query engine → Whisperer API → Simulation UI
```

---

## 2. Phase 1: Corpus Assembly

### 2.1 Source Documents (53 documents, ~9,000 chunks)

| Category | Documents | Format | Priority |
|---|---|---|---|
| **Primary Statutes** | DPDP Act 2023, IT Act 2000, Aadhaar Act 2016, BNS 2023, Consumer Protection Act 2019, Copyright Act 1957, RTI Act 2005 | PDF → Text | P0 |
| **AI Governance** | India AI Governance Guidelines 2025, NITI Aayog Responsible AI 2021, RBI FREE-AI Report 2025 | PDF → Text | P0 |
| **Competency Frameworks** | MeitY AI Competency Framework 2024, UNESCO AI Competencies 2022 | PDF → Text | P0 |
| **Procurement** | GFR 2017 (Rules 144-175), GeM Guidelines, CVC Circulars on IT procurement | PDF → Text | P1 |
| **Sectoral** | RBI AI Guidelines, SEBI Circular on Algo Trading, IRDAI AI Framework, TRAI Recommendations, ICMR AI Ethics | PDF → Text | P1 |
| **Standards** | BIS IS/ISO 42001, IS/ISO 23894, IS/ISO 24028 (selected sections) | PDF → Text | P2 |
| **International Reference** | EU AI Act (summary), OECD AI Principles, G7 Hiroshima Process | PDF → Text | P2 |

### 2.2 Corpus Ingestion Script

```python
# corpus/ingest.py
import os
import re
from pathlib import Path
from dataclasses import dataclass

@dataclass
class CorpusDocument:
    title: str
    source_type: str           # statute | guideline | standard | framework | report
    year: int
    sections: list[dict]       # [{section_ref, text, page_num}]
    scenario_relevance: list[str]  # scenario slugs this doc is relevant to

class CorpusIngester:
    """Converts raw PDFs/texts into structured chunks for LightRAG."""
    
    CHUNK_SIZE = 300           # tokens
    CHUNK_OVERLAP = 50         # tokens
    
    def __init__(self, corpus_dir: str = "./corpus/raw"):
        self.corpus_dir = Path(corpus_dir)
        self.processed_dir = Path("./corpus/processed")
        self.processed_dir.mkdir(exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (free, no API needed)."""
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += f"\n[PAGE {page.number + 1}]\n"
            text += page.get_text("text")
        return text
    
    def clean_legal_text(self, text: str) -> str:
        """Clean common PDF artifacts from Indian legal documents."""
        # Remove page headers/footers
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'Gazette of India.*?\n', '', text)
        # Normalize section references
        text = re.sub(r'Section\s+(\d+)', r'Section \1', text)
        text = re.sub(r'Rule\s+(\d+)', r'Rule \1', text)
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    def section_split(self, text: str, doc_type: str) -> list[dict]:
        """Split by legal sections/rules/articles rather than arbitrary chunks."""
        if doc_type == "statute":
            # Split on "Section X." or "Rule X."
            pattern = r'((?:Section|Rule|Article)\s+\d+[A-Z]?\.?\s)'
            parts = re.split(pattern, text)
        elif doc_type == "guideline":
            # Split on numbered headings
            pattern = r'(\d+\.\d+\.?\s+[A-Z])'
            parts = re.split(pattern, text)
        else:
            # Default: paragraph-level split
            parts = text.split('\n\n')
        
        sections = []
        current_ref = "Preamble"
        for part in parts:
            ref_match = re.match(r'(Section|Rule|Article)\s+(\d+[A-Z]?)', part)
            if ref_match:
                current_ref = ref_match.group(0)
            elif len(part.strip()) > 50:  # Skip tiny fragments
                sections.append({
                    "section_ref": current_ref,
                    "text": part.strip(),
                })
        return sections
    
    def chunk_with_overlap(self, sections: list[dict]) -> list[dict]:
        """Further chunk long sections while preserving section metadata."""
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        
        chunks = []
        for section in sections:
            tokens = enc.encode(section["text"])
            if len(tokens) <= self.CHUNK_SIZE:
                chunks.append(section)
            else:
                # Sliding window with overlap
                for i in range(0, len(tokens), self.CHUNK_SIZE - self.CHUNK_OVERLAP):
                    chunk_tokens = tokens[i:i + self.CHUNK_SIZE]
                    chunk_text = enc.decode(chunk_tokens)
                    chunks.append({
                        "section_ref": section["section_ref"],
                        "text": chunk_text,
                        "chunk_index": len(chunks),
                    })
        return chunks
    
    def process_document(self, doc: CorpusDocument, raw_text: str) -> list[dict]:
        """Full pipeline: clean → section split → chunk → metadata."""
        cleaned = self.clean_legal_text(raw_text)
        sections = self.section_split(cleaned, doc.source_type)
        chunks = self.chunk_with_overlap(sections)
        
        # Add metadata to each chunk
        for chunk in chunks:
            chunk["document_title"] = doc.title
            chunk["source_type"] = doc.source_type
            chunk["year"] = doc.year
            chunk["scenario_relevance"] = ",".join(doc.scenario_relevance)
        
        return chunks
```

---

## 3. Phase 2: Graph Construction with LightRAG

### 3.1 Setup and Configuration

```python
# corpus/graph_builder.py
import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm import gemini_complete, gemini_embedding
from lightrag.utils import EmbeddingFunc
import numpy as np

# Environment setup
os.environ["GEMINI_API_KEY"] = "your-free-api-key"

class GovernAIGraphBuilder:
    """Builds and manages the GovernAI knowledge graph using LightRAG."""
    
    def __init__(self, working_dir: str = "./graph_data"):
        self.working_dir = working_dir
        os.makedirs(working_dir, exist_ok=True)
        
        self.rag = LightRAG(
            working_dir=working_dir,
            
            # LLM for entity extraction (uses Gemini free tier)
            llm_model_func=gemini_complete,
            llm_model_name="gemini-2.0-flash",
            llm_model_max_async=2,       # Stay under 15 RPM
            llm_model_max_token_size=2000,
            
            # Embedding function
            embedding_func=EmbeddingFunc(
                embedding_dim=768,
                max_token_size=8192,
                func=self._embed_with_gemini,
            ),
            
            # Chunking (our pre-chunked text will be further processed)
            chunk_token_size=300,
            chunk_overlap_token_size=50,
            
            # Entity extraction parameters
            entity_extract_max_gleaning=2,  # Balance quality vs API cost
            
            # Graph storage (file-based, free)
            graph_storage="NetworkXStorage",
            
            # Vector storage (built-in, free)
            vector_storage="NanoVectorDBStorage",
            
            # KV storage
            kv_storage="JsonKVStorage",
        )
    
    async def _embed_with_gemini(self, texts: list[str]) -> np.ndarray:
        """Use Gemini free embedding API."""
        import google.generativeai as genai
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=texts,
            task_type="retrieval_document",
        )
        return np.array(result['embedding'])
    
    async def ingest_all(self, processed_chunks: list[dict]):
        """Ingest all corpus chunks into the knowledge graph.
        
        IMPORTANT: Run this during off-peak hours (late night IST) to 
        avoid hitting Gemini rate limits. Estimated: ~3-4 hours for 9K chunks.
        """
        # Format chunks with metadata prefix for better entity extraction
        documents = []
        for chunk in processed_chunks:
            doc_text = (
                f"[Document: {chunk['document_title']}] "
                f"[Section: {chunk['section_ref']}] "
                f"[Type: {chunk['source_type']}] "
                f"[Year: {chunk['year']}]\n\n"
                f"{chunk['text']}"
            )
            documents.append(doc_text)
        
        # Batch insert (LightRAG handles batching internally)
        batch_size = 10  # Small batches to respect rate limits
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            combined = "\n\n---\n\n".join(batch)
            await self.rag.ainsert(combined)
            
            # Rate limit pause (Gemini free: 15 RPM)
            if (i // batch_size) % 5 == 0:
                print(f"Processed {i + batch_size}/{len(documents)} chunks...")
                await asyncio.sleep(10)  # Pause every 5 batches
    
    async def query(self, query: str, mode: str = "hybrid") -> str:
        """Query the knowledge graph.
        
        Modes:
          - naive:  Pure vector search (fast, simple queries)
          - local:  Entity-focused graph traversal (specific clauses)
          - global: Community-level thematic search (principles, themes)
          - hybrid: Both local + global (default, best quality)
        """
        return await self.rag.aquery(
            query,
            param=QueryParam(mode=mode, top_k=5)
        )
    
    def get_graph_stats(self) -> dict:
        """Get statistics about the constructed knowledge graph."""
        import networkx as nx
        G = nx.read_graphml(f"{self.working_dir}/graph_chunk_entity_relation.graphml")
        return {
            "total_entities": G.number_of_nodes(),
            "total_relationships": G.number_of_edges(),
            "entity_types": len(set(nx.get_node_attributes(G, 'entity_type').values())),
            "connected_components": nx.number_connected_components(G.to_undirected()),
        }
```

### 3.2 Graph Construction Script (Run Once)

```python
# scripts/build_graph.py
"""
One-time script to build the GovernAI knowledge graph.
Run on Kaggle/Colab for free GPU, or locally.

Estimated time: 3-4 hours (rate-limited by Gemini free tier)
Estimated cost: ₹0
"""
import asyncio
from corpus.ingest import CorpusIngester, CorpusDocument
from corpus.graph_builder import GovernAIGraphBuilder

# Define corpus manifest
CORPUS_MANIFEST = [
    CorpusDocument(
        title="Digital Personal Data Protection Act 2023",
        source_type="statute",
        year=2023,
        sections=[],
        scenario_relevance=["vendor-free-ai", "twelve-thousand-rejections", 
                           "aadhaar-numbers-chatbot", "cameras-market"],
    ),
    CorpusDocument(
        title="India AI Governance Guidelines 2025",
        source_type="guideline", 
        year=2025,
        sections=[],
        scenario_relevance=["all"],  # Relevant to every scenario
    ),
    CorpusDocument(
        title="General Financial Rules 2017",
        source_type="statute",
        year=2017,
        sections=[],
        scenario_relevance=["vendor-free-ai", "rfp-cant-copy-gem"],
    ),
    # ... remaining 50 documents defined similarly
]

async def main():
    ingester = CorpusIngester()
    builder = GovernAIGraphBuilder()
    
    all_chunks = []
    for doc in CORPUS_MANIFEST:
        # Extract text from PDF
        pdf_path = f"./corpus/raw/{doc.title}.pdf"
        raw_text = ingester.extract_text_from_pdf(pdf_path)
        
        # Process into chunks
        chunks = ingester.process_document(doc, raw_text)
        all_chunks.extend(chunks)
        print(f"Processed {doc.title}: {len(chunks)} chunks")
    
    print(f"\nTotal chunks: {len(all_chunks)}")
    print("Starting graph construction (this will take 3-4 hours)...")
    
    await builder.ingest_all(all_chunks)
    
    stats = builder.get_graph_stats()
    print(f"\nGraph built successfully!")
    print(f"  Entities: {stats['total_entities']}")
    print(f"  Relationships: {stats['total_relationships']}")
    print(f"  Entity types: {stats['entity_types']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3.3 Expected Knowledge Graph Output

After construction, the graph will contain approximately:

| Metric | Estimate |
|---|---|
| Entities (statutes, sections, institutions, concepts) | ~2,000-3,000 |
| Relationships (references, defines, governs, etc.) | ~5,000-8,000 |
| Communities (thematic clusters) | ~50-100 |
| Storage on disk | ~100-200 MB |

---

## 4. Phase 3: Hybrid Retrieval Engine

### 4.1 Adaptive Query Router

```python
# retrieval/query_router.py
import re
from enum import Enum

class QueryComplexity(Enum):
    SIMPLE = "naive"      # Direct fact lookup
    ENTITY = "local"      # Specific clause/section
    THEMATIC = "global"   # Principle/concept level
    COMPLEX = "hybrid"    # Multi-hop cross-document

class QueryRouter:
    """Classifies query complexity to route to optimal retrieval mode.
    
    Rule-based (no LLM call needed — saves rate limit budget).
    """
    
    SECTION_PATTERNS = [
        r'section\s+\d+', r'rule\s+\d+', r'article\s+\d+',
        r'clause\s+\d+', r'para\s+\d+',
    ]
    
    THEMATIC_KEYWORDS = [
        'principle', 'sutra', 'framework', 'approach', 'philosophy',
        'how should', 'what is the best', 'compare', 'relationship between',
    ]
    
    CROSS_DOC_INDICATORS = [
        'and', 'conflict', 'interact', 'together', 'versus', 'vs',
        'which acts', 'which laws', 'multiple', 'both',
    ]
    
    def classify(self, query: str) -> QueryComplexity:
        query_lower = query.lower()
        
        # Check for specific section references → entity-level search
        for pattern in self.SECTION_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryComplexity.ENTITY
        
        # Check for thematic/conceptual queries → global search
        if any(kw in query_lower for kw in self.THEMATIC_KEYWORDS):
            return QueryComplexity.THEMATIC
        
        # Check for cross-document queries → hybrid search
        if any(ind in query_lower for ind in self.CROSS_DOC_INDICATORS):
            return QueryComplexity.COMPLEX
        
        # Default: simple vector search (fastest)
        return QueryComplexity.SIMPLE
```

### 4.2 Complete Retrieval Pipeline

```python
# retrieval/pipeline.py
from retrieval.query_router import QueryRouter, QueryComplexity
from corpus.graph_builder import GovernAIGraphBuilder

class GovernAIRetriever:
    """The complete retrieval pipeline for the Reference Whisperer."""
    
    def __init__(self, graph: GovernAIGraphBuilder):
        self.graph = graph
        self.router = QueryRouter()
    
    async def retrieve(self, 
                       scenario_context: str,
                       decision_prompt: str,
                       whisperer_keywords: list[str] = None) -> dict:
        """
        Main retrieval entry point.
        
        Returns structured references with source attribution.
        """
        # Step 1: Build enriched query
        query_parts = [decision_prompt]
        if scenario_context:
            query_parts.insert(0, f"Context: {scenario_context}")
        if whisperer_keywords:
            query_parts.append(f"Keywords: {', '.join(whisperer_keywords)}")
        full_query = "\n".join(query_parts)
        
        # Step 2: Classify complexity
        complexity = self.router.classify(full_query)
        
        # Step 3: Execute retrieval
        raw_result = await self.graph.query(
            query=full_query,
            mode=complexity.value
        )
        
        # Step 4: Structure the response
        return {
            "query": decision_prompt,
            "mode_used": complexity.value,
            "raw_response": raw_result,
            "disclaimer": "Contextual suggestions, not legal advice.",
        }
```

---

## 5. Phase 4: Integration with Simulation Engine

### 5.1 Whisperer FastAPI Endpoint

```python
# api/routes/whisperer.py
from fastapi import APIRouter, Depends
from retrieval.pipeline import GovernAIRetriever

router = APIRouter(prefix="/v1/sessions", tags=["whisperer"])

@router.get("/{session_id}/reference")
async def get_references(
    session_id: str,
    decision_moment_id: str,
    retriever: GovernAIRetriever = Depends(get_retriever),
    session: dict = Depends(get_current_session),
):
    """Reference Whisperer endpoint — graph-powered reference surfacing."""
    
    # Get decision context from session
    decision = get_decision_moment(session, decision_moment_id)
    
    # Retrieve references via GraphRAG
    result = await retriever.retrieve(
        scenario_context=session["scenario"]["setting"]["narrative"],
        decision_prompt=decision["prompt_text"],
        whisperer_keywords=decision.get("whisperer_keywords", []),
    )
    
    return {
        "references": result["raw_response"],
        "mode": result["mode_used"],
        "disclaimer": result["disclaimer"],
    }
```

---

## 6. Evaluation Framework (Build BEFORE Deploying)

### 6.1 Golden Test Dataset

```python
# evaluation/golden_dataset.py
"""
50 hand-crafted query → expected_references pairs.
Built by content author + legal advisor.
"""

GOLDEN_QUERIES = [
    {
        "query": "What data residency requirements apply to AI procurement?",
        "expected_sources": ["DPDP Act Section 17", "GFR Rule 144"],
        "expected_mode": "hybrid",
        "min_relevance": 0.8,
    },
    {
        "query": "Section 8(1) of the DPDP Act",
        "expected_sources": ["DPDP Act Section 8(1)"],
        "expected_mode": "local",
        "min_relevance": 0.95,
    },
    {
        "query": "How do the Seven Sutras relate to RBI FREE-AI principles?",
        "expected_sources": ["India AI Guidelines", "RBI FREE-AI Report"],
        "expected_mode": "global",
        "min_relevance": 0.7,
    },
    # ... 47 more queries covering all scenarios
]
```

### 6.2 Automated Evaluation Script

```python
# evaluation/run_eval.py
async def evaluate_retrieval(retriever, golden_data):
    results = {"pass": 0, "fail": 0, "details": []}
    
    for test in golden_data:
        result = await retriever.retrieve(
            scenario_context="",
            decision_prompt=test["query"],
        )
        
        # Check if expected sources appear in response
        found_sources = [s for s in test["expected_sources"] 
                        if s.lower() in result["raw_response"].lower()]
        
        passed = len(found_sources) >= len(test["expected_sources"]) * 0.6
        results["pass" if passed else "fail"] += 1
        results["details"].append({
            "query": test["query"],
            "passed": passed,
            "found": found_sources,
            "expected": test["expected_sources"],
        })
    
    accuracy = results["pass"] / len(golden_data) * 100
    print(f"Retrieval accuracy: {accuracy:.1f}% ({results['pass']}/{len(golden_data)})")
    return results
```

**Target:** ≥80% accuracy on golden dataset before deploying Whisperer.

---

## 7. Fallback Architecture

If LightRAG graph quality is insufficient, the fallback plan:

| Scenario | Action |
|---|---|
| Graph extraction misses key entities | Supplement with hand-curated entity list (JSON) |
| Gemini rate limits block graph construction | Use local `all-MiniLM-L6-v2` for embeddings, Ollama for entity extraction |
| Graph too large for Render disk | Prune to scenario-relevant subgraphs only |
| Retrieval accuracy < 70% | Fall back to ChromaDB (v2.0) + keyword boost while improving graph |

---

*End of GraphRAG Pipeline Implementation Guide v3.0*
