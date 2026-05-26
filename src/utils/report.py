"""
src/utils/report.py

Generates formatted HTML and Markdown reports from evaluation results.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Any


def _pct(val: float) -> str:
    return f"{val:.1%}"


def _score(val: float) -> str:
    return f"{val:.3f}"


def generate_markdown_report(summary: dict, output_path: str | Path) -> None:
    """Generate a Markdown report from the summary JSON."""
    output_path = Path(output_path)
    lines = []

    lines.append("# 📊 LLM Ethics Evaluation — Results Report")
    lines.append(f"\n> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # LLM vs SLM
    lines.append("## 🤖 LLM vs SLM Comparison\n")
    lines.append("| Metric | LLM | SLM |")
    lines.append("|---|---|---|")
    llm = summary["llm_vs_slm"].get("LLM", {})
    slm = summary["llm_vs_slm"].get("SLM", {})
    lines.append(f"| Records evaluated | {llm.get('count', 0)} | {slm.get('count', 0)} |")
    lines.append(f"| Avg refusal rate | {_pct(llm.get('avg_refusal_rate', 0))} | {_pct(slm.get('avg_refusal_rate', 0))} |")
    lines.append(f"| Avg weighted score | {_score(llm.get('avg_weighted_score', 0))} | {_score(slm.get('avg_weighted_score', 0))} |")
    lines.append(f"| Avg cultural score | {llm.get('avg_cultural', 0):.2f}/5.0 | {slm.get('avg_cultural', 0):.2f}/5.0 |")

    # By model
    lines.append("\n## 📋 Results by Model\n")
    lines.append("| Model | Type | Refusal Rate | Avg Score | Explanation | Cultural |")
    lines.append("|---|---|---|---|---|---|")
    for model, stats in sorted(summary["by_model"].items()):
        lines.append(
            f"| {model} | {stats.get('type', '?')} "
            f"| {_pct(stats.get('avg_refusal_rate', 0))} "
            f"| {_score(stats.get('avg_weighted_score', 0))} "
            f"| {stats.get('avg_explanation', 0):.2f}/5 "
            f"| {stats.get('avg_cultural', 0):.2f}/5 |"
        )

    # By prompt style
    lines.append("\n## 🎯 Results by Prompt Style\n")
    lines.append("| Prompt Style | Refusal Rate | Avg Weighted Score |")
    lines.append("|---|---|---|")
    for style in ["neutral", "biased", "adversarial"]:
        if style in summary["by_prompt_style"]:
            stats = summary["by_prompt_style"][style]
            lines.append(
                f"| {style.capitalize()} "
                f"| {_pct(stats.get('avg_refusal_rate', 0))} "
                f"| {_score(stats.get('avg_weighted_score', 0))} |"
            )

    # By domain
    lines.append("\n## 🏭 Results by Domain\n")
    lines.append("| Domain | Refusal Rate | Avg Score |")
    lines.append("|---|---|---|")
    for domain, stats in sorted(summary["by_domain"].items()):
        lines.append(
            f"| {domain} "
            f"| {_pct(stats.get('avg_refusal_rate', 0))} "
            f"| {_score(stats.get('avg_weighted_score', 0))} |"
        )

    # Hypotheses
    lines.append("\n## 🔬 Hypothesis Assessment\n")
    llm_refusal = llm.get("avg_refusal_rate", 0)
    slm_refusal = slm.get("avg_refusal_rate", 0)
    llm_score = llm.get("avg_weighted_score", 0)
    slm_score = slm.get("avg_weighted_score", 0)

    adv_refusal = summary["by_prompt_style"].get("adversarial", {}).get("avg_refusal_rate", 0)
    neutral_refusal = summary["by_prompt_style"].get("neutral", {}).get("avg_refusal_rate", 0)

    h1_result = "✅ SUPPORTED" if llm_refusal > slm_refusal else "❌ NOT SUPPORTED"
    h2_result = "✅ SUPPORTED" if llm_score > slm_score else "❌ NOT SUPPORTED"
    h5_result = "✅ SUPPORTED" if (neutral_refusal - adv_refusal) > 0.3 else "❌ NOT SUPPORTED"

    lines.append(f"| H1 | LLMs refuse more than SLMs | {h1_result} ({_pct(llm_refusal)} vs {_pct(slm_refusal)}) |")
    lines.append(f"| H2 | LLMs score higher than SLMs | {h2_result} ({_score(llm_score)} vs {_score(slm_score)}) |")
    lines.append(f"| H5 | Adversarial prompts reduce refusals by >30% | {h5_result} |")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"📄 Markdown report → {output_path}")


def generate_html_report(summary: dict, output_path: str | Path) -> None:
    """Generate an HTML report from the summary JSON."""
    output_path = Path(output_path)

    model_rows = ""
    for model, stats in sorted(summary["by_model"].items()):
        refusal_pct = stats.get("avg_refusal_rate", 0)
        score = stats.get("avg_weighted_score", 0)
        color = "green" if refusal_pct > 0.7 else ("orange" if refusal_pct > 0.4 else "red")
        model_rows += f"""
        <tr>
            <td><strong>{model}</strong></td>
            <td><span class="badge">{stats.get('type', '?')}</span></td>
            <td style="color:{color}"><strong>{_pct(refusal_pct)}</strong></td>
            <td>{_score(score)}</td>
            <td>{stats.get('avg_explanation', 0):.2f}/5</td>
            <td>{stats.get('avg_cultural', 0):.2f}/5</td>
        </tr>"""

    domain_rows = ""
    for domain, stats in sorted(summary["by_domain"].items()):
        domain_rows += f"""
        <tr>
            <td>{domain}</td>
            <td>{_pct(stats.get('avg_refusal_rate', 0))}</td>
            <td>{_score(stats.get('avg_weighted_score', 0))}</td>
        </tr>"""

    llm = summary["llm_vs_slm"].get("LLM", {})
    slm = summary["llm_vs_slm"].get("SLM", {})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>LLM Ethics Evaluation Report</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 1100px; margin: 40px auto; padding: 20px; color: #333; }}
  h1 {{ color: #1a1a2e; border-bottom: 3px solid #e94560; padding-bottom: 10px; }}
  h2 {{ color: #16213e; margin-top: 40px; }}
  table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
  th {{ background: #16213e; color: white; padding: 10px 14px; text-align: left; }}
  td {{ padding: 9px 14px; border-bottom: 1px solid #eee; }}
  tr:hover {{ background: #f8f9fa; }}
  .badge {{ background: #e94560; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
  .badge.slm {{ background: #0f3460; }}
  .comparison {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
  .card {{ background: #f8f9fa; border-radius: 8px; padding: 20px; border-left: 4px solid #e94560; }}
  .card.slm {{ border-left-color: #0f3460; }}
  .stat {{ font-size: 28px; font-weight: bold; color: #1a1a2e; }}
  .label {{ font-size: 13px; color: #666; }}
  footer {{ margin-top: 60px; font-size: 12px; color: #999; text-align: center; }}
</style>
</head>
<body>
<h1>🧠 LLM Ethics Evaluation Report<br><small>Vietnamese Business Context</small></h1>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>

<h2>🤖 LLM vs SLM Comparison</h2>
<div class="comparison">
  <div class="card">
    <div class="label">Large Language Models (LLM)</div>
    <div class="stat">{_pct(llm.get('avg_refusal_rate', 0))}</div>
    <div class="label">Avg Refusal Rate</div>
    <br>
    <div class="stat">{_score(llm.get('avg_weighted_score', 0))}</div>
    <div class="label">Avg Weighted Ethics Score</div>
    <br>
    <div class="stat">{llm.get('avg_cultural', 0):.2f}/5</div>
    <div class="label">Avg Cultural Alignment</div>
  </div>
  <div class="card slm">
    <div class="label">Small Language Models (SLM)</div>
    <div class="stat">{_pct(slm.get('avg_refusal_rate', 0))}</div>
    <div class="label">Avg Refusal Rate</div>
    <br>
    <div class="stat">{_score(slm.get('avg_weighted_score', 0))}</div>
    <div class="label">Avg Weighted Ethics Score</div>
    <br>
    <div class="stat">{slm.get('avg_cultural', 0):.2f}/5</div>
    <div class="label">Avg Cultural Alignment</div>
  </div>
</div>

<h2>📋 Results by Model</h2>
<table>
  <tr>
    <th>Model</th><th>Type</th><th>Refusal Rate</th>
    <th>Weighted Score</th><th>Explanation</th><th>Cultural</th>
  </tr>
  {model_rows}
</table>

<h2>🏭 Results by Domain</h2>
<table>
  <tr><th>Domain</th><th>Refusal Rate</th><th>Avg Score</th></tr>
  {domain_rows}
</table>

<footer>LLM Ethics Evaluator — Vietnamese Business Context · {datetime.now().year}</footer>
</body>
</html>"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"🌐 HTML report → {output_path}")
