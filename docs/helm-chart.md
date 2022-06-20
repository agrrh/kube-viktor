# Helm chart

### How to update

```
cd deployment/helm

helm repo index \
  --url https://agrrh.github.io/kube-viktor/deployment/ \
  --merge index.yaml \
  ./
```

### Usage

```
helm repo add kube-viktor https://agrrh.github.io/kube-viktor/deployment/
```
