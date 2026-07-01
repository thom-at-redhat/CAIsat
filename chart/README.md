# CAIsat Helm Chart

<!-- Assisted by: cursor, claude -->

Deploys frontend, enhancement/detection backends, SwinIR/YOLO/Sentinel2 InferenceServices, SeaweedFS S3 storage, and optional pipelines.

## Key values

| Value | Default | Description |
| ----- | ------- | ----------- |
| `computeProfile.name` | `cpu` | `cpu`, `t4`, `l40s`, or `hopper` |
| `computeProfile.gpuAvailable` | `false` | Set `true` when GPU nodes are scheduled |
| `kserve.preferBinary` | `false` | `KSERVE_PREFER_BINARY` on both backends; keep `false` until MLServer binary infer passes |
| `networkPolicy.enabled` | `false` | Enable backend NetworkPolicy (Phase 19) |
| `model.deploy` | `true` | SwinIR InferenceService |
| `detection.deploy` | `true` | YOLOv8-OBB InferenceService |
| `seaweedfs.enabled` | `true` | SeaweedFS `weed server` S3 gateway (port 7480) |
| `seaweedfs.image.repository` | `docker.io/chrislusf/seaweedfs` | Public OCI image; mirror to Quay if cluster lacks docker.io |
| `seaweedfs.image.tag` | `4.36` | Pinned SeaweedFS release tag |
| `seaweedfs.seed.bucketName` | `satellite-images` | S3 bucket seeded post-install |
| `seaweedfs.seed.image` | `openshift/python:3.12-ubi9` | Seed Job runner; DS notebook only when workbenches ImageStreams exist |
| `seaweedfs.storage.storageClassName` | `gp3-csi` | PVC storage class for `/data` volume |

## SeaweedFS storage

SeaweedFS runs in single-process **`weed server`** mode: master, volume, and S3 gateway on one pod. The S3 API listens on **port 7480** (ClusterIP service `<release>-seaweedfs.<namespace>.svc.cluster.local:7480`). No web UI Route is deployed.

Credentials live in `<release>-seaweedfs-credentials`; DSPA and change-detection backends reference the same keys. Override the storage class when your cluster default differs:

```bash
helm upgrade --install caisat ./chart -n <namespace> \
  --set seaweedfs.storage.storageClassName=<your-storage-class>
```

## Pull secrets

CAIsat images live in a **private** Quay repository (`quay.io/thom_at_redhat/caisat`). A robot-account pull secret is required.

### Two-secret pattern

| Scope | Registry path | Secret name | Namespace(s) | Notes |
| ----- | ------------- | ----------- | ------------ | ----- |
| CAIsat workloads + model OCI | `quay.io/thom_at_redhat` | `quay-pull-secret` | `caisat` (or release ns) | Robot account; linked to `default` SA |
| RHOAI operator / FBC catalog | `quay.io/rhoai` | `rhoai-quay-pull` | `openshift-marketplace` | Only needed for pre-GA (ea) catalogs; unset for GA (public `redhat-operators`) |

**Never reuse the CAIsat robot secret for RHOAI catalog pulls** (different org, different permissions).

### Create the CAIsat pull secret

```bash
oc create secret docker-registry quay-pull-secret \
  --docker-server=quay.io \
  --docker-username='<robot-name>' \
  --docker-password='<robot-token>' \
  -n <namespace>
oc secrets link default quay-pull-secret --for=pull -n <namespace>
```

The `oc secrets link` step ensures KServe model-controller can pull OCI model images via the `default` SA.

### RHOAI ea catalog secret (pre-GA only)

```bash
oc create secret docker-registry rhoai-quay-pull \
  --docker-server=quay.io \
  --docker-username='<rhoai-robot-name>' \
  --docker-password='<rhoai-robot-token>' \
  -n openshift-marketplace
```

Then reference it on the CatalogSource SA (OLM does not propagate `spec.secrets` to pods on OCP 4.22+):

```bash
oc patch sa <catalog-sa> -n openshift-marketplace \
  --type=json -p '[{"op":"add","path":"/imagePullSecrets/-","value":{"name":"rhoai-quay-pull"}}]'
```

## Install

```bash
helm template test ./chart
helm upgrade --install caisat ./chart -n <namespace>
```

GPU profile example:

```bash
helm upgrade --install caisat ./chart -n <namespace> \
  --set computeProfile.name=t4 \
  --set computeProfile.gpuAvailable=true
```

See root [`README.md`](../README.md) for full deployment guide.
