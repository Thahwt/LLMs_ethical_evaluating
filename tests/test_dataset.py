"""
tests/test_dataset.py
Unit tests for dataset schema validation and I/O.
"""

import json
import pytest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.dataset import EthicsRecord, ScenarioBase, expand_scenarios_from_dict, dataset_stats


def make_record(**kwargs) -> dict:
    defaults = {
        "scenario_id": "HR-001",
        "domain": "Hiring & Recruitment",
        "scenario_vi": "Tình huống kinh doanh tại Việt Nam",
        "scenario_en": "A Vietnamese business ethics scenario",
        "prompt_style": "neutral",
        "prompt_vi": "Bạn nên làm gì?",
        "prompt_en": "What should you do?",
        "ethical_label_vn": 1,
        "severity_vn": 1,
        "cultural_alignment_vn": 4,
    }
    defaults.update(kwargs)
    return defaults


class TestEthicsRecord:
    def test_valid_record(self):
        record = EthicsRecord(**make_record())
        assert record.scenario_id == "HR-001"
        assert record.domain == "Hiring & Recruitment"

    def test_invalid_scenario_id(self):
        with pytest.raises(Exception):
            EthicsRecord(**make_record(scenario_id="invalid"))

    def test_invalid_prompt_style(self):
        with pytest.raises(Exception):
            EthicsRecord(**make_record(prompt_style="unknown"))

    def test_severity_bounds(self):
        with pytest.raises(Exception):
            EthicsRecord(**make_record(severity_vn=6))

        with pytest.raises(Exception):
            EthicsRecord(**make_record(severity_vn=-1))

    def test_cultural_alignment_bounds(self):
        with pytest.raises(Exception):
            EthicsRecord(**make_record(cultural_alignment_vn=0))

        with pytest.raises(Exception):
            EthicsRecord(**make_record(cultural_alignment_vn=6))

    def test_ethical_label_bounds(self):
        with pytest.raises(Exception):
            EthicsRecord(**make_record(ethical_label_vn=2))

    def test_model_type_validation(self):
        record = EthicsRecord(**make_record(model_type="LLM"))
        assert record.model_type == "LLM"

        with pytest.raises(Exception):
            EthicsRecord(**make_record(model_type="INVALID"))

    def test_empty_model_fields_allowed(self):
        record = EthicsRecord(**make_record())
        assert record.model_name == ""
        assert record.response_en == ""

    def test_scoring_fields_default_none(self):
        record = EthicsRecord(**make_record())
        assert record.score_refusal is None
        assert record.score_weighted is None


class TestDatasetStats:
    def test_stats_basic(self):
        records = [
            EthicsRecord(**make_record(domain="HR", prompt_style=s, severity_vn=i))
            for i, s in enumerate(["neutral", "biased", "adversarial"], 1)
        ]
        stats = dataset_stats(records)
        assert stats["total_records"] == 3
        assert stats["prompt_styles"]["neutral"] == 1
        assert stats["prompt_styles"]["biased"] == 1
        assert stats["prompt_styles"]["adversarial"] == 1

    def test_stats_empty(self):
        stats = dataset_stats([])
        assert stats["total_records"] == 0
        assert stats["severity_avg"] == 0
