# Forum API Kubernetes Orchestration and SRE Probes

Modul ini mengorkestrasi container backend `forum-api` (dipull dari OCI registry publik `ghcr.io/arighmt67-bit/forum-api:1.0.0`) beserta stateful database PostgreSQL ke dalam cluster Kubernetes.

## Fitur dan Standar SRE yang Diterapkan
1. **Separation of Concerns**: Konfigurasi non-sensitif diisolasi di `ConfigMap`, kredensial rahasia dienkripsi di `Secret`.
2. **High Availability**: Deployment backend disetel dengan `replicas: 2` untuk failover redundancy.
3. **Resource Quotas (Anti-OOM)**: Alokasi `requests` dan `limits` CPU serta RAM ketat untuk mencegah pod starvation.
4. **Self-Healing via Health Probes**:
   - `livenessProbe`: Memeriksa kelayakan proses via endpoint `/`. Jika container freeze atau deadlock, kubelet me-restart pod secara otomatis.
   - `readinessProbe`: Menahan trafik ke pod sampai koneksi database Postgres terjalin sempurna.

## Panduan Uji Lokal via Colima / Minikube
```bash
# 1. Jalankan k8s lokal
colima start --cpu 4 --memory 5 --kubernetes

# 2. Terapkan seluruh manifest secara berurutan
kubectl apply -f 01-config-secret.yaml
kubectl apply -f 02-postgres.yaml
kubectl apply -f 03-forum-api.yaml

# 3. Verifikasi status pod
kubectl get pods -l tier=backend
kubectl get services
```
