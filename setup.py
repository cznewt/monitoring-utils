from setuptools import setup, find_packages

setup(
    name='monitoring_utils',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'markdown',
        'pyyaml',
        'requests',
        'pdfkit',
        'promqlpy',
        'pandas',
    ],
    entry_points='''
        [console_scripts]
        extract-prometheus-metrics=monitoring_utils.cli:extract_prometheus_metrics
        convert-grafana-panels=monitoring_utils.cli:convert_grafana_panels
        generate-grafana-report=monitoring_utils.cli:generate_grafana_report
        export-grafana-panels=monitoring_utils.cli:export_grafana_panels
        get-resource-info=monitoring_utils.cli:get_resource_info
    ''',
)
