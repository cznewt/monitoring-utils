import re
import logging
from monitoring_utils.utils import parse_yaml

from .utils import clean_comments

split_keywords = [
    " / ",
    " + ",
    " * ",
    " - ",
    ">",
    "<",
    " or ",
    " OR ",
    " and ",
    " AND ",
    " unless "
    " UNLESS "
    " group_left ",
    " GROUP_LEFT ",
    " group_right ",
    " GROUP_RIGHT ",
]
keywords = [
    "-",
    "/",
    "(",
    ")",
    "!",
    ",",
    "^",
    ".",
    '"',
    "=",
    "*",
    "+",
    ">",
    "<",
    " instance ",
    " job ",
    " type ",
    " url ",
    "?:",
]

final_keywords = [
    "$filter",
    "0",
    "abs",
    "absent",
    "absent_over_time",
    "and",
    "acos",
    "acosh",
    "asin",
    "asinh",
    "atan",
    "atanh",
    "avg",
    "avg_over_time",
    "bool",
    "bottomk",
    "ceil",
    "changes",
    "clamp_max",
    "clamp_min",
    "cos",
    "cosh",
    "count",
    "count_over_time",
    "count_values",
    "d",
    "day_of_month",
    "day_of_week",
    "days_in_month",
    "deg",
    "delta",
    "deriv",
    "e",
    "exp",
    "floor",
    "group_left",
    "group_right",
    "h",
    "histogram_quantile",
    "holt_winters",
    "hour",
    "idelta",
    "increase",
    "inf",
    "irate",
    "json",
    "label_join",
    "label_replace",
    "last_over_time",
    "ln",
    "log10",
    "log2",
    "m",
    "max",
    "max_over_time",
    "min",
    "min_over_time",
    "minute",
    "month",
    "offset",
    "on",
    "or",
    "pi",
    "predict_linear",
    "present_over_time",
    "quantile_over_time",
    "rad",
    "rate",
    "resets",
    "round",
    "s",
    "scalar",
    "sgn",
    "sin",
    "sinh",
    "sort",
    "sort_desc",
    "sqrt",
    "stddev",
    "stddev_over_time",
    "stdvar",
    "stdvar_over_time",
    "sum",
    "sum_over_time",
    "tan",
    "tanh",
    "time",
    "timestamp",
    "topk",
    "values",
    "vector",
    "w",
    "y",
    "year",
    "|",
    "$",
]


def get_groups_data(file, excludes=[]):
    groups = parse_yaml(file)
    metrics = []
    for group in groups.get("groups", []):
        for rul in group.get("rules", []):
            logging.debug(
                "Found '{}' rule ...".format(
                    rul.get("alert", rul.get('record')))
            )
            if 'record' in rul:
                if 'recording-rule-expr' not in excludes:
                    if "expr" in rul:
                        logging.debug("Found query: {}".format(rul["expr"]))
                        metrics += parse_promql(rul["expr"])
                if 'recording-rule-name' not in excludes:
                    metrics += parse_promql(rul["record"])
            else:
                if 'alerting-rule-expr' not in excludes:
                    if "expr" in rul:
                        logging.debug("Found query: {}".format(rul["expr"]))
                        metrics += parse_promql(rul["expr"])
    return {
        'filename': file,
        'metrics': sorted(list(set(metrics)))
    }


def split_by_keyword(query, split_keywords, level=0):
    if level < len(split_keywords):
        new_query = []
        for item in query:
            new_query = new_query + item.split(split_keywords[level])
        return split_by_keyword(new_query, split_keywords, level + 1)

    else:
        return query


def parse_promql(orig_query):
    query = clean_comments(orig_query)
    query = re.sub(r"[0-9]+e[0-9]+", "", query)
    query = query.replace(" [0-9]+ ", "")
    query = re.sub(
        r"group_left \((\w|,| )+\)", " group_left ", query, flags=re.IGNORECASE
    )
    query = re.sub(
        r"group_left\((\w|,| )+\)", " group_left ", query, flags=re.IGNORECASE
    )
    query = re.sub(
        r"group_right \((\w|,| )+\)", " group_right ", query, flags=re.IGNORECASE
    )
    query = re.sub(
        r"group_right\((\w|,| )+\)", " group_right ", query, flags=re.IGNORECASE
    )

    subqueries = split_by_keyword([query], split_keywords, 0)

    #logging.debug("Step 1: {}".format(query))
    subquery_output = []
    for subquery in subqueries:
        subquery = re.sub(r"\{.*\}", "", subquery)
        subquery = re.sub(r"\[.*\]", "", subquery)
        subquery = re.sub(r"\".*\"", "", subquery)

        subquery = re.sub(r"by \((\w|,| )+\)", "",
                          subquery, flags=re.IGNORECASE)
        subquery = re.sub(r"by\((\w|,| )+\)", "",
                          subquery, flags=re.IGNORECASE)
        subquery = re.sub(r"on \((\w|,| )+\)", "",
                          subquery, flags=re.IGNORECASE)
        subquery = re.sub(r"on\((\w|,| )+\)", "",
                          subquery, flags=re.IGNORECASE)
        subquery = re.sub(r"without \(.*\)", "", subquery, flags=re.IGNORECASE)
        subquery = re.sub(r"without\(.*\)", "", subquery, flags=re.IGNORECASE)
        subquery_output.append(subquery)
    query = " ".join(subquery_output)

    #logging.debug("Step 2: {}".format(query))
    for keyword in keywords:
        query = query.replace(keyword, " ")
    query = re.sub(r" [0-9]+ ", " ", query)
    query = re.sub(r" [0-9]+", " ", query)
    query = re.sub(r"^[0-9]+$", " ", query)
    query = query.replace("(", " ")
    final_queries = []

    #logging.debug("Step 3: {}".format(query))
    raw_queries = query.split(" ")
    for raw_query in raw_queries:
        if raw_query.lower().strip() not in final_keywords:
            raw_query = re.sub(r"^[0-9]+$", " ", raw_query)
            if raw_query.strip() != "":
                final_queries.append(raw_query.strip())

    output = list(set(final_queries))

    #logging.debug("Parsed query: {}".format(orig_query))
    logging.debug("Extracted metric(s): {}".format(", ".join(output)))
    return output
