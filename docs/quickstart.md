# Quickstart

### Running locally

```
APP_KUBECONFIG_FILE=~/.kube/my-config.yml \
APP_PROM_ADDRESS=http://localhost:12345/api/v1/query \
APP_RUN_ONCE=yes \
APP_HANDLE_ACTION=log \
  python3 kube-viktor/main.py
```

### Running inside cluster

```
${EDITOR} deployment/kubernetes/deployment.yml
kubectl apply -f deployment/kubernetes
```

### Preparing payload

In this case, you run handle action `evict` when Pod reach `0.8` of memory limit:

```
metadata:
  labels:
    ...
    kube-viktor.agrrh.com/enabled: "true"
  annotations:
    ...
    kube-viktor.agrrh.com/handle-action: evict
    kube-viktor.agrrh.com/metric-threshold: "0.8"
```

In case you're dealing with Deployment, modify `spec.template.metadata` instead.

Also, read more about possible [handle actions](./handle-actions.md).
