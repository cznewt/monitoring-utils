import subprocess
import logging

GRAFONNET_INCLUDES = """
    local grafana = import 'grafonnet/grafana.libsonnet';
    local dashboard = grafana.dashboard;
    local row = grafana.row;
    local prometheus = grafana.prometheus;
    local template = grafana.template;
    local graphPanel = grafana.graphPanel;"""

GRAFONNET_DASHBOARD = """
    dashboard.new(\n{}, tags={})"""

GRAFONNET_ROW = """
    row.new()"""

GRAFONNET_GRAPH_PANEL = """
    graphPanel.new(
      '{}',
      datasource='$datasource',
      span={},
      format='{}',
      stack={},
      min=0,
    )"""

GRAFONNET_SINGLESTAT_PANEL = """
    singlestat.new(
      '{}',
      datasource='$datasource',
      span={},
      format='{}',
      valueName='current',
    )"""

GRAFONNET_PROMETHEUS_TARGET = """
    .addTarget(
      prometheus.target(
        |||
          {}
        ||| % $._config,
        legendFormat='',
      )
    )"""

GRAFONNET_INFLUXDB_TARGET = """
    .addTarget(
      influxdb.target(
        |||
          {}
        ||| % $._config,
        alias='{}',
      )
    )"""

GRAPH_BUILDER_DASHBOARD = """
    g.dashboard({}, tags={})
"""


def create_dashboard(dashboard, format, source_path, build_path):
    dashboard_lines = []
    if format == "grafonnet":
        dashboard_lines.append(GRAFONNET_INCLUDES)
        dashboard_lines.append("{\ngrafanaDashboards+:: {")
        dashboard_lines.append("'{}':".format(dashboard["filename"]))
        dashboard_lines.append(
            GRAFONNET_DASHBOARD.format(
                '"' + dashboard.get("title", "N/A") + '"', [])
        )
        for variable in dashboard.get("templating", {}).get("list", []):
            if variable["type"] == "query":
                if variable["multi"]:
                    multi = "Multi"
                else:
                    multi = ""
                dashboard_lines.append(
                    "\n.add{}Template('{}', '{}', 'instance')".format(
                        multi, variable["name"], variable["query"]
                    )
                )
    else:
        dashboard_body = GRAPH_BUILDER_DASHBOARD.format(
            '"' + dashboard.get("title", "N/A") + '"', []
        )
        for variable in dashboard.get("templating", {}).get("list", []):
            if variable["type"] == "query":
                if variable["multi"]:
                    multi = "Multi"
                else:
                    multi = ""
                dashboard_body += "\n.add{}Template('{}', '{}', 'instance')".format(
                    multi, variable["name"], variable["query"]
                )

        dashboard_lines.append("}\n}")

    dashboard_str = "\n".join(dashboard_lines)


def convert_panel(panel, format):
    lines = []
    if format == "grafonnet":
        if panel["type"] == "singlestat":
            lines.append(
                GRAFONNET_SINGLESTAT_PANEL.format(
                    panel["title"], panel["span"], panel["format"]
                )
            )
        if panel["type"] == "graph":
            lines.append(
                GRAFONNET_GRAPH_PANEL.format(
                    panel["title"],
                    panel["span"],
                    panel["yaxes"][0]["format"],
                    panel["stack"],
                )
            )
        for target in panel.get("targets", []):
            if "expr" in target:
                lines.append(
                    GRAFONNET_PROMETHEUS_TARGET.format(target["expr"])
                )
    lines.append(")")


def old_convert_panel(data, format, source_path, build_path):
    dashboard_lines = []
    if format == "grafonnet":
        for row in dashboard.get("rows", []):
            dashboard_lines.append(".addRow(")
            dashboard_lines.append("row.new()")

        dashboard_lines.append("}\n}")

    dashboard_str = "\n".join(dashboard_lines)

    if build_path == "":
        print("JSONNET:\n{}".format(dashboard_str))
        #print("JSON:\n{}".format(_jsonnet.evaluate_snippet("snippet", dashboard_str)))
    else:
        build_file = (
            build_path + "/" +
            dashboard["filename"].replace(".json", ".jsonnet")
        )
        with open(build_file, "w") as the_file:
            the_file.write(dashboard_str)
        output = (
            subprocess.Popen(
                "jsonnet fmt -n 2 --max-blank-lines 2 --string-style s --comment-style s -i "
                + build_file,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            .stdout.read()
            .decode("utf-8")
        )
        if "ERROR" in output:
            logging.info(
                "Error `{}` converting dashboard `{}/{}` to `{}`".format(
                    output, source_path, dashboard["_filename"], build_file
                )
            )
        else:
            logging.info(
                "Converted dashboard `{}/{}` to `{}` ({} format)".format(
                    source_path, dashboard["_filename"], build_file, format
                )
            )

    return dashboard_str
