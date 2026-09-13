# Runbook: Incident Response & Disaster Recovery (DRP)

## 1. Klasifikasi Insiden
- SEV-1 (Kritis): Core service down. RTO < 30 menit, RPO < 5 menit.
- SEV-2 (Mayor): Fitur parsial degraded. RTO < 2 jam.

## 2. Prosedur Recovery
1. Identifikasi & Triage via Prometheus/Grafana.
2. Rollback otomatis ke tag rilis sebelumnya via GitHub Actions.
3. Restore database dari automated snapshot terverifikasi.
