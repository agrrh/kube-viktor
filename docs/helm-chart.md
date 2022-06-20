# Helm chart

### How to update

```
cd deployment

# new
helm repo index \
  --url https://agrrh.github.io/kube-viktor/deployment/ \
  ./helm

# update
helm repo index \
  --url https://agrrh.github.io/kube-viktor/deployment/ \
  --merge index.yaml \
  ./helm

mv ./helm/index.yaml ./
```

### Usage

```
helm repo add kube-viktor https://agrrh.github.io/kube-viktor/deployment/
```
