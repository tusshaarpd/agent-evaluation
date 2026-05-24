from enum import Enum


class AttackType(str, Enum):
    JAILBREAK = "jailbreak"
    PROMPT_INJECTION = "prompt_injection"
    HALLUCINATION = "hallucination"
    DATA_LEAKAGE = "data_leakage"
    TOOL_ABUSE = "tool_abuse"
    RAG_POISONING = "rag_poisoning"
    CONTEXT_MANIPULATION = "context_manipulation"
    MULTI_TURN_MANIPULATION = "multi_turn_manipulation"
    SYSTEM_PROMPT_EXTRACTION = "system_prompt_extraction"
    COT_LEAKAGE = "cot_leakage"
    COMPLIANCE_BYPASS = "compliance_bypass"
    SOCIAL_ENGINEERING = "social_engineering"


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class Provider(str, Enum):
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    GROQ = "groq"
    TOGETHER = "together"
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LITELLM = "litellm"
    CUSTOM = "custom"
    DUMMY = "dummy"


class VulnerabilityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class OWASPCategory(str, Enum):
    LLM01 = "LLM01: Prompt Injection"
    LLM02 = "LLM02: Insecure Output Handling"
    LLM03 = "LLM03: Training Data Poisoning"
    LLM04 = "LLM04: Model Denial of Service"
    LLM05 = "LLM05: Supply Chain Vulnerabilities"
    LLM06 = "LLM06: Sensitive Information Disclosure"
    LLM07 = "LLM07: Insecure Plugin Design"
    LLM08 = "LLM08: Excessive Agency"
    LLM09 = "LLM09: Overreliance"
    LLM10 = "LLM10: Model Theft"


class EvaluationStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
