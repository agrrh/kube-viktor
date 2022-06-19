import os
import json
import logging

from controller import Controller


if __name__ == "__main__":
    # TODO Use argparse/fire/... lib here
    run_once = os.environ.get("APP_RUN_ONCE", False)
    loop_delay = int(os.environ.get("APP_LOOP_DELAY", "15"))
    kubeconfig_file = os.environ.get("APP_KUBECONFIG_FILE", "")
    labels_selector = json.loads(os.environ.get("APP_LABELS_SELECTOR", "{}"))
    handle_action = os.environ.get("APP_HANDLE_ACTION", "log")

    prom_address = os.environ.get("APP_PROM_ADDRESS", "http://prometheus.metrics.svc:9090/api/v1/query")
    prom_query = os.environ.get("APP_PROM_QUERY", False)
    prom_query_threshold = float(os.environ.get("APP_PROM_QUERY_THRESHOLD", "0.8"))

    log_verbose = os.environ.get("APP_LOG_VERBOSE", False)
    log_debug = os.environ.get("APP_LOG_DEBUG", False)

    if log_debug:
        log_level = logging.DEBUG
    elif log_verbose:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level)

    controller = Controller(
        kubeconfig_file=kubeconfig_file,
        labels_selector=labels_selector,
        handle_action=handle_action,
        prom_address=prom_address,
        prom_query=prom_query,
        prom_query_threshold=prom_query_threshold,
    )

    controller.run_loop(run_once=run_once, loop_delay=loop_delay)
