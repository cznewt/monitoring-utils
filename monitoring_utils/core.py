import glob
import logging
import datetime
from .generator.grafana import create_dashboard, convert_panel
from .generator.doc import generate_doc
from .parser.grafana import get_dashboard_data, get_dashboard_live_data, get_panel_screenshot
from .parser.prometheus import get_groups_data
from .utils import guess_file_type, get_file_name, write_image


def get_info_by_path(path):
    output = []
    files = glob.glob("{}/*.*".format(path))
    for file in files:
        type = guess_file_type(file)
        logging.debug('Found resource file {} of "{}" type'.format(file, type))
        if type == 'dashboard':
            dashboard = get_dashboard_data(file)
            output.append(str(dashboard))
        if type == 'rules':
            groups = get_groups_data(file)
            output.append(str(groups))
    if len(files) == 0:
        logging.error("No dashboards found at path {}!".format(path))
    return "\n".join(output)


def find_metrics_by_path(path, format="yaml", exclude_sources=[], exclude_files=[]):
    files = glob.glob("{}/*.*".format(path))
    dasbhoard_metrics = []
    rules_metrics = []
    total_metrics = []
    if files == None:
        return total_metrics
    for file in files:
        if get_file_name(file) in exclude_files:
            logging.debug('Excluded file {}'.format(file))
            continue
        type = guess_file_type(file)
        logging.debug('Found resource file {} of "{}" type'.format(file, type))
        if type == 'dashboard':
            dashboard = get_dashboard_data(file, exclude_sources)
            dasbhoard_metrics += dashboard["metrics"]
            total_metrics += dashboard["metrics"]
        if type == 'rules':
            groups = get_groups_data(file, exclude_sources)
            rules_metrics += groups["metrics"]
            total_metrics += groups["metrics"]

    total_metrics = sorted(list(set(dasbhoard_metrics+rules_metrics)))

    return total_metrics


def convert_panels_by_path(source_path, build_path, format, layout):
    board_files = glob.glob("{}/*.json".format(source_path))
    for board_file in board_files:
        type = guess_file_type(board_file)
        if type == 'dashboard':
            logging.debug(
                'Found resource file {} of "{}" type'.format(board_file, type))
            dashboard = get_dashboard_data(board_file)
            for panel in dashboard['panels']:
                convert_panel(panel, format)

    if len(board_files) == 0:
        logging.error("No dashboards found at path {}!".format(source_path))


def export_panels_from_grafana(grafana_url, grafana_token, grafana_dashboard_uid, grafana_dashboard_slug, grafana_dashboard_params, build_path, format, range):
    dashboard = get_dashboard_live_data(
        grafana_url, grafana_token, grafana_dashboard_uid, grafana_dashboard_slug, grafana_dashboard_params, range)
    grafana_panel_id = 1

    ct = datetime.datetime.now()
    ago = 3600 * 24 * 7
    raw_end = int(ct.timestamp())
    raw_start = raw_end - ago
    end = raw_end * 1000
    start = raw_start * 1000

    if 'rows' in dashboard:
        for panel in dashboard['rows']:
            if format == 'png':
                screen = get_panel_screenshot(grafana_url, grafana_token,
                                              grafana_dashboard_uid, grafana_dashboard_slug,
                                              grafana_panel_id,
                                              start, end)
                image_path = build_path + '/' + grafana_dashboard_slug + \
                    '-' + str(grafana_panel_id) + '.png'
                grafana_panel_id += 1
                write_image(image_path, screen)


def generate_report_from_grafana(grafana_url, grafana_token, grafana_dashboard_uid, grafana_dashboard_slug, grafana_dashboard_params, build_path, format, range):
    dashboard = get_dashboard_live_data(
        grafana_url, grafana_token, grafana_dashboard_uid, grafana_dashboard_slug, range)

    grafana_panel_id = 1
    title = dashboard['title']
    range = 'past week'
    panels = []

    ct = datetime.datetime.now()
    ago = 3600 * 24 * 7
    raw_end = int(ct.timestamp())
    raw_start = raw_end - ago
    end = raw_end * 1000
    start = raw_start * 1000
    print_end = ct.strftime("%Y-%m-%d %H:%M:%S")
    start_ct = ct - datetime.timedelta(seconds=ago)
    print_start = start_ct.strftime("%Y-%m-%d %H:%M:%S")

    if 'rows' in dashboard:
        for panel in dashboard['rows']:
            if format == 'png':
                screen = get_panel_screenshot(grafana_url, grafana_token,
                                              grafana_dashboard_uid, grafana_dashboard_slug,
                                              grafana_panel_id,
                                              start, end)
                image_path = build_path + '/' + grafana_dashboard_slug + \
                    '-' + str(grafana_panel_id) + '.png'
                write_image(image_path, screen)
                panels.append(
                    {
                        'name': panel['title'],
                        'path': './' + grafana_dashboard_slug + '-' + str(grafana_panel_id) + '.png'
                    }
                )
                grafana_panel_id += 1
    generate_doc(title, print_start, print_end, panels, build_path)
