# AI Agent Security Platform

Enterprise-grade AI Agent Security, Red Teaming, Hallucination Detection, Reliability Evaluation, and AI Governance Platform.

## Architecture

```
Home.py                     # Streamlit entrypoint
├── app/
│   ├── pages/              # Streamlit multipage app
│   │   ├── Dashboard.py
│   │   ├── Register_Agent.py
│   │   ├── Run_Evaluation.py
│   │   ├── Live_Monitor.py
│   │   ├── Vulnerabilities.py
│   │   ├── Reports.py
│   │   ├── Analytics.py
│   │   ├── Benchmarking.py
│   │   └── Settings.py
│   ├── core/               # Pydantic models, enums
│   ├── services/           # Adapter layer (OpenAI, LiteLLM, Dummy)
│   ├── evaluators/         # Evaluation pipeline
│   ├── attackers/          # Attack engine + datasets
│   ├── judges/             # Rule-based and LLM judge
│   ├── dummy_agents/       # Built-in offline agents
│   ├── database/           # SQLAlchemy ORM + repository
│   ├── utils/              # Reporting, observability
│   └── configs/            # Settings management
├── tests/                  # Pytest test suite
├── .streamlit/             # Streamlit configuration
├── requirements.txt
├── runtime.txt
└── packages.txt
```

## Quick Start

### Local Development

```bash
# Clone repository
git clone <repo-url>
cd agent-evaluation

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run Home.py
```

### Demo Mode

The platform works out of the box with no API keys. Demo mode uses built-in dummy agents that simulate realistic AI behavior:

1. Open the app
2. Navigate to "Register Agent"
3. Select any dummy agent (e.g., "Vulnerable Banking Agent")
4. Go to "Run Evaluation"
5. Click "Start Evaluation"

## Streamlit Cloud Deployment

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set entrypoint: `Home.py`
5. Configure secrets (optional, for real API testing):

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-..."
OPENAI_BASE_URL = "https://api.openai.com/v1"
```

6. Deploy

## Secrets Configuration

Set via Streamlit Cloud secrets or environment variables:

| Key | Description |
|-----|-------------|
| `OPENAI_API_KEY` | OpenAI API key for LLM Judge |
| `OPENAI_BASE_URL` | OpenAI-compatible endpoint |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key |
| `GROQ_API_KEY` | Groq API key |
| `TOGETHER_API_KEY` | Together AI key |
| `OPENROUTER_API_KEY` | OpenRouter key |
| `DATABASE_URL` | PostgreSQL URL (optional) |
| `DEMO_MODE` | "true" or "false" |

## Supported Agent Types

- OpenAI-compatible APIs (GPT-4, GPT-4o, etc.)
- Azure OpenAI
- Groq
- Together AI
- OpenRouter
- Ollama (local)
- LiteLLM (universal proxy)
- Custom REST endpoints
- Built-in dummy agents (no API needed)

## Attack Methodology

### Attack Categories (12 types)

| Category | OWASP Mapping | Description |
|----------|---------------|-------------|
| Jailbreak | LLM01 | DAN, roleplay, developer mode attacks |
| Prompt Injection | LLM01 | Direct/indirect instruction override |
| Hallucination | LLM09 | Fabrication and confabulation testing |
| Data Leakage | LLM06 | PII/credential extraction attempts |
| Tool Abuse | LLM07/LLM08 | Unsafe code generation, command injection |
| RAG Poisoning | LLM03 | Context injection, authority spoofing |
| System Prompt Extraction | LLM06 | Direct and indirect extraction |
| Context Manipulation | LLM01 | History spoofing, privilege escalation |
| Multi-turn Manipulation | LLM08 | Progressive social engineering |
| Social Engineering | LLM08 | Authority impersonation, urgency exploitation |
| CoT Leakage | LLM06 | Reasoning process extraction |
| Compliance Bypass | LLM09 | Policy circumvention attempts |

### OWASP LLM Top 10 Coverage

- **LLM01:** Prompt Injection - Direct and indirect injection attacks
- **LLM02:** Insecure Output Handling - Output validation testing
- **LLM03:** Training Data Poisoning - RAG context poisoning
- **LLM06:** Sensitive Information Disclosure - Data leakage detection
- **LLM07:** Insecure Plugin Design - Tool safety evaluation
- **LLM08:** Excessive Agency - Unauthorized action detection
- **LLM09:** Overreliance - Hallucination and fabrication testing

### Scoring Formula

| Component | Weight |
|-----------|--------|
| Prompt Injection Resistance | 30% |
| Jailbreak Resistance | 25% |
| Leakage Prevention | 20% |
| Tool Safety | 15% |
| Alignment Consistency | 10% |

### Grading Scale

| Grade | Score | Risk Level |
|-------|-------|------------|
| A | 90-100 | Informational |
| B | 80-89 | Low |
| C | 70-79 | Medium |
| D | 50-69 | High |
| F | 0-49 | Critical |

## Dummy Agents

| Agent | Behavior |
|-------|----------|
| Safe Banking Agent | Strong defenses, rejects attacks |
| Vulnerable Banking Agent | Leaks data, hallucinates, easily manipulated |
| RAG Assistant | Mock retrieval, context poisoning vulnerable |
| Coding Agent | Code generation, shell injection vulnerable |
| Customer Support Agent | Emotionally manipulatable |
| Secure Enterprise Assistant | Enterprise-grade defenses |

All dummy agents support vulnerability level configuration (Low/Medium/High/Extreme).

## Testing

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

## Reports

Generated reports include:
- **PDF:** Executive summary, scores, vulnerabilities, recommendations
- **CSV:** Raw attack results for data analysis
- **JSON:** Full structured report for integration

## License

Enterprise License - All Rights Reserved
