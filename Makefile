CWD=$(shell pwd)

.PHONY: test

test:
	python tests/test_query.py
	extract-prometheus-metrics --path ./tests/prometheus/
	extract-prometheus-metrics --path ./tests/prometheus/ --exclude_sources recording-rule-name
	extract-prometheus-metrics --path ./tests/prometheus/ --exclude_sources recording-rule-expr
	extract-prometheus-metrics --path ./tests/prometheus/ --exclude_sources alerting-rule-expr --format json
	extract-prometheus-metrics --path ./tests/prometheus/ --exclude_sources recording-rule-name,recording-rule-expr
	extract-prometheus-metrics --path ./tests/prometheus-grafana/
	extract-prometheus-metrics --path ./tests/prometheus-grafana/ --exclude_files elasticsearch.json,prometheus-redis_rev1.json
