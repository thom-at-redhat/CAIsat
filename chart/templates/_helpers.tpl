{{/*
Expand the name of the chart.
*/}}
{{- define "caisat.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "caisat.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "caisat.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "caisat.labels" -}}
helm.sh/chart: {{ include "caisat.chart" . }}
{{ include "caisat.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "caisat.selectorLabels" -}}
app.kubernetes.io/name: {{ include "caisat.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Hybrid InferenceService model resources: cpu/memory from values; optional conditional nvidia.com/gpu.
Pass dict with root, resources, and gpu (bool). Do not blind toYaml on full resources — drops GPU conditional.
*/}}
{{- define "caisat.inferenceModelResources" -}}
{{- $root := index . "root" -}}
{{- $resources := index . "resources" -}}
{{- $gpu := index . "gpu" | default false -}}
limits:
  cpu: {{ $resources.limits.cpu | quote }}
  memory: {{ $resources.limits.memory | quote }}
  {{- if and $gpu (ne $root.Values.computeProfile.name "cpu") $root.Values.computeProfile.gpuAvailable }}
  nvidia.com/gpu: "1"
  {{- end }}
requests:
  cpu: {{ $resources.requests.cpu | quote }}
  memory: {{ $resources.requests.memory | quote }}
  {{- if and $gpu (ne $root.Values.computeProfile.name "cpu") $root.Values.computeProfile.gpuAvailable }}
  nvidia.com/gpu: "1"
  {{- end }}
{{- end }}

{{/*
GPU node tolerations for InferenceService predictors when gpuAvailable is true.
*/}}
{{- define "caisat.gpuTolerations" -}}
{{- if and (ne .Values.computeProfile.name "cpu") .Values.computeProfile.gpuAvailable }}
tolerations:
{{- toYaml .Values.computeProfile.gpuTolerations | nindent 2 }}
{{- end }}
{{- end }}

{{/*
Model endpoint URL
*/}}
{{- define "caisat.modelEndpoint" -}}
{{- $namespace := .Values.model.namespace | default .Release.Namespace -}}
{{- $serviceName := .Values.model.serviceName | default (printf "%s-predictor" .Values.model.name) -}}
http://{{ $serviceName }}.{{ $namespace }}.svc.cluster.local:{{ .Values.model.port }}/v2/models/{{ .Values.model.name }}/infer
{{- end }}
