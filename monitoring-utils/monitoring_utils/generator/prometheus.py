import json
import os
import glob
import logging
import subprocess

from monitoring_utils.parsers.prom import parse_promql
from monitoring_utils.parsers.utils import parse_yaml

PROMETHEUS_RECORD_RULES = """
{
  prometheusRules+:: {
    groups+: [
        {}
    ]
  }
}"""

def convert_groups_to_jsonnet(rule, source_path, build_path):
    rule_lines = []

    for group in rule["groups"]:
        rule_lines.append(json.dumps(group, indent=2))

    rule_str = (
        "{\nprometheusAlerts+:: {\ngroups+: [\n" + ",\n".join(rule_lines) + "\n]\n}\n}"
    )

    if build_path == "":
        print(rule_str)
    else:
        filename = (
            rule["_filename"].replace(".yml", ".jsonnet").replace(".yaml", ".jsonnet")
        )
        build_file = build_path + "/" + filename
        with open(build_file, "w") as the_file:
            the_file.write(rule_str)
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
                "Error `{}` converting rules file `{}/{}` to `{}`.".format(
                    output, source_path, rule["_filename"], build_file
                )
            )
        else:
            logging.info(
                "Converted rules file `{}/{}` to `{}`.".format(
                    source_path, rule["_filename"], build_file
                )
            )

    return rule_str
