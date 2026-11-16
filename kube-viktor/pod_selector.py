import logging
import threading
import time

from kubernetes import watch


class PodSelector(object):
    WATCH_RETRY_DELAY = 5

    def __init__(self, kube_api):
        super(PodSelector, self).__init__()

        self.kube_api = kube_api

        self.__pods = {}
        self.__pods_lock = threading.Lock()

        self.__ready = threading.Event()

    def __pod_process_empty_labels(self, pod):
        logging.debug("Checking if Pod labels are empty")

        return bool(pod.metadata.labels)

    def __selector_dict_to_raw(self, selector):
        return ",".join([f"{k}={v}" for k, v in selector.items()])

    def __pod_process_phase(self, pod):
        logging.debug("Checking if Pod is running")

        return pod.status.phase == "Running"

    def __pod_process_limits(self, pod):
        logging.debug("Checking if Pod has memory limits")

        def container_has_memory_limits(container):
            return container.resources.limits and bool(container.resources.limits.get("memory"))

        return any(map(container_has_memory_limits, pod.spec.containers))

    def __remember_pod(self, pod):
        with self.__pods_lock:
            self.__pods[pod.metadata.uid] = pod

    def __forget_pod(self, pod):
        with self.__pods_lock:
            self.__pods.pop(pod.metadata.uid, None)

    def __process_event(self, event):
        event_type = event["type"]

        if event_type == "DELETED":
            pod = event["object"]
            logging.debug(f"Forgetting deleted Pod {pod.metadata.namespace}/{pod.metadata.name}")

            self.__forget_pod(pod)

        elif event_type in ("ADDED", "MODIFIED"):
            pod = event["object"]
            logging.debug(f"Remembering Pod {pod.metadata.namespace}/{pod.metadata.name}")

            self.__remember_pod(pod)
            self.__ready.set()

        else:
            logging.debug(f"Skipping {event_type} event")

    def __watch_pods(self, selector):
        logging.info("Subscribing to Pods from all namespaces")

        while True:
            try:
                watcher = watch.Watch()

                for event in watcher.stream(
                    self.kube_api.list_pod_for_all_namespaces,
                    label_selector=self.__selector_dict_to_raw(selector),
                ):
                    self.__process_event(event)

            except Exception as e:
                logging.error(e)

                logging.info(f"Resubscribing in {self.WATCH_RETRY_DELAY}s")
                time.sleep(self.WATCH_RETRY_DELAY)

    def subscribe(self, selector):
        logging.info("Starting Pods subscription")

        thread = threading.Thread(target=self.__watch_pods, args=(selector,), daemon=True)
        thread.start()

    def wait_until_ready(self, timeout=None):
        self.__ready.wait(timeout=timeout)

    def get_all_suitable(self):
        logging.debug("Iterating through remembered pods")

        with self.__pods_lock:
            pods = list(self.__pods.values())

        for pod in pods:
            logging.debug(f"Checking pod {pod.metadata.namespace}/{pod.metadata.name}")

            if (
                self.__pod_process_empty_labels(pod)
                and self.__pod_process_phase(pod)
                and self.__pod_process_limits(pod)
            ):
                yield pod
