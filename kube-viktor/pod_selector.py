import logging


class PodSelector(object):
    def __init__(self, kube_api):
        super(PodSelector, self).__init__()

        self.kube_api = kube_api

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

    def get_all_suitable(self, selector):
        logging.debug("Getting all pods from all namespaces")
        pods = self.kube_api.list_pod_for_all_namespaces(
            watch=False, label_selector=self.__selector_dict_to_raw(selector)
        )

        logging.debug("Iterating through pods list")
        for pod in pods.items:
            logging.debug(f"Checking pod {pod.metadata.namespace}/{pod.metadata.name}")

            if (
                self.__pod_process_empty_labels(pod)
                and self.__pod_process_phase(pod)
                and self.__pod_process_limits(pod)
            ):
                yield pod
