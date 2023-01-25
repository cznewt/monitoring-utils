#!/usr/bin/env bash

prometheus-extract-metrics --path ./tests/data/prometheus/
prometheus-extract-metrics --path ./tests/data/prometheus/ --exclude_sources recording-rule-name
prometheus-extract-metrics --path ./tests/data/prometheus/ --exclude_sources recording-rule-expr
prometheus-extract-metrics --path ./tests/data/prometheus/ --exclude_sources alerting-rule-expr --format json
prometheus-extract-metrics --path ./tests/data/prometheus/ --exclude_sources recording-rule-name,recording-rule-expr
prometheus-extract-metrics --path ./tests/data/prometheus-grafana/
prometheus-extract-metrics --path ./tests/data/prometheus-grafana/ --exclude_files elasticsearch.json,prometheus-redis_rev1.json
