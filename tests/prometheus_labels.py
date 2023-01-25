#!/usr/bin/env python
# encoding: utf-8

from monitoring_utils.query.prometheus import get_label

from math import floor
import datetime

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
    print("Testing ... {}".format(test_query["queries"]))
    range = test_query.pop('range')
    test_query['end'] = datetime.datetime.now().timestamp()
    test_query['start'] = (datetime.datetime.now() -
                           datetime.timedelta(hours=1)).timestamp()

    labels = get_label(test_query, "instance")

    if set(labels) == set(test_query["result"]):
        print("OK, found: {}\n".format(set(labels)))
    else:
        print(
            "Failed, found: {}, expected: {}\n".format(
                set(labels), set(test_query["result"])
            )
        )
