{{/*
Expand the name of the chart.
*/}}
{{- define "spiderkeeper.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "spiderkeeper.fullname" -}}
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
{{- define "spiderkeeper.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "spiderkeeper.labels" -}}
helm.sh/chart: {{ include "spiderkeeper.chart" . }}
{{ include "spiderkeeper.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "spiderkeeper.selectorLabels" -}}
app.kubernetes.io/name: {{ include "spiderkeeper.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "spiderkeeper.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "spiderkeeper.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "spiderkeeper-executor.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "spiderkeeper.fullname" .) .Values.executor.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.executor.serviceAccount.name }}
{{- end }}
{{- end }}


{{/*
Create a default fully qualified default backend name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "spiderkeeper-web.fullname" -}}
{{- printf "%s-%s" (include "spiderkeeper.fullname" .) .Values.web.name | trunc 63 | trimSuffix "-" -}}
{{- end -}}


{{/*
Create the name of the configmap to use
*/}}
{{- define "spiderkeeper-web.configMapName" -}}
{{- default "default" .Values.web.configMap.name }}
{{- end }}

{{/*
Create a default fully qualified default backend name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "spiderkeeper-server.fullname" -}}
{{- printf "%s-%s" (include "spiderkeeper.fullname" .) .Values.server.name | trunc 63 | trimSuffix "-" -}}
{{- end -}}


{{/*
Create the name of the configmap to use
*/}}
{{- define "spiderkeeper-server.configMapName" -}}
{{- default "default" .Values.server.configMap.name }}
{{- end }}

{{/*
Create a default fully qualified default backend name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "spiderkeeper-scheduler.fullname" -}}
{{- printf "%s-%s" (include "spiderkeeper.fullname" .) .Values.scheduler.name | trunc 63 | trimSuffix "-" -}}
{{- end -}}


{{/*
Create the name of the configmap to use
*/}}
{{- define "spiderkeeper-scheduler.configMapName" -}}
{{- default "default" .Values.scheduler.configMap.name }}
{{- end }}


{{/*
Create a default fully qualified default backend name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "spiderkeeper-forwarder.fullname" -}}
{{- printf "%s-%s" (include "spiderkeeper.fullname" .) .Values.forwarder.name | trunc 63 | trimSuffix "-" -}}
{{- end -}}


{{/*
Create the name of the configmap to use
*/}}
{{- define "spiderkeeper-forwarder.configMapName" -}}
{{- default "default" .Values.forwarder.configMap.name }}
{{- end }}

{{/*
Create a default fully qualified default backend name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "spiderkeeper-executor.fullname" -}}
{{- printf "%s-%s" (include "spiderkeeper.fullname" .) .Values.executor.name | trunc 63 | trimSuffix "-" -}}
{{- end -}}


{{/*
Create the name of the configmap to use
*/}}
{{- define "spiderkeeper-executor.configMapName" -}}
{{- default "default" .Values.executor.configMap.name }}
{{- end }}






