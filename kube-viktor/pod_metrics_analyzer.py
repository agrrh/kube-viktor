import logging
import requests


class PodMetricsAnalyzer(object):
    DEFAULT_PROM_QUERY = """
        sum(
            container_memory_usage_bytes{{namespace="{namespace}",pod="{name}",container!="POD"}}
            /
            container_spec_memory_limit_bytes
        ) by (namespace, pod)
    """

    ANNOTATION_THRESHOLD_KEY = "kube-viktor.agrrh.com/metric-threshold"

    def __init__(
        self,
        prom_address="http://prometheus.metrics.svc:9090/api/v1/query",
        prom_query=False,
        prom_query_threshold=0.8,
    ):
        super(PodMetricsAnalyzer, self).__init__()

        self.prom_address = prom_address
        self.prom_query = prom_query or self.DEFAULT_PROM_QUERY
        self.prom_query_threshold = prom_query_threshold

        logging.info(f"Prometheus address is: {self.prom_address}")
        logging.info(f"Prometheus query is: {self.prom_query}")
        logging.info(f"Prometheus threshold is: {self.prom_query_threshold}")

    def __annotations_check_override_threshold(self, pod):
        override_threshold = pod.metadata.annotations.get(self.ANNOTATION_THRESHOLD_KEY)

        if not override_threshold:
            return self.prom_query_threshold

        try:
            override_threshold = float(override_threshold)

            logging.info(
                f"Annotation overrides metric threshold, {self.prom_query_threshold} becomes {override_threshold}"
            )

            threshold = override_threshold
        except Exception as e:
            logging.error(e)

            threshold = self.prom_query_threshold

        return threshold

    def select_for_eviction(self, pod):
        logging.info(f"Checking metrics for Pod {pod.metadata.namespace}/{pod.metadata.name}")

        try:
            response = requests.get(
                self.prom_address,
                params={"query": self.prom_query.format(name=pod.metadata.name, namespace=pod.metadata.namespace)},
            ).json()

            logging.debug(response)

            # {
            #     "status": "success",
            #     "data": {
            #         "resultType": "vector",
            #         "result": [
            #             {
            #                 "metric": {"pod": "payload-b587bd7f-vqzz8"},
            #                 "value": [1655497979.83, "0.997100830078125"],  # timestamp and value
            #             }
            #         ],
            #     },
            # }

            if response.get("status") != "success":
                return False

        except Exception as e:
            logging.error(e)
            return False

        for metric in response.get("data", {}).get("result", []):
            try:
                _, value = metric.get("value")
                value = float(value)

            except Exception as e:
                logging.error(e)
                return False

            logging.debug(f"Metric value is {value}")

            if value == float("+inf"):
                logging.info(f"Pod {pod.metadata.namespace}/{pod.metadata.name} has {value} value, skipping")
                return False

            prom_query_threshold = self.__annotations_check_override_threshold(pod)

            if value > prom_query_threshold:
                logging.warning(f"Pod {pod.metadata.namespace}/{pod.metadata.name}: {value} > {prom_query_threshold}")

                return pod

            logging.debug(f"Pod {pod.metadata.namespace}/{pod.metadata.name}: {value} <= {prom_query_threshold}")
