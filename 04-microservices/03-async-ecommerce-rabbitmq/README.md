# ⚡ Proyek 3: Implementasi Asynchronous Communication pada E-Commerce App

Proyek Akhir dari kelas **Belajar Membangun Arsitektur Microservices** (Dicoding). Mengimplementasikan arsitektur asynchronous event-driven microservices menggunakan RabbitMQ message broker antara `order-service` (publisher) dan `shipping-service` (consumer) di Kubernetes.

---

## 📋 Struktur Komponen

- `order-service/` : Node.js Express service untuk menerima pesanan (`POST /order`) dan menerbitkan event ke antrean RabbitMQ.
- `shipping-service/` : Node.js worker service yang mendengarkan antrean RabbitMQ dan memproses pengiriman pesanan secara asinkron.
- `kubernetes/` : Manifest deployment dan service Kubernetes:
  - `rabbitmq.yaml` : Deployment RabbitMQ broker + ClusterIP Service.
  - `order-service.yaml` : Deployment order service (image GHCR) + Service.
  - `shipping-service.yaml` : Deployment shipping consumer service (image GHCR).

---

## 🐳 Container Images di GitHub Packages (GHCR)

Kedua image terverifikasi **Public** di GitHub Packages:
```bash
docker pull ghcr.io/arighmt67-bit/order-service:latest
docker pull ghcr.io/arighmt67-bit/shipping-service:latest
```

---

## 🚀 Panduan Deployment ke Kubernetes

Terapkan manifest secara berurutan:

```bash
# 1. Jalankan RabbitMQ Message Broker
kubectl apply -f kubernetes/rabbitmq.yaml

# 2. Jalankan Publisher (Order Service)
kubectl apply -f kubernetes/order-service.yaml

# 3. Jalankan Consumer (Shipping Service)
kubectl apply -f kubernetes/shipping-service.yaml
```

Verifikasi alur komunikasi asinkron via log:
```bash
kubectl logs -l app=shipping-service -f
```
