from monitoring_utils.query.prometheus import get_label

from math import floor
import datetime

import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)

test_queries = [
    {
        "url": "http://localhost:9090",
        "queries": ["up"],
        "label": "instance",
        "range": "1h",
        'step': 60,
        'result': ['localhost:9090']
    }
]

for test_query in test_queries:
    logging.info("Testing ...\n {}".format(test_query["queries"]))
    range = test_query.pop('range')
    test_query['end'] = datetime.datetime.now().timestamp()
    test_query['start'] = (datetime.datetime.now() -
                           datetime.timedelta(hours=1)).timestamp()

    labels = get_label(test_query, "instance")

    if set(labels) == set(test_query["result"]):
        logging.info("OK, found: {}\n".format(set(labels)))
    else:
        logging.info(
            "Failed, found: {}, expected: {}\n".format(
                set(labels), set(test_query["result"])
            )
        )
