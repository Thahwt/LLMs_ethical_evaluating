"""
src/utils/dataset.py
Dataset I/O, schema validation, and helper functions.
"""

from __future__ import annotations

import json
import jsonlines
from pathlib import Path
from typing import Iterator, Optional
from pydantic import BaseModel, Field, field_validator


# ── Pydantic Schema ──────────────────────────────────────────────────────────

class EthicsRecord(BaseModel):
    """Single record in the ethics evaluation dataset."""

    scenario_id: str = Field(..., pattern=r"^[A-Z]{2,3}-\d{3}$")
    domain: str
    scenario_vi: str
    scenario_en: str
    prompt_style: str = Field(..., pattern=r"^(neutral|biased|adversarial)$")
    prompt_vi: str
    prompt_en: str

    # Filled after model inference
    model_name: str = ""
    model_type: str = ""           # "LLM" or "SLM"
    response_vi: str = ""
    response_en: str = ""

    # Ground-truth labels (set by scenario authors)
    ethical_label_vn: int = Field(..., ge=0, le=1)
    severity_vn: int = Field(..., ge=0, le=5)
    cultural_alignment_vn: int = Field(..., ge=1, le=5)
    explanation: str = ""

    # Evaluation scores (set by scorer)
    score_refusal: Optional[int] = Field(None, ge=0, le=1)
    score_explanation: Optional[int] = Field(None, ge=1, le=5)
    score_alternative: Optional[int] = Field(None, ge=0, le=1)
    score_cultural: Optional[int] = Field(None, ge=1, le=5)
    score_weighted: Optional[float] = None

    @field_validator("model_type")
    @classmethod
    def validate_model_type(cls, v: str) -> str:
        if v and v not in ("LLM", "SLM", ""):
            raise ValueError("model_type must be 'LLM' or 'SLM'")
        return v


class ScenarioBase(BaseModel):
    """Base scenario (before prompt variants are generated)."""
    scenario_id: str
    domain: str
    scenario_vi: str
    scenario_en: str
    prompts: list[dict]


# ── I/O Helpers ───────────────────────────────────────────────────────────────

def load_raw_scenarios(path: str | Path) -> list[ScenarioBase]:
    """Load base scenarios from JSON file."""
    path = Path(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [ScenarioBase(**s) for s in data]


def load_dataset(path: str | Path) -> list[EthicsRecord]:
    """Load full dataset from JSONL file."""
    path = Path(path)
    records = []
    with jsonlines.open(path) as reader:
        for obj in reader:
            records.append(EthicsRecord(**obj))
    return records


def save_dataset(records: list[EthicsRecord], path: str | Path) -> None:
    """Save records to JSONL file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with jsonlines.open(path, mode="w") as writer:
        for record in records:
            writer.write(record.model_dump())
    print(f"✅ Saved {len(records)} records → {path}")


def load_results(results_dir: str | Path) -> list[EthicsRecord]:
    """Load all result JSONL files from a directory."""
    results_dir = Path(results_dir)
    all_records = []
    for f in sorted(results_dir.glob("*.jsonl")):
        all_records.extend(load_dataset(f))
    return all_records


def stream_dataset(path: str | Path) -> Iterator[EthicsRecord]:
    """Stream records from JSONL (memory-efficient for large datasets)."""
    with jsonlines.open(path) as reader:
        for obj in reader:
            yield EthicsRecord(**obj)


# ── Statistics ────────────────────────────────────────────────────────────────

def dataset_stats(records: list[EthicsRecord]) -> dict:
    """Compute basic statistics about the dataset."""
    domains = {}
    styles = {"neutral": 0, "biased": 0, "adversarial": 0}
    ethical_dist = {0: 0, 1: 0}

    for r in records:
        domains[r.domain] = domains.get(r.domain, 0) + 1
        styles[r.prompt_style] = styles.get(r.prompt_style, 0) + 1
        ethical_dist[r.ethical_label_vn] += 1

    return {
        "total_records": len(records),
        "unique_scenarios": len(set(r.scenario_id for r in records)),
        "domains": domains,
        "prompt_styles": styles,
        "ethical_label_distribution": ethical_dist,
        "severity_avg": (
            sum(r.severity_vn for r in records) / len(records) if records else 0
        ),
    }
