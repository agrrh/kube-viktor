import time
import logging

from codetiming import Timer

from kubernetes import client, config

from pod_selector import PodSelector
from pod_metrics_analyzer import PodMetricsAnalyzer
from pod_evictor import PodEvictor


class Controller(object):
    def __init__(
        self,
        kubeconfig_file=None,
        labels_selector={},
        handle_action="log",
        prom_address="http://prometheus.metrics.svc:9090/api/v1/query",
        prom_query=False,
        prom_query_threshold=0.8,
    ):
        super(Controller, self).__init__()

        self.kubeconfig_file = kubeconfig_file

        self.labels_selector = labels_selector
        self.handle_action = handle_action

        self.prom_address = prom_address
        self.prom_query = prom_query
        self.prom_query_threshold = prom_query_threshold

    @Timer(name="Loop body", text="{name} took {:.2f}s to complete", logger=logging.warning)
    def loop_body(self, pod_selector, pod_analyzer, pod_evictor):
        pods = list(pod_selector.get_all_suitable(self.labels_selector))
        pods_selected = list(filter(pod_analyzer.select_for_eviction, pods))

        [pod_evictor.handle(pod) for pod in pods_selected]

        logging.info(f"Listed {len(pods)} Pod(s), where {len(pods_selected)} Pod(s) were selected for processing")

    def run_loop(
        self,
        run_once=False,
        loop_delay=15,
    ):
        logging.critical("Initializing loop")

        try:
            config.load_kube_config(config_file=self.kubeconfig_file)
        except config.config_exception.ConfigException:
            config.load_incluster_config()

        kube_api = client.CoreV1Api()

        pod_selector = PodSelector(kube_api=kube_api)
        pod_analyzer = PodMetricsAnalyzer(
            prom_address=self.prom_address, prom_query=self.prom_query, prom_query_threshold=self.prom_query_threshold
        )
        pod_evictor = PodEvictor(kube_api=kube_api, default_action=self.handle_action)

        logging.critical("Starting loop")

        while True:
            # TODO Add leader election
            #   https://github.com/kubernetes-client/python/tree/master/kubernetes/base/leaderelection

            self.loop_body(pod_selector, pod_analyzer, pod_evictor)

            if run_once:
                logging.critical("Requested single run, stopping")
                break

            logging.info(f"Loop delay, sleeping for {loop_delay}s")
            time.sleep(loop_delay)
