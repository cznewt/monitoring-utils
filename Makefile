CWD=$(shell pwd)

.PHONY: test
test:
	./tests/prometheus_metrics.py
	./tests/prometheus_cli_tests.sh
