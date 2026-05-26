# GovernAI Studio — LLM Gateway & Agentic Orchestration
## v3.0 · May 2026 · Cost: ₹0

---

## 1. Multi-Provider LLM Gateway

### 1.1 Provider Registry

```python
# ai/providers.py
PROVIDERS = {
    "gemini": {
        "model": "gemini/gemini-2.0-flash",
        "api_key_env": "GEMINI_API_KEY",
        "rpm": 15, "daily": 1500,
        "strengths": ["roleplay", "reasoning", "long-context"],
        "roles": ["director", "whisperer", "coach"],  # Best for these
    },
    "groq": {
        "model": "groq/llama-3.3-70b-versatile",
        "api_key_env": "GROQ_API_KEY",
        "rpm": 30, "daily": 14400,
        "strengths": ["speed", "chat", "streaming"],
        "roles": ["npc_dialogue"],  # Ultra-fast for chat
    },
    "cerebras": {
        "model": "cerebras/llama-3.3-70b",
        "api_key_env": "CEREBRAS_API_KEY",
        "rpm": 30, "daily": 14400,
        "strengths": ["throughput", "drafting"],
        "roles": ["drafting_partner"],
    },
    "sambanova": {
        "model": "sambanova/Meta-Llama-3.3-70B-Instruct",
        "api_key_env": "SAMBANOVA_API_KEY",
        "rpm": 20, "daily": 10000,
        "strengths": ["general", "fallback"],
        "roles": ["fallback"],
    },
}
```

### 1.2 Smart Router (Role-Based + Failover)

```python
# ai/gateway.py
import asyncio
import time
from collections import defaultdict
import litellm

class LLMGateway:
    def __init__(self):
        self.usage = defaultdict(lambda: {"rpm_count": 0, "daily_count": 0, "rpm_reset": 0})
    
    def _get_provider_for_role(self, role: str) -> list[dict]:
        """Route AI roles to optimal providers."""
        primary = [p for p in PROVIDERS.values() if role in p["roles"]]
        fallbacks = [p for p in PROVIDERS.values() if "fallback" in p["roles"]]
        all_providers = [p for p in PROVIDERS.values()]
        
        # Priority: role-specific → fallback → any available
        return (primary or fallbacks or all_providers)
    
    def _has_budget(self, provider: dict) -> bool:
        usage = self.usage[provider["model"]]
        now = time.time()
        
        # Reset RPM counter every 60 seconds
        if now - usage["rpm_reset"] > 60:
            usage["rpm_count"] = 0
            usage["rpm_reset"] = now
        
        return (usage["rpm_count"] < provider["rpm"] and 
                usage["daily_count"] < provider["daily"])
    
    async def generate(self, system_prompt: str, user_prompt: str,
                       role: str = "general", temperature: float = 0.5,
                       max_tokens: int = 2000, stream: bool = False):
        """Generate with smart routing and auto-failover."""
        providers = self._get_provider_for_role(role)
        
        for provider in providers:
            if not self._has_budget(provider):
                continue
            try:
                response = await litellm.acompletion(
                    model=provider["model"],
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    timeout=30,
                )
                # Track usage
                self.usage[provider["model"]]["rpm_count"] += 1
                self.usage[provider["model"]]["daily_count"] += 1
                return response
            except Exception as e:
                print(f"Provider {provider['model']} failed: {e}")
                continue
        
        raise Exception("All LLM providers exhausted. Retry in 60s.")

# Singleton
gateway = LLMGateway()
```

### 1.3 Capacity After Stacking

| | Gemini Only (v2.0) | Stacked (v3.0) |
|---|---|---|
| **RPM** | 15 | ~95 |
| **Daily requests** | 1,500 | ~40,000 |
| **Concurrent officers** | ~2 | ~15-20 |
| **Redundancy** | None (single point of failure) | 4 providers |

---

## 2. Agentic Orchestration (LangGraph)

### 2.1 Why LangGraph Over Hardcoded State Machine

The v2.0 state machine is linear: Setting → Stakeholders → Decisions → Consequences → Reflection. Real governance scenarios need **dynamic routing** — an NPC reaction might loop back to another stakeholder, the Whisperer might trigger proactively, a drafting stage might require multiple rounds.

LangGraph provides:
- **Stateful graph execution** with checkpointing (resume from any point)
- **Conditional edges** (dynamic routing based on officer actions)
- **Parallel execution** (Whisperer queries while NPC responds)
- **Built-in persistence** (saves to DB, survives Render cold restarts)

### 2.2 Simulation Graph Definition

```python
# orchestration/graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from typing import TypedDict, Annotated, Literal
from operator import add

class SimState(TypedDict):
    session_id: str
    officer_tier: str
    scenario: dict
    stage: str
    npc_exchanges: Annotated[list, add]  # Append-only
    decisions: Annotated[list, add]
    references: Annotated[list, add]
    drafts: list
    consequences: list
    reflection: dict
    npc_required_met: dict  # {npc_id: bool}

# ---- Agent Nodes ----

async def scenario_director(state: SimState) -> SimState:
    """Adapts scenario narrative to officer's tier."""
    prompt = f"""Adapt this scenario setting for a {'policy/HQ' if state['officer_tier'] == 'A' else 'field/district'} officer:
    
{state['scenario']['setting']['narrative']}

Maintain government idiom. Keep it under 300 words. Write in second person ("You are sitting...")."""
    
    response = await gateway.generate(
        system_prompt="You are the Scenario Director for GovernAI Studio.",
        user_prompt=prompt, role="director", temperature=0.4,
    )
    state["stage"] = "SETTING"
    return state

async def npc_dialogue(state: SimState) -> SimState:
    """Handles NPC conversation turn."""
    active_npc = state.get("active_npc")
    npc_config = next(n for n in state["scenario"]["npcs"] if n["id"] == active_npc)
    
    # Build conversation history for this NPC
    npc_history = [e for e in state["npc_exchanges"] if e["npc_id"] == active_npc]
    
    prompt = f"""Previous exchanges: {npc_history[-5:] if npc_history else 'None'}
Officer's latest message: {state.get('officer_message', '')}

Respond in character. Stay under 150 words. Never break character."""
    
    response = await gateway.generate(
        system_prompt=npc_config["system_prompt"],
        user_prompt=prompt, role="npc_dialogue", temperature=0.7,
    )
    
    state["npc_exchanges"] = [{
        "npc_id": active_npc,
        "npc_name": npc_config["name"],
        "officer_msg": state.get("officer_message"),
        "npc_response": response.choices[0].message.content,
    }]
    
    # Track required interactions
    npc_count = len([e for e in state["npc_exchanges"] if e["npc_id"] == active_npc])
    required = npc_config.get("required_interactions", 1)
    state["npc_required_met"][active_npc] = npc_count >= required
    
    return state

async def reference_whisperer(state: SimState) -> SimState:
    """Surfaces relevant legal references via GraphRAG."""
    from retrieval.pipeline import GovernAIRetriever
    retriever = GovernAIRetriever(graph_builder)
    
    current_decision = state["scenario"]["decision_moments"][len(state["decisions"])]
    
    result = await retriever.retrieve(
        scenario_context=state["scenario"]["setting"]["narrative"],
        decision_prompt=current_decision["prompt"],
        whisperer_keywords=current_decision.get("whisperer_keywords", []),
    )
    
    state["references"] = [result]
    return state

async def drafting_partner(state: SimState) -> SimState:
    """Critiques officer's draft from multiple angles."""
    draft = state.get("current_draft", "")
    
    prompt = f"""Critique this government draft from 5 angles:
1. Legal soundness (cite specific sections if applicable)
2. Ethical risk (bias, fairness, consent gaps)
3. Citizen impact (who benefits, who is harmed)
4. Political optics (how media/opposition would frame this)
5. Drafting convention (format, language, GFR compliance)

Draft: {draft}

Be specific. Quote the draft where needed. Suggest concrete improvements."""
    
    response = await gateway.generate(
        system_prompt="You are the Drafting Partner — a sharp legal advisor.",
        user_prompt=prompt, role="drafting_partner", temperature=0.3,
    )
    state["drafts"].append({"draft": draft, "critique": response.choices[0].message.content})
    return state

async def reflection_coach(state: SimState) -> SimState:
    """Generates the Seven Sutras reflective debrief."""
    
    prompt = f"""Generate a reflective debrief for this officer's scenario session.

Scenario: {state['scenario']['title']}
Decisions made: {state['decisions']}
References surfaced: {state['references']}

Structure around the Seven Sutras: Trust, People First, Innovation over Restraint, 
Fairness and Equity, Accountability, Understandable by Design, Safety/Resilience.

CRITICAL RULES:
- NEVER score, rank, grade, or compare
- Use ONLY reflective questions and observations
- Say "How might..." not "You should have..."
- Surface which Sutras were engaged, which were left unaddressed
- Suggest alternative approaches WITHOUT judging
- Include 3-4 further reading recommendations from the corpus"""
    
    response = await gateway.generate(
        system_prompt="You are the Reflection Coach — a wise, non-judgmental mentor.",
        user_prompt=prompt, role="coach", temperature=0.5, max_tokens=3000,
    )
    state["reflection"] = {"content": response.choices[0].message.content}
    state["stage"] = "COMPLETED"
    return state

# ---- Routing Functions ----

def route_after_npc(state: SimState) -> Literal["npc_dialogue", "decision_handler"]:
    all_met = all(state["npc_required_met"].values())
    if all_met and state.get("officer_ready_for_decisions"):
        return "decision_handler"
    return "npc_dialogue"

def route_after_decision(state: SimState) -> Literal["reference_whisperer", "drafting_partner", "consequence_engine", "decision_handler"]:
    decisions_total = len(state["scenario"]["decision_moments"])
    decisions_made = len(state["decisions"])
    
    if decisions_made >= decisions_total:
        return "consequence_engine"
    
    next_decision = state["scenario"]["decision_moments"][decisions_made]
    if next_decision.get("requires_draft"):
        return "drafting_partner"
    return "reference_whisperer"  # Always surface references before next decision

# ---- Build Graph ----

def build_simulation_graph():
    graph = StateGraph(SimState)
    
    graph.add_node("scenario_director", scenario_director)
    graph.add_node("npc_dialogue", npc_dialogue)
    graph.add_node("reference_whisperer", reference_whisperer)
    graph.add_node("decision_handler", lambda s: s)  # Waits for officer input
    graph.add_node("drafting_partner", drafting_partner)
    graph.add_node("consequence_engine", lambda s: s)  # Renders consequences
    graph.add_node("reflection_coach", reflection_coach)
    
    graph.set_entry_point("scenario_director")
    graph.add_edge("scenario_director", "npc_dialogue")
    graph.add_conditional_edges("npc_dialogue", route_after_npc)
    graph.add_edge("reference_whisperer", "decision_handler")
    graph.add_conditional_edges("decision_handler", route_after_decision)
    graph.add_edge("drafting_partner", "decision_handler")
    graph.add_edge("consequence_engine", "reflection_coach")
    graph.add_edge("reflection_coach", END)
    
    # Persistence: checkpoint to Neon PostgreSQL
    checkpointer = PostgresSaver.from_conn_string(os.environ["DATABASE_URL"])
    return graph.compile(checkpointer=checkpointer)
```

### 2.3 FastAPI Integration

```python
# api/routes/simulation.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/v1/sessions")
sim_graph = build_simulation_graph()

@router.post("/start")
async def start_session(scenario_id: str, user = Depends(get_current_user)):
    scenario = await load_scenario(scenario_id)
    config = {"configurable": {"thread_id": f"session-{user.id}-{scenario_id}"}}
    
    initial_state = SimState(
        session_id=str(uuid4()), officer_tier=user.tier,
        scenario=scenario, stage="NOT_STARTED",
        npc_exchanges=[], decisions=[], references=[],
        drafts=[], consequences=[], reflection={},
        npc_required_met={npc["id"]: False for npc in scenario["npcs"]},
    )
    
    result = await sim_graph.ainvoke(initial_state, config)
    return {"session_id": result["session_id"], "stage": result["stage"]}

@router.post("/{session_id}/interact")
async def npc_interact(session_id: str, npc_id: str, message: str):
    config = {"configurable": {"thread_id": session_id}}
    
    result = await sim_graph.ainvoke(
        {"active_npc": npc_id, "officer_message": message}, config
    )
    return {"response": result["npc_exchanges"][-1]["npc_response"]}

@router.post("/{session_id}/decision")
async def submit_decision(session_id: str, decision_moment_id: str, 
                          choice: str, free_text: str = None):
    config = {"configurable": {"thread_id": session_id}}
    
    result = await sim_graph.ainvoke(
        {"decisions": [{"moment_id": decision_moment_id, "choice": choice, 
                        "free_text": free_text}],
         "officer_ready_for_decisions": True}, config
    )
    return {"stage": result["stage"], "next": "consequences" if result["stage"] == "CONSEQUENCES" else "decision"}
```

---

## 3. Custom Training Pipeline

### 3.1 Training Data Generation

```python
# training/generate_data.py
"""Generate synthetic training data using the free LLM gateway."""

async def generate_npc_training_data(npc_archetype: str, num_conversations: int = 200):
    """Generate multi-turn NPC conversations for LoRA training."""
    
    archetypes = {
        "vendor": "persuasive tech vendor selling AI solutions to government",
        "journalist": "investigative journalist asking tough questions about AI procurement",
        "citizen": "concerned citizen challenging algorithmic decisions",
        "colleague": "cautious deputy secretary flagging governance risks",
        "minister": "impatient minister demanding quick decisions on AI policy",
    }
    
    prompt = f"""Generate a realistic 6-turn government dialogue.
    
NPC role: {archetypes[npc_archetype]}
Setting: Indian government office, AI governance context
Format: JSON with "conversations" array of {{role, content}} objects

Rules:
- NPC NEVER breaks character
- NPC has specific personality traits and pressure tactics
- Officer responses should be realistic civil service language
- Include references to actual Indian governance frameworks"""
    
    conversations = []
    for i in range(num_conversations):
        response = await gateway.generate(
            system_prompt="Generate training data for AI characters.",
            user_prompt=prompt, role="general", temperature=0.8,
        )
        conversations.append(response.choices[0].message.content)
        if i % 20 == 0:
            print(f"Generated {i}/{num_conversations} conversations")
            await asyncio.sleep(5)  # Rate limit pause
    
    return conversations

async def generate_coach_training_data(num_sessions: int = 100):
    """Generate reflection transcripts that follow strict non-evaluative rules."""
    
    prompt = """Generate a Reflection Coach debrief for an AI governance scenario.

STRICT RULES (these define the Coach's character):
- NEVER use: "score", "grade", "correct", "wrong", "should have", "failed", "well done"
- ONLY use: reflective questions, observations, alternative framings
- Structure around 3-4 of the Seven Sutras
- End with 2-3 further reading suggestions
- Tone: wise mentor, not examiner

Format: JSON with preamble, sutra_observations (array), alternative_approaches, further_reading"""
    
    return await _batch_generate(prompt, num_sessions)
```

### 3.2 LoRA Training (Kaggle Notebook)

```python
# training/train_lora.py — Run on Kaggle (free T4 GPU)
from unsloth import FastLanguageModel
from trl import SFTTrainer
from datasets import load_dataset

# Load base model (4-bit quantized)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3.3-8b-instruct-bnb-4bit",
    max_seq_length=4096,
    load_in_4bit=True,
)

# Apply LoRA
model = FastLanguageModel.get_peft_model(
    model, r=32, lora_alpha=64,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05, bias="none",
)

# Load training data
dataset = load_dataset("json", data_files="npc_training_data.jsonl")

# Train
trainer = SFTTrainer(
    model=model, tokenizer=tokenizer,
    train_dataset=dataset["train"],
    dataset_text_field="text",
    max_seq_length=4096,
    args=dict(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        num_train_epochs=3,
        learning_rate=2e-4,
        output_dir="./governai-npc-lora",
        logging_steps=10,
    ),
)

trainer.train()

# Save & push to HuggingFace (free)
model.save_pretrained("./governai-npc-lora")
model.push_to_hub("governai/npc-character-lora")
```

### 3.3 Training Schedule (All Free)

| Model | Platform | GPU | Time | Data | Week |
|---|---|---|---|---|---|
| GovernAI-Embed | Kaggle | T4 | ~4 hrs | 10K pairs | 2-3 |
| GovernAI-Rerank | Kaggle | T4 | ~2 hrs | 5K triplets | 3-4 |
| GovernAI-NPC-LoRA | Kaggle | T4 | ~5 hrs | 1K conversations | 4-6 |
| GovernAI-Coach-LoRA | Kaggle | T4 | ~3 hrs | 300 reflections | 5-6 |

---

## 4. Backend Project Structure

```
governai-backend/
├── app/
│   ├── main.py                     # FastAPI app
│   ├── config.py                   # Env vars, settings
│   ├── ai/
│   │   ├── providers.py            # Provider registry
│   │   ├── gateway.py              # LLM Gateway (multi-provider)
│   │   └── rate_limiter.py         # Token bucket per provider
│   ├── auth/
│   │   ├── magic_link.py           # Resend integration
│   │   └── jwt.py                  # JWT creation/validation
│   ├── corpus/
│   │   ├── ingest.py               # PDF → chunks pipeline
│   │   └── graph_builder.py        # LightRAG graph construction
│   ├── retrieval/
│   │   ├── query_router.py         # Complexity classifier
│   │   └── pipeline.py             # Full retrieval pipeline
│   ├── orchestration/
│   │   └── graph.py                # LangGraph simulation engine
│   ├── api/routes/
│   │   ├── auth.py
│   │   ├── onboarding.py
│   │   ├── scenarios.py
│   │   ├── simulation.py           # Start, interact, decide
│   │   └── whisperer.py            # Reference endpoint
│   ├── db/
│   │   ├── database.py             # Neon async connection
│   │   ├── models.py               # SQLAlchemy ORM
│   │   └── migrations/             # Alembic
│   └── privacy/
│       └── middleware.py           # PII stripping
├── corpus/
│   ├── raw/                        # Source PDFs
│   └── processed/                  # Cleaned text files
├── graph_data/                     # LightRAG persistent storage
├── evaluation/
│   ├── golden_dataset.py           # 50 test queries
│   └── run_eval.py                 # Evaluation script
├── training/
│   ├── generate_data.py            # Synthetic data generation
│   └── train_lora.py               # Kaggle notebook script
├── scripts/
│   ├── build_graph.py              # One-time graph construction
│   └── seed_scenarios.py           # Seed DB with scenario JSONs
├── requirements.txt
├── Dockerfile
└── render.yaml
```

---

## 5. Implementation Order (Week by Week)

| Week | What to Build | Depends On | Deliverable |
|---|---|---|---|
| **1** | Project scaffolding, Neon DB, Gemini API key, all free accounts | Nothing | Skeleton deploys to Render |
| **2** | Corpus ingestion pipeline (PDF → chunks) | Raw PDFs collected | 9K chunks ready |
| **3** | LightRAG graph construction (run overnight) | Chunks + Gemini key | Knowledge graph built |
| **3** | LLM Gateway + LiteLLM (all 4 providers) | API keys | Multi-provider routing works |
| **4** | Retrieval pipeline + query router | Graph built | Whisperer answers queries |
| **4** | Golden dataset + evaluation | Retrieval pipeline | ≥80% accuracy confirmed |
| **5** | LangGraph orchestration engine | Gateway + Retrieval | Full simulation loop runs |
| **5** | Auth (magic link + JWT) | Resend account | Officers can log in |
| **6** | Training data generation (NPC + Coach) | Gateway working | Training datasets ready |
| **6** | LoRA training on Kaggle | Training data | Adapters on HuggingFace |
| **7** | Integration testing (all components) | Everything above | End-to-end scenario works |
| **8** | Deploy to Render, Neon, seed scenarios | All tested | Backend live at ₹0/month |

---

*End of LLM Gateway & Orchestration Implementation v3.0*
