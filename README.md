
# Monitoring utilities

Utility scripts to work with monitoring resources:

* Grafana dashboards
* Prometheus alert and recording rules

## Cli tools

* Convert Grafana dashboards to jsonnet definitions
* Convert Prometheus rules to jsonnet definitions
* Parse out metric names from the Prometheus queries

### Supported Grafana libraries

* [grafonnet](https://github.com/grafana/grafonnet) - Current library to generate grafana dashboards, renders up-2-date Grafana charts
* [grafana-builder](https://github.com/grafana/jsonnet-libs/tree/master/grafana-builder) - Lightweight lib, still maintained, renders legacy Grafana charts
* [grafonnet-lib](https://github.com/grafana/grafonnet-lib) - Original grafonnet lib, used in most mixins, renders legacy Grafana charts


## Grafonnet extensions
