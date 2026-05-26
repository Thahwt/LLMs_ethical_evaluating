.PHONY: install generate evaluate score report test clean

install:
	pip install -r requirements.txt

generate:
	python src/generators/scenario_generator.py \
		--count 100 \
		--output data/raw/scenarios_raw.json
	python src/generators/prompt_variants.py \
		--input data/raw/scenarios_raw.json \
		--output data/processed/dataset.jsonl

evaluate:
	python src/evaluators/model_runner.py \
		--dataset data/processed/dataset.jsonl \
		--models configs/models.yaml \
		--output data/results/ \
		--lang en

score:
	python src/evaluators/ethical_scorer.py \
		--results data/results/ \
		--rubric configs/evaluation.yaml \
		--report data/results/summary_report.json

report:
	python -c "\
import json; \
from src.utils.report import generate_markdown_report, generate_html_report; \
s = json.load(open('data/results/summary_report.json')); \
generate_markdown_report(s, 'data/results/report.md'); \
generate_html_report(s, 'data/results/report.html')"

test:
	pytest tests/ -v --tb=short

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

all: install generate evaluate score report
