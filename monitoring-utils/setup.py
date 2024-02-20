from setuptools import setup, find_packages

setup(
    name='monitoring_utils',
    version='0.2.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'markdown',
        'pyyaml',
        'requests',
        'pdfkit',
        'pandas',
    ],
    entry_points='''
        [console_scripts]
        prometheus-extract-metrics=monitoring_utils.cli:extract_prometheus_metrics
        grafana-convert-panels=monitoring_utils.cli:convert_grafana_panels
        grafana-generate-report=monitoring_utils.cli:generate_grafana_report
        grafana-export-panels=monitoring_utils.cli:export_grafana_panels
        monitoring-get-info=monitoring_utils.cli:get_resource_info
    ''',
)
