# Actions

```
metadata:
  labels:
    ...
  annotations:
    ...
    kube-viktor.agrrh.com/handle-action: CHANGEME
```

### `log`

Just write action to logs.

### `evict`

Create [Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/api-eviction/) object, which causes the API server to terminate the Pod.

Evictions respect [Disruption Budget](https://kubernetes.io/docs/tasks/run-application/configure-pdb/), if specified.

### `delete`

Deletes the Pod.

Warning, multiple Pods could be deleted at once.
