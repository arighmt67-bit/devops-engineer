# ☸️ Proyek 2: Deploy Aplikasi Karsa Jobs dengan Kubernetes

Proyek Kedua dari kelas **Belajar Membangun Arsitektur Microservices** (Dicoding). Mengimplementasikan orkestrasi microservices multi-tier (Go backend + Vue.js frontend + MongoDB database) ke dalam cluster Kubernetes menggunakan 11 manifest declarative.

---

## 📋 Struktur Komponen

- `backend/` : Source code Go REST API (`karsajobs`), Dockerfile, dan script build-push image GHCR.
- `frontend/` : Source code Vue.js SPA (`karsajobs-ui`), Tailwind CSS, Dockerfile, dan script build-push image GHCR.
- `kubernetes/` : 11 manifest Kubernetes lengkap:
  - `mongodb/` : Secret, ConfigMap, PVC, Deployment, dan Service untuk MongoDB.
  - `backend/` : Secret, ConfigMap, Deployment, dan Service untuk backend API.
  - `frontend/` : ConfigMap, Deployment, dan Service (NodePort) untuk web UI.

---

## 🐳 Container Images di GitHub Packages (GHCR)

Kedua image terverifikasi **Public** dan dapat ditarik langsung:
```bash
docker pull ghcr.io/arighmt67-bit/karsajobs:latest
docker pull ghcr.io/arighmt67-bit/karsajobs-ui:latest
```

---

## 🚀 Panduan Deployment ke Kubernetes

Terapkan seluruh manifest sesuai urutan dependensi:

```bash
# 1. Terapkan database MongoDB
kubectl apply -f kubernetes/mongodb/

# 2. Terapkan Backend API Go
kubectl apply -f kubernetes/backend/

# 3. Terapkan Frontend Web UI
kubectl apply -f kubernetes/frontend/
```

Verifikasi status seluruh pod:
```bash
kubectl get pods -l app=karsajobs
```
