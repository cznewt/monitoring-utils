
import markdown
import pdfkit
from monitoring_utils.utils import ServeDirectoryWithHTTP

HTML_TEMPLATE = '''
<html>
<head>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" crossorigin="anonymous">
<style>
@media print {{
  .page-break-after {{
    page-break-after: always;
  }}
}}
</style>
</head>
<body>
{}
</body>
</html>
'''

CONTENT_TEMPLATE = '''

# Report for {}

## Time range reported: {} - {}

Report contains:

* Visualizations of selected panels
* CSV data for further analysis

<p class="page-break-after">&nbsp;</p>

{}
'''


def generate_doc(title, start, end, panels, build_path):
    panels_text = []
    for panel in panels:
        panels_text.append('#### ' + panel['name'])
        panels_text.append('')
        panels_text.append('<img src="' + panel['path'] + '" />')

    text = CONTENT_TEMPLATE.format(title, start, end, '\n'.join(panels_text))

    html = HTML_TEMPLATE.format(markdown.markdown(text))
    file = open(build_path + '/doc-output.html', "w")
    file.write(html)
    file.close()

    http_server, http_address = ServeDirectoryWithHTTP(build_path)

    pdfkit.from_url(
        http_address + '/doc-output.html',
        build_path + '/doc-output.pdf')
