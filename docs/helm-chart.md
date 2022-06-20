# Helm chart

### How to update

```
cd deployment

# new
helm repo index \
  --url https://agrrh.github.io/kube-viktor/deployment/helm/ \
  ./helm

# update
helm repo index \
  --url https://agrrh.github.io/kube-viktor/deployment/helm/ \
  --merge index.yaml \
  ./helm

mv -f ./helm/index.yaml ./
```

### Usage

```
helm repo add kube-viktor https://agrrh.github.io/kube-viktor/deployment/
```
