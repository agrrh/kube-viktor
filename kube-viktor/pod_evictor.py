import logging

from kubernetes import client


class PodEvictor(object):
    POSSIBLE_ACTIONS = ("log", "evict", "delete")
    ANNOTATION_ACTION_KEY = "kube-viktor.agrrh.com/handle-action"

    def __init__(self, kube_api=None, default_action="log"):
        super(PodEvictor, self).__init__()

        self.kube_api = kube_api

        if default_action not in self.POSSIBLE_ACTIONS:
            raise TypeError(f'Action must one of {self.POSSIBLE_ACTIONS}, got "{default_action}" instead')

        self.default_action = default_action

    def __select_action(self, pod):
        override_action = pod.metadata.annotations.get(self.ANNOTATION_ACTION_KEY)

        if not override_action:
            return self.default_action

        override_action_valid = override_action in self.POSSIBLE_ACTIONS

        if override_action_valid:
            logging.info(f'Annotation overrides handle action, "{self.default_action}" becomes "{override_action}"')
            action = override_action
        else:
            logging.error(f'Not overriding handle action, value unknown: "{override_action}"')
            action = self.default_action

        return action

    def handle(self, pod):
        action = self.__select_action(pod)

        if action == "log":
            logging.warning(f"Performing LOG action: {pod.metadata.namespace}/{pod.metadata.name}")

        elif action == "evict":
            logging.warning(f"Performing EVICT action: {pod.metadata.namespace}/{pod.metadata.name}")

            try:
                self.kube_api.create_namespaced_pod_eviction(
                    name=pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    body=client.V1Eviction(
                        metadata=client.V1ObjectMeta(
                            name=pod.metadata.name,
                            namespace=pod.metadata.namespace,
                        )
                    ),
                )
            except Exception as e:
                logging.error(e)

        elif action == "delete":
            logging.warning(f"Performing DELETE action: {pod.metadata.namespace}/{pod.metadata.name}")

            try:
                self.kube_api.delete_namespaced_pod(name=pod.metadata.name, namespace=pod.metadata.namespace)
            except Exception as e:
                logging.error(e)
