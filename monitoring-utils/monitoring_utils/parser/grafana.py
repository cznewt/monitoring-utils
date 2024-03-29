import os
import requests
import logging
from monitoring_utils.utils import parse_yaml
from monitoring_utils.parser.prometheus import parse_promql
from monitoring_utils.parser.utils import guess_query_language


def clean_dashboard_variable(query):
    if "label_values(" in query:
        query = query.replace("label_values(", "")
        query = ",".join(query.split(",")[:-1])
    return query


def get_panel_metrics(panel):
    metrics = []
    for target in panel.get("targets", []):
        if target.get("expr", "") != "":
            logging.debug(
                "Found query: {}".format(
                    target.get("expr", "")
                    .replace("\n", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                    .replace("  ", " ")
                )
            )
            queries = parse_promql(target.get("expr", ""))
            metrics += queries
    return metrics


def get_dashboard_live_data(grafana_url, grafana_token, grafana_dashboard_uid, grafana_dashboard_slug, range, end=None):
    data_url = '{}/api/dashboards/uid/{}'.format(
        grafana_url, grafana_dashboard_uid)

    logging.debug(
        "Getting data for '{}' dashboard ...".format(
            data_url,
        )
    )
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + grafana_token
    }

    r = requests.get(data_url, headers=headers)
    data = r.json()['dashboard']
    return data


def get_panel_screenshot(grafana_url, grafana_token, grafana_dashboard_uid, grafana_dashboard_slug, grafana_org_id, grafana_panel_id, start, end, width=1200, height=600, vars={}):
    data_url = '{}/render/d-solo/{}/{}'.format(
        grafana_url,
        grafana_dashboard_uid,
        grafana_dashboard_slug,
    )

    logging.debug(
        "Getting screen from '{}' dashboard panel ...".format(
            data_url,
        )
    )

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + grafana_token
    }

    params = {
        'orgId': grafana_org_id,
        'refresh': '60s',
        'from': start,
        'to': end,
        'theme': 'light',
        'panelId': grafana_panel_id,
        'width': width,
        'height': height,
        'tz': 'Europe/Prague'
    }
    params.update(vars)

    r = requests.get(data_url, params=params,
                     headers=headers, allow_redirects=True)
    data = r.content
    return data


def get_dashboard_data(board_file, excludes=[]):
    dashboard = parse_yaml(board_file)
    panels = []
    metrics = []
    logging.debug(
        "Searching '{}' dashboard at {} ...".format(
            dashboard.get("title", "untitled"), board_file
        )
    )
    if 'dashboard-variable' not in excludes:
        for variable in dashboard.get("templating", {}).get("list", []):
            if variable.get("type", "") == "query":
                if type(variable.get("query", None)) == dict:
                    query = variable["query"].get("query", "")
                else:
                    query = variable.get("query", "")
                query_lang = guess_query_language(query)
                if query_lang != 'promql':
                    logging.debug("Possible {} query: {}".format(query_lang, query))
                    query = ""
                if query != "":
                    logging.debug(
                        "Found '{}' variable ...".format(
                            variable.get("name", "unnamed"))
                    )
                    logging.debug("Found query: {}".format(query))
                    query = clean_dashboard_variable(query)
                    metrics += parse_promql(query)
    if 'dashboard-annotation' not in excludes:
        for annotation in dashboard.get("annotations", {}).get("list", []):
            if "expr" in annotation:
                query = annotation["expr"]
                logging.debug(
                    "Found {} annotation ...".format(
                        annotation.get("name", "unnamed"))
                )
                logging.debug("Found query: {}".format(query))
                metrics += parse_promql(query)
    if 'dashboard-panel' not in excludes:
        for panel in dashboard.get("panels", []):
            if "targets" in panel:
                logging.debug("Found '{}' panel ...".format(
                    panel.get("title", "untitled")))
                panels.append(panel)
                metrics += get_panel_metrics(panel)
            if "panels" in panel:
                for subpanel in panel.get("panels", []):
                    if "targets" in subpanel:
                        logging.debug("Found '{}' panel ...".format(
                            subpanel.get("title", "untitled")))
                        panels.append(subpanel)
                        metrics += get_panel_metrics(subpanel)
        if dashboard.get("rows", []) == None:
            logging.error("Dashboard {} has Null row".format(board_file))
            dashboard["rows"] = []
        for row in dashboard.get("rows", []):
            for panel in row.get("panels", []):
                if "targets" in panel:
                    logging.debug("Found '{}' panel ...".format(
                        panel.get("title", "untitled")))
                    panels.append(panel)
                    metrics += get_panel_metrics(panel)
    final_metrics = sorted(list(set(metrics)))
    dashboard["filename"] = os.path.basename(board_file)
    dashboard["panels"] = panels
    dashboard["metrics"] = final_metrics
    return dashboard
