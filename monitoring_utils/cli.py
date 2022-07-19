#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import logging
from .core import export_panels_from_grafana, convert_panels_by_path, \
    get_info_by_path, find_metrics_by_path, generate_report_from_grafana
from .utils import set_logger, encode_json


@click.command()
@click.option(
    "--source-path",
    default="./source",
    help="Path to search for the source Grafana dashboards.",
)
@click.option(
    "--build-path",
    default="",
    help="Path to save converted JSONNET dashboards, none to print to console.",
)
@click.option(
    "--format",
    default="grafonnet",
    help="Format of the dashboard: `grafonnet` or `grafana-builder`.",
)
@click.option(
    "--layout",
    default="rows",
    help="Format of the dashboard: `normal` (scheme 14) , `grid` (scheme 16).",
)
def convert_grafana_panels(source_path, build_path, format, layout):
    """Convert Grafana dashboard panels to JSONNET format."""
    set_logger()
    logging.debug(
        "Searching path `{}` for panels to convert ...".format(source_path)
    )
    convert_panels_by_path(source_path, build_path, format, layout)


@click.command()
@click.option(
    "--grafana-url",
    envvar='GRAFANA_URL',
    help="Base URL of Grafana instance.",
)
@click.option(
    "--grafana-token",
    envvar='GRAFANA_TOKEN',
    help="API key for the Grafana instance.",
)
@click.option(
    "--grafana-dashboard-uid",
    help="Grafana dashboard UID.",
)
@click.option(
    "--grafana-dashboard-slug",
    help="Grafana dashboard slug.",
)
@click.option(
    "--build-path",
    default="./build",
    help="Path to save exported panels.",
)
@click.option(
    "--format",
    default="png",
    help="Format of the panel oputput: `png` or `svg`.",
)
@click.option(
    "--range",
    default="7d",
    help="Range for the panel data",
)
def generate_grafana_report(grafana_url, grafana_token, grafana_dashboard_uid, grafana_dashboard_slug, build_path, format, range):
    """Export Grafana dashboard panels data or image."""
    set_logger()
    logging.debug(
        "Generating report from `{}` dashboard ...".format(grafana_url)
    )
    generate_report_from_grafana(grafana_url, grafana_token, grafana_dashboard_uid, grafana_dashboard_slug, build_path, format, range)


@click.command()
@click.option(
    "--grafana-url",
    envvar='GRAFANA_URL',
    help="Base URL of Grafana instance.",
)
@click.option(
    "--grafana-token",
    envvar='GRAFANA_TOKEN',
    help="API key for the Grafana instance.",
)
@click.option(
    "--grafana-dashboard-uid",
    help="Grafana dashboard UID.",
)
@click.option(
    "--grafana-dashboard-slug",
    help="Grafana dashboard slug.",
)
@click.option(
    "--build-path",
    default="./build",
    help="Path to save exported panels.",
)
@click.option(
    "--format",
    default="png",
    help="Format of the panel oputput: `png` or `svg`.",
)
@click.option(
    "--range",
    default="7d",
    help="Range for the panel data",
)
def export_grafana_panels(grafana_url, grafana_token, grafana_dashboard_uid, grafana_dashboard_slug, build_path, format, range):
    """Export Grafana dashboard panels data or image."""
    set_logger()
    logging.debug(
        "Searching `{}` for panels to export ...".format(grafana_url)
    )
    export_panels_from_grafana(grafana_url, grafana_token, grafana_dashboard_uid, grafana_dashboard_slug, build_path, format, range)


@click.command()
@click.option(
    "--path", default="./data",
    help="Path to search for the source Grafana dashboards."
)
def get_resource_info(path):
    """Get info from monitoring resources."""
    set_logger()
    logging.debug(
        "Searching path `{}` for Grafana dashboards...".format(path)
    )
    print(get_info_by_path(path))


@click.command()
@click.option(
    "--path", default="./data", help="Path to search for the YAML rule definions."
)
@click.option(
    "--format", default="string", help="Format of the output [string/json]")
@click.option(
    "--exclude_sources",
    default="none",
    help="Exclude sources from parsing, possible: dashboard-variable, dashboard-annotation, recording-rule-expr, recording-rule-name, alerting-rule-expr",
)
@click.option(
    "--exclude_files",
    default="none",
    help="Exclude sources from parsing, possible: dashboard-variable, dashboard-annotation, recording-rule-expr, recording-rule-name, alerting-rule-expr",
)
def extract_prometheus_metrics(path, format, exclude_sources, exclude_files):
    """Get metric names from Grafana dashboard targets and Prometheus rule expressions."""
    set_logger()
    logging.debug(
        "Searching path `{}` for metrics ...".format(path)
    )
    metrics = find_metrics_by_path(path, format, exclude_sources.split(','), exclude_files.split(','))
    if format == 'string':
        print('\n'.join(metrics))
    else:
        print(encode_json(metrics))
