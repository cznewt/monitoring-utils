CWD=$(shell pwd)

.PHONY: test-parser
test-parser:
	python tests/test_parser.py
	extract-prometheus-metrics --path ./tests/prometheus/
	extract-prometheus-metrics --path ./tests/prometheus/ --exclude_sources recording-rule-name
	extract-prometheus-metrics --path ./tests/prometheus/ --exclude_sources recording-rule-expr
	extract-prometheus-metrics --path ./tests/prometheus/ --exclude_sources alerting-rule-expr --format json
	extract-prometheus-metrics --path ./tests/prometheus/ --exclude_sources recording-rule-name,recording-rule-expr
	extract-prometheus-metrics --path ./tests/prometheus-grafana/
	extract-prometheus-metrics --path ./tests/prometheus-grafana/ --exclude_files elasticsearch.json,prometheus-redis_rev1.json

.PHONY: test
test: test-parser