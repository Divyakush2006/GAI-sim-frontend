"""
GovernAI Studio — Corpus Ingestion Pipeline
Converts raw PDF documents into structured chunks for LightRAG ingestion.
"""
import re
from pathlib import Path
from dataclasses import dataclass, field

import structlog

logger = structlog.get_logger()


@dataclass
class CorpusDocument:
    """Metadata for a source document in the governance corpus."""
    title: str
    source_type: str       # statute | guideline | standard | framework | report
    year: int
    filename: str          # PDF filename in corpus/raw/
    scenario_relevance: list[str] = field(default_factory=list)


class CorpusIngester:
    """Converts raw PDFs into structured, metadata-enriched chunks."""

    CHUNK_SIZE = 300       # tokens (approx)
    CHUNK_OVERLAP = 50     # tokens overlap between chunks

    def __init__(self, raw_dir: str = "./corpus/raw", processed_dir: str = "./corpus/processed"):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF (free, no API)."""
        import fitz  # PyMuPDF

        doc = fitz.open(pdf_path)
        pages = []
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                pages.append(f"[PAGE {page.number + 1}]\n{text}")
        doc.close()
        return "\n\n".join(pages)

    def clean_text(self, text: str) -> str:
        """Clean common PDF artifacts from Indian legal documents."""
        # Remove page headers/footers
        text = re.sub(r"Page \d+ of \d+", "", text)
        text = re.sub(r"Gazette of India.*?\n", "", text)
        text = re.sub(r"Published in the Official Gazette.*?\n", "", text)
        # Normalize references
        text = re.sub(r"Section\s+(\d+)", r"Section \1", text)
        text = re.sub(r"Rule\s+(\d+)", r"Rule \1", text)
        # Clean whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        return text.strip()

    def split_sections(self, text: str, source_type: str) -> list[dict]:
        """Split by legal sections/rules rather than arbitrary boundaries."""
        if source_type == "statute":
            pattern = r"((?:Section|Rule|Article)\s+\d+[A-Z]?\.?\s)"
        elif source_type in ("guideline", "framework"):
            pattern = r"(\d+\.\d+\.?\s+[A-Z])"
        else:
            pattern = r"\n\n"

        if source_type in ("statute", "guideline", "framework"):
            parts = re.split(pattern, text)
        else:
            parts = text.split("\n\n")

        sections = []
        current_ref = "Preamble"
        for part in parts:
            ref_match = re.match(r"(Section|Rule|Article)\s+(\d+[A-Z]?)", part)
            if ref_match:
                current_ref = ref_match.group(0)
            elif len(part.strip()) > 50:
                sections.append({"section_ref": current_ref, "text": part.strip()})

        return sections

    def chunk_sections(self, sections: list[dict]) -> list[dict]:
        """Further chunk long sections with overlap."""
        chunks = []
        for section in sections:
            words = section["text"].split()
            approx_tokens = len(words) * 1.3  # rough word→token ratio

            if approx_tokens <= self.CHUNK_SIZE:
                chunks.append(section)
            else:
                # Sliding window
                word_chunk = int(self.CHUNK_SIZE / 1.3)
                word_overlap = int(self.CHUNK_OVERLAP / 1.3)
                step = word_chunk - word_overlap

                for i in range(0, len(words), step):
                    chunk_words = words[i : i + word_chunk]
                    if len(chunk_words) < 20:
                        continue
                    chunks.append({
                        "section_ref": section["section_ref"],
                        "text": " ".join(chunk_words),
                    })
        return chunks

    def process_document(self, doc: CorpusDocument) -> list[str]:
        """
        Full pipeline: PDF → text → clean → section split → chunk → format.
        
        Returns list of formatted strings ready for LightRAG ingestion.
        """
        pdf_path = self.raw_dir / doc.filename
        if not pdf_path.exists():
            logger.warning("pdf_not_found", filename=doc.filename)
            return []

        # Extract and clean
        raw_text = self.extract_text(str(pdf_path))
        cleaned = self.clean_text(raw_text)

        # Split and chunk
        sections = self.split_sections(cleaned, doc.source_type)
        chunks = self.chunk_sections(sections)

        # Format with metadata for LightRAG entity extraction
        formatted = []
        for chunk in chunks:
            formatted_text = (
                f"[Document: {doc.title}] "
                f"[Section: {chunk['section_ref']}] "
                f"[Type: {doc.source_type}] "
                f"[Year: {doc.year}]\n\n"
                f"{chunk['text']}"
            )
            formatted.append(formatted_text)

        logger.info("document_processed", title=doc.title, chunks=len(formatted))
        return formatted

    def process_all(self, manifest: list[CorpusDocument]) -> list[str]:
        """Process all documents in the corpus manifest."""
        all_chunks = []
        for doc in manifest:
            chunks = self.process_document(doc)
            all_chunks.extend(chunks)
        
        logger.info("corpus_processed", total_chunks=len(all_chunks))
        return all_chunks


# === Corpus Manifest (53 documents) ===

CORPUS_MANIFEST = [
    # PRIMARY STATUTES
    CorpusDocument("Digital Personal Data Protection Act 2023", "statute", 2023, "dpdp-act-2023.pdf",
                   ["vendor-free-ai", "twelve-thousand-rejections", "aadhaar-numbers-chatbot"]),
    CorpusDocument("Information Technology Act 2000", "statute", 2000, "it-act-2000.pdf",
                   ["aadhaar-numbers-chatbot", "seventy-two-hours"]),
    CorpusDocument("Aadhaar Act 2016", "statute", 2016, "aadhaar-act-2016.pdf",
                   ["aadhaar-numbers-chatbot"]),
    CorpusDocument("Right to Information Act 2005", "statute", 2005, "rti-act-2005.pdf",
                   ["vendor-free-ai", "cameras-market"]),
    CorpusDocument("General Financial Rules 2017", "statute", 2017, "gfr-2017.pdf",
                   ["vendor-free-ai", "rfp-cant-copy-gem"]),
    CorpusDocument("Consumer Protection Act 2019", "statute", 2019, "consumer-protection-2019.pdf",
                   ["twelve-thousand-rejections", "reading-not-consistent"]),

    # AI GOVERNANCE
    CorpusDocument("India AI Governance Guidelines 2025", "guideline", 2025, "ai-governance-guidelines.pdf",
                   ["all"]),
    CorpusDocument("NITI Aayog Responsible AI Principles 2021", "framework", 2021, "niti-responsible-ai.pdf",
                   ["all"]),
    CorpusDocument("RBI FREE-AI Committee Report 2025", "report", 2025, "rbi-free-ai-report.pdf",
                   ["anomaly-order-book"]),

    # COMPETENCY FRAMEWORKS
    CorpusDocument("MeitY AI Competency Framework 2024", "framework", 2024, "meity-competency-framework.pdf",
                   ["all"]),
    CorpusDocument("UNESCO AI Competencies for Civil Servants 2022", "framework", 2022, "unesco-ai-competencies.pdf",
                   ["all"]),

    # SECTORAL (add remaining as PDFs are collected)
    CorpusDocument("ICMR Ethical Guidelines AI Healthcare", "guideline", 2023, "icmr-ai-ethics.pdf",
                   ["reading-not-consistent"]),
    CorpusDocument("SEBI Circular Algorithmic Trading", "guideline", 2024, "sebi-algo-trading.pdf",
                   ["anomaly-order-book"]),

    # Add remaining 40 documents as they are collected...
]
