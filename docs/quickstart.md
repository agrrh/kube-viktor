# kube-viktor quickstart

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
${EDITOR} deployment/deployment.yml
kubectl apply -f deployment/
```
