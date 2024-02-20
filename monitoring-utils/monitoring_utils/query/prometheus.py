import pandas as pd
import numpy as np
import datetime
from monitoring_utils.query import Query, InstantQuery, RangeQuery

PROMETHEUS_REPLY = "Prometheus API replied with error {}: {}"


class PrometheusQuery(Query):
    def __init__(self, **kwargs):
        kwargs["queries"] = [kwargs["query"]]
        if kwargs.get("moment", None) == None:
            self.query = 'range'
            self._collector = PrometheusRangeQuery(**kwargs)
        else:
            self.query = 'moment'
            self._collector = PrometheusInstantQuery(**kwargs)
        super(PrometheusQuery, self).__init__(**kwargs)

    def _render_info(self):
        info = "Query info:\n".format(**self._info)
        info += "  Server URL: {url}\n".format(**self._info)
        if self.query == 'range':
            info += "  Type: Range PromQL query\n".format(**self._info)
        else:
            info += "  Type: Instant PromQL query\n".format(**self._info)
        info += "  Query: {query}\n".format(**self._info)
        if self.query == 'range':
            info += "  Duration: {start} - {end}\n".format(**self._info)
        else:
            info += "  Moment: {moment}\n".format(**self._info)
        info += "  Step: {step}\n".format(**self._info)
        return info


class PrometheusRangeQuery(RangeQuery):
    def __init__(self, **kwargs):
        super(PrometheusRangeQuery, self).__init__(**kwargs)

    def data(self):
        data = self._http_get_params()
        return self._process(data)

    def _params(self):
        return {
            "query": self.queries,
            "start": self.start,
            "end": self.end,
            "step": self.step,
        }

    def _url(self):
        url = "/api/v1/query_range"
        if self.step:
            return self.base_url + url + "?step=%s" % self.step
        return self.base_url + url

    def _process(self, response):
        if response["status"] == "error":
            raise Exception(
                PROMETHEUS_REPLY.format(
                    response["errorType"], response["error"])
            )
        self.raw_data = response["data"]["result"]
        for series in self.raw_data:
            for values in series["values"]:
                values[0] = pd.Timestamp(
                    datetime.datetime.fromtimestamp(values[0]))
                values[1] = float(values[1])

        np_data = [
            (
                "{}_{}".format(
                    series["metric"].get("__name__", "name"),
                    series["metric"].get("instance", "instance"),
                ),
                np.array(series["values"]),
            )
            for series in self.raw_data
        ]

        series = []
        for query, serie in np_data:
            frame = pd.DataFrame(
                serie[:, 1], index=serie[:, 0], columns=[query])
            series.append(frame)
        if len(series) > 0:
            return pd.concat(series, axis=1, join="inner")
        else:
            return None


class PrometheusInstantQuery(InstantQuery):
    def __init__(self, **kwargs):
        super(PrometheusInstantQuery, self).__init__(**kwargs)

    def data(self):
        data = self._http_get_params()
        return self._process(data)

    def _params(self):
        return {"query": self.queries, "time": self.moment}

    def _url(self):
        url = "/api/v1/query"
        return self.base_url + url

    def _process(self, response):
        if response["status"] == "error":
            raise Exception(
                PROMETHEUS_REPLY.format(
                    response["errorType"], response["error"])
            )
        self.raw_data = response["data"]["result"]

        for series in self.raw_data:
            for values in [series["value"]]:
                values[0] = pd.Timestamp(
                    datetime.datetime.fromtimestamp(values[0]))
                values[1] = float(values[1])
        np_data = [
            (
                "{}_{}".format(
                    series["metric"]["__name__"], series["metric"]["instance"]
                ),
                np.array([series["value"]]),
            )
            for series in self.raw_data
        ]
        series = []
        for query, serie in np_data:
            frame = pd.DataFrame(
                serie[:, 1], index=serie[:, 0], columns=[query])
            series.append(frame)
        if len(series) > 0:
            return pd.concat(series, axis=1, join="inner")
        else:
            return None


def get_label(params, label):
    query = PrometheusRangeQuery(
        **params
    )
    query.data()
    result = []
    for serie in query.raw_data:
        if label in serie['metric']:
            if serie['metric'][label] not in result:
                result.append(serie['metric'][label])
    return(result)
