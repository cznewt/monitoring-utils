CWD=$(shell pwd)

.PHONY: test

test:
	python tests/test_query.py
	extract-prometheus-metrics --path ./tests/prometheus/
	extract-prometheus-metrics --path ./tests/prometheus/ --excludes recording-rule-name
	extract-prometheus-metrics --path ./tests/prometheus/ --excludes recording-rule-expr
	extract-prometheus-metrics --path ./tests/prometheus/ --excludes alerting-rule-expr --format json
	extract-prometheus-metrics --path ./tests/prometheus/ --excludes recording-rule-name,recording-rule-expr
	extract-prometheus-metrics --path ./tests/prometheus-grafana/
