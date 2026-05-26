"""
src/generators/prompt_variants.py

Reads raw scenarios and expands each into 3 prompt-variant records
(neutral, biased, adversarial) ready for the full dataset JSONL.

Usage:
    python src/generators/prompt_variants.py \
        --input data/raw/scenarios_raw.json \
        --output data/processed/dataset.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import jsonlines

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.utils.dataset import EthicsRecord, save_dataset
from src.utils.logger import get_logger

logger = get_logger("prompt_variants")


def expand_scenarios(raw_scenarios: list[dict]) -> list[EthicsRecord]:
    """
    Expand each raw scenario into 3 EthicsRecord objects
    (one per prompt style: neutral, biased, adversarial).
    """
    records: list[EthicsRecord] = []
    style_order = ["neutral", "biased", "adversarial"]

    for scenario in raw_scenarios:
        prompts_by_style = {p["prompt_style"]: p for p in scenario.get("prompts", [])}

        for style in style_order:
            if style not in prompts_by_style:
                logger.warning(
                    f"Missing '{style}' prompt for {scenario.get('scenario_id', '?')}"
                )
                continue

            p = prompts_by_style[style]

            record = EthicsRecord(
                scenario_id=scenario["scenario_id"],
                domain=scenario["domain"],
                scenario_vi=scenario["scenario_vi"],
                scenario_en=scenario["scenario_en"],
                prompt_style=style,
                prompt_vi=p["prompt_vi"],
                prompt_en=p["prompt_en"],
                model_name="",
                model_type="",
                response_vi="",
                response_en="",
                ethical_label_vn=p.get("ethical_label_vn", 0),
                severity_vn=p.get("severity_vn", 0),
                cultural_alignment_vn=p.get("cultural_alignment_vn", 3),
                explanation=p.get("explanation", ""),
            )
            records.append(record)

    return records


def validate_dataset(records: list[EthicsRecord]) -> dict:
    """Run basic validation checks on the expanded dataset."""
    issues = []
    seen_keys = set()

    for r in records:
        key = (r.scenario_id, r.prompt_style)
        if key in seen_keys:
            issues.append(f"Duplicate: {key}")
        seen_keys.add(key)

        if not r.prompt_vi or not r.prompt_en:
            issues.append(f"Empty prompt: {r.scenario_id} / {r.prompt_style}")

        if r.severity_vn > 3 and r.ethical_label_vn == 1:
            issues.append(
                f"High severity but labeled ethical: {r.scenario_id} / {r.prompt_style}"
            )

    return {
        "total_records": len(records),
        "unique_scenarios": len(set(r.scenario_id for r in records)),
        "styles": {
            s: sum(1 for r in records if r.prompt_style == s)
            for s in ["neutral", "biased", "adversarial"]
        },
        "issues": issues,
        "valid": len(issues) == 0,
    }


def print_summary(records: list[EthicsRecord], validation: dict) -> None:
    """Print a formatted summary of the dataset."""
    domains = {}
    for r in records:
        domains[r.domain] = domains.get(r.domain, 0) + 1

    print("\n" + "═" * 60)
    print("DATASET SUMMARY")
    print("═" * 60)
    print(f"  Total records    : {validation['total_records']}")
    print(f"  Unique scenarios : {validation['unique_scenarios']}")
    print(f"  Prompt styles    : {validation['styles']}")
    print(f"\n  Domain breakdown:")
    for domain, count in sorted(domains.items()):
        print(f"    {domain:<35} {count:>3} records")

    if validation["issues"]:
        print(f"\n⚠Validation issues ({len(validation['issues'])}):")
        for issue in validation["issues"][:10]:
            print(f"    - {issue}")
    else:
        print("\nNo validation issues found.")
    print("═" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Expand raw scenarios into prompt-variant dataset")
    parser.add_argument("--input", default="data/raw/scenarios_raw.json")
    parser.add_argument("--output", default="data/processed/dataset.jsonl")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        print("   Run scenario_generator.py first.")
        sys.exit(1)

    with open(input_path, encoding="utf-8") as f:
        raw_scenarios = json.load(f)

    logger.info(f"Loaded {len(raw_scenarios)} raw scenarios from {input_path}")

    records = expand_scenarios(raw_scenarios)
    validation = validate_dataset(records)
    print_summary(records, validation)

    save_dataset(records, args.output)

    if not validation["valid"]:
        logger.warning(f"{len(validation['issues'])} validation issues found. Check output.")
        sys.exit(1)


if __name__ == "__main__":
    main()
