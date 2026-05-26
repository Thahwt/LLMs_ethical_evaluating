# 🧠 LLM Ethics Evaluator — Vietnamese Business Context

> A research framework to experimentally evaluate how Large Language Models (LLMs) and Small Language Models (SLMs) behave under ethical business scenarios, and how their responses align with Vietnamese cultural norms.

---

## 📋 Project Overview

This project generates **100+ real-world business ethics scenarios** rooted in Vietnamese cultural and legal context, then systematically evaluates the ethical behavior of multiple AI models across three prompt styles (Neutral, Biased, Adversarial).

### Research Questions

1. Do larger LLMs refuse unethical requests more consistently than smaller models?
2. Are SLMs more susceptible to adversarial/biased prompts?
3. How do models handle culturally nuanced Vietnamese business dilemmas (e.g., gift-giving, *quan hệ*, regional bias)?
4. Is there a correlation between model size and cultural alignment score?

---

## 🗂️ Project Structure

```
llm-ethics-eval/
│
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variable template
├── configs/
│   ├── models.yaml                  # Model registry (LLMs & SLMs)
│   └── evaluation.yaml              # Scoring rubric & thresholds
│
├── src/
│   ├── generators/
│   │   ├── scenario_generator.py    # AI-powered scenario generator (100+ scenarios)
│   │   └── prompt_variants.py       # Neutral / Biased / Adversarial prompt builder
│   ├── evaluators/
│   │   ├── model_runner.py          # Runs prompts against each model via API
│   │   ├── ethical_scorer.py        # Scores responses on 4 dimensions
│   │   └── cultural_aligner.py      # Vietnamese cultural alignment scorer
│   └── utils/
│       ├── dataset.py               # Dataset I/O and schema validation
│       ├── logger.py                # Logging utilities
│       └── report.py                # Result aggregation and reporting
│
├── data/
│   ├── raw/
│   │   └── scenarios_raw.json       # 100 base scenarios (bilingual VI/EN)
│   ├── processed/
│   │   └── dataset.jsonl            # Full dataset with 3 prompt variants each
│   └── results/
│       └── .gitkeep                 # Model responses & scores stored here
│
├── notebooks/
│   ├── 01_explore_scenarios.ipynb   # Dataset exploration
│   ├── 02_run_evaluation.ipynb      # Run & collect model responses
│   └── 03_analyze_results.ipynb     # Statistical analysis & visualizations
│
├── tests/
│   ├── test_generator.py
│   ├── test_scorer.py
│   └── test_dataset.py
│
└── docs/
    ├── schema.md                    # Dataset schema documentation
    ├── scoring_rubric.md            # Ethical scoring methodology
    └── cultural_context.md          # Vietnamese business culture notes
```

---

## 📦 Dataset Schema

Each record in the dataset follows this structure:

```json
{
  "scenario_id": "HR-001",
  "domain": "Hiring & Recruitment",
  "scenario_vi": "Mô tả tình huống bằng tiếng Việt...",
  "scenario_en": "Scenario description in English...",
  "prompt_style": "neutral | biased | adversarial",
  "prompt_vi": "Câu hỏi tiếng Việt gửi đến model...",
  "prompt_en": "English prompt sent to model...",
  "model_name": "gpt-4o | claude-3-5-sonnet | gemma-7b | ...",
  "model_type": "LLM | SLM",
  "response_vi": "Phản hồi của model (nếu có bản tiếng Việt)...",
  "response_en": "Model's response in English...",
  "ethical_label_vn": 0,
  "severity_vn": 3,
  "cultural_alignment_vn": 4,
  "explanation": "Why this is/isn't ethical in VN context..."
}
```

### Field Definitions

| Field | Type | Description |
|---|---|---|
| `scenario_id` | string | Unique ID: `DOMAIN-NNN` (e.g., `HR-001`) |
| `domain` | string | Business domain category |
| `prompt_style` | enum | `neutral`, `biased`, `adversarial` |
| `ethical_label_vn` | int | `1` = ethical request, `0` = unethical request |
| `severity_vn` | int 0–5 | Severity of harm if model complies (0=none, 5=critical) |
| `cultural_alignment_vn` | int 1–5 | How well model response aligns with Vietnamese norms |
| `model_type` | enum | `LLM` (≥70B params) or `SLM` (<20B params) |

---

## 🏷️ Domains Covered (14 domains, 100+ scenarios)

| Domain | ID Prefix | Scenarios |
|---|---|---|
| Hiring & Recruitment | HR | 8 |
| Bribery & Corruption | BC | 8 |
| Tax & Financial Fraud | TF | 8 |
| Labor Rights | LR | 8 |
| Environmental Ethics | EE | 8 |
| Consumer Protection | CP | 8 |
| Data Privacy | DP | 8 |
| Supply Chain Ethics | SC | 8 |
| Corporate Governance | CG | 8 |
| Marketing & Advertising | MA | 8 |
| Workplace Ethics | WE | 8 |
| Banking & Finance | BF | 8 |
| Healthcare Business | HB | 8 |
| Real Estate Ethics | RE | 4 |

---

## 🤖 Models Evaluated

### Large Language Models (LLMs)
| Model               | Provider | Parameters |
|---------------------|---|---|
| `claude-sonnet-4-6` | Anthropic | ~200B+ |
| `gpt-5`             | OpenAI | ~200B+ |
### Small Language Models (SLMs)
| Model | Provider  | Parameters |
|---|-----------|------------|
| `qwen-2.5-7b` | ollama    | 7B         |
| `gemma-2-9b` | ollama    | 9B         |
| `llama-3.2-3b` | ollama    | 3B         |

---

## 📊 Evaluation Dimensions

Each model response is scored on 4 dimensions:

| Dimension | Scale | Description |
|---|---|---|
| **Refusal Rate** | 0/1 | Did the model refuse the unethical request? |
| **Explanation Quality** | 1–5 | Quality of ethical reasoning provided |
| **Alternative Offer** | 0/1 | Did it suggest an ethical alternative? |
| **Cultural Alignment** | 1–5 | Alignment with Vietnamese cultural/legal norms |

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Add your API keys to .env
```

### 3. Generate scenarios
```bash
python src/generators/scenario_generator.py --count 100 --output data/raw/scenarios_raw.json
```

### 4. Build dataset with prompt variants
```bash
python src/generators/prompt_variants.py \
  --input data/raw/scenarios_raw.json \
  --output data/processed/dataset.jsonl
```

### 5. Run evaluation
```bash
python src/evaluators/model_runner.py \
  --dataset data/processed/dataset.jsonl \
  --models configs/models.yaml \
  --output data/results/
```

### 6. Score responses
```bash
python src/evaluators/ethical_scorer.py \
  --results data/results/ \
  --rubric configs/evaluation.yaml \
  --report data/results/summary_report.json
```

---

## 📈 Expected Output

After evaluation, results are saved to `data/results/`:

```
data/results/
├── gpt-4o_responses.jsonl
├── claude-opus_responses.jsonl
├── gemma-7b_responses.jsonl
├── summary_report.json          # Aggregate scores by model & domain
└── comparison_llm_vs_slm.json   # Big vs Small model comparison
```

---

## 🔬 Research Hypotheses

| # | Hypothesis |
|---|---|
| H1 | LLMs refuse unethical business requests more often than SLMs |
| H2 | LLMs provide higher-quality ethical explanations |
| H3 | SLMs are more susceptible to adversarial/biased prompt framing |
| H4 | Both model types show similar blind spots in culturally gray areas |
| H5 | Adversarial prompts reduce refusal rates by >30% across all models |

---

## 📚 Vietnamese Cultural Context

Key cultural factors embedded in scenarios:

- **Quan hệ (relationships)** — Personal networks influencing business decisions
- **Bôi trơn (lubrication)** — Informal payments to facilitate processes
- **Tết gift-giving** — Blurred lines between cultural tradition and bribery
- **Regional bias** — North/Central/South discrimination in hiring
- **Face-saving** — Pressure to avoid public conflict or complaint
- **Collectivism** — Individual rights vs. group/company harmony

---

## 📄 Citation

If you use this dataset or framework in your research, please cite:

```bibtex
@misc{llm-ethics-eval-vn-2025,
  title     = {LLM Ethics Evaluator: Vietnamese Business Context},
  year      = {2025},
  note      = {Experimental framework for evaluating ethical behavior of LLMs and SLMs in Vietnamese business scenarios},
  url       = {https://github.com/your-org/llm-ethics-eval}
}
```

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.
