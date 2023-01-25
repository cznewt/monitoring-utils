#!/usr/bin/env bash

extract-prometheus-metrics --path ./tests/data/prometheus/
extract-prometheus-metrics --path ./tests/data/prometheus/ --exclude_sources recording-rule-name
extract-prometheus-metrics --path ./tests/data/prometheus/ --exclude_sources recording-rule-expr
extract-prometheus-metrics --path ./tests/data/prometheus/ --exclude_sources alerting-rule-expr --format json
extract-prometheus-metrics --path ./tests/data/prometheus/ --exclude_sources recording-rule-name,recording-rule-expr
extract-prometheus-metrics --path ./tests/data/prometheus-grafana/
extract-prometheus-metrics --path ./tests/data/prometheus-grafana/ --exclude_files elasticsearch.json,prometheus-redis_rev1.json
