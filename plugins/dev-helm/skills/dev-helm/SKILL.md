---
name: dev-helm
description: Create or modify Helm charts for Kubernetes deployments with proper templating, values, and best practices. Use when building or updating Helm charts.
argument-hint: "[chart-name-or-action]"
---

# Helm Chart Development

Create or update Helm chart for: **$ARGUMENTS**

## Process

1. **Scaffold chart** — `helm create <name>` or modify existing
2. **Design values.yaml** — sensible defaults, documented overrides
3. **Write templates** — Deployment, Service, Ingress, ConfigMap, etc.
4. **Add helpers** — `_helpers.tpl` for reusable template functions
5. **Test** — `helm template`, `helm lint`, `helm test`

## Chart Structure

```
charts/<name>/
├── Chart.yaml                 # Chart metadata, dependencies
├── values.yaml                # Default configuration values
├── values-dev.yaml            # Dev environment overrides
├── values-staging.yaml        # Staging overrides
├── values-prod.yaml           # Production overrides
├── templates/
│   ├── _helpers.tpl           # Template helpers (labels, names)
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml               # Horizontal Pod Autoscaler
│   ├── pdb.yaml               # Pod Disruption Budget
│   ├── serviceaccount.yaml
│   ├── servicemonitor.yaml    # Prometheus ServiceMonitor
│   └── tests/
│       └── test-connection.yaml
└── README.md
```

## values.yaml — Design Principles

```yaml
# values.yaml — sensible defaults, everything overridable

replicaCount: 2

image:
  repository: ghcr.io/org/app
  tag: ""                       # Overridden by CI/CD (defaults to Chart.appVersion)
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8080

ingress:
  enabled: false
  className: nginx
  annotations: {}
  hosts:
    - host: app.example.com
      paths:
        - path: /
          pathType: Prefix
  tls: []

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

env: {}                         # Plain env vars: KEY: value
envFrom: []                     # ConfigMap/Secret refs

probes:
  liveness:
    path: /health
    initialDelaySeconds: 10
    periodSeconds: 10
  readiness:
    path: /ready
    initialDelaySeconds: 5
    periodSeconds: 5

podDisruptionBudget:
  enabled: true
  minAvailable: 1

serviceMonitor:
  enabled: false
  path: /metrics
  interval: 30s
```

## Template Patterns

### _helpers.tpl
```yaml
{{- define "app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "app.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "app.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/name: {{ include "app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "app.fullname" . }}
  labels:
    {{- include "app.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels:
        {{- include "app.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "app.fullname" . }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.service.port }}
              protocol: TCP
          livenessProbe:
            httpGet:
              path: {{ .Values.probes.liveness.path }}
              port: {{ .Values.service.port }}
            initialDelaySeconds: {{ .Values.probes.liveness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.liveness.periodSeconds }}
          readinessProbe:
            httpGet:
              path: {{ .Values.probes.readiness.path }}
              port: {{ .Values.service.port }}
            initialDelaySeconds: {{ .Values.probes.readiness.initialDelaySeconds }}
            periodSeconds: {{ .Values.probes.readiness.periodSeconds }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- with .Values.env }}
          env:
            {{- range $key, $value := . }}
            - name: {{ $key }}
              value: {{ $value | quote }}
            {{- end }}
          {{- end }}
          {{- with .Values.envFrom }}
          envFrom:
            {{- toYaml . | nindent 12 }}
          {{- end }}
```

## Validation & Testing

```bash
# Lint chart
helm lint charts/<name>

# Render templates locally (dry run)
helm template my-release charts/<name> -f values-dev.yaml

# Validate against cluster
helm install my-release charts/<name> --dry-run --debug

# Run chart tests
helm test my-release

# Diff before upgrade
helm diff upgrade my-release charts/<name> -f values-prod.yaml
```

## Rules
- Every value in `values.yaml` must have a sensible default
- Use `_helpers.tpl` for ALL labels and names (DRY)
- Always include resource requests AND limits
- Always include liveness and readiness probes
- Use `securityContext` — `runAsNonRoot: true` minimum
- ConfigMap changes should trigger pod restart (use `checksum/config` annotation)
- Pod Disruption Budget for production workloads
- Image tag should default to `Chart.appVersion`, overridden by CI
- Use `helm lint` and `helm template` in CI before deploying
