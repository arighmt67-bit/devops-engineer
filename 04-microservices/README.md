# 🧩 Belajar Membangun Arsitektur Microservices — Dicoding Showcase

[![Dicoding](https://img.shields.io/badge/Dicoding-Course%20Completed-blue?style=flat-square&logo=dicoding)](https://www.dicoding.com/)
[![Docker](https://img.shields.io/badge/Container-Docker%20%26%20Compose-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-326CE5?style=flat-square&logo=kubernetes)](https://kubernetes.io/)
[![RabbitMQ](https://img.shields.io/badge/Message%20Broker-RabbitMQ-FF6600?style=flat-square&logo=rabbitmq)](https://www.rabbitmq.com/)
[![GitHub Packages](https://img.shields.io/badge/Registry-GHCR-181717?style=flat-square&logo=github)](https://github.com/arighmt67-bit?tab=packages)

Repositori resmi showcase dan dokumentasi implementasi monorepo untuk seluruh tugas akhir/submission pada kelas **[Belajar Membangun Arsitektur Microservices (a433)](https://www.dicoding.com/academies/433)** di **Dicoding Indonesia**. Seluruh proyek disatukan secara terstruktur dalam branch default `main` untuk kemudahan navigasi, review teknis, dan portofolio engineering.

---

## 📑 Daftar Proyek Submission

| No | Proyek | Fokus Arsitektur & Teknologi | Direktori | Status GHCR / Deployment |
| :---: | :--- | :--- | :--- | :---: |
| **01** | **Deploy Item App dengan Docker Compose** | Multi-container application (Node.js Express + MongoDB) via Docker Compose | [`01-item-app-docker-compose/`](./01-item-app-docker-compose/) | [`ghcr.io/.../item-app:v1`](https://github.com/arighmt67-bit/a433-microservices/pkgs/container/item-app) |
| **02** | **Deploy Karsa Jobs dengan Kubernetes** | Multi-tier polyglot stack (Go backend + Vue.js frontend + MongoDB) via 11 K8s declarative manifests | [`02-karsajobs-kubernetes/`](./02-karsajobs-kubernetes/) | [`karsajobs`](https://github.com/arighmt67-bit/a433-microservices/pkgs/container/karsajobs) & [`karsajobs-ui`](https://github.com/arighmt67-bit/a433-microservices/pkgs/container/karsajobs-ui) |
| **03** | **Asynchronous Communication E-Commerce** | Event-driven microservices architecture menggunakan RabbitMQ message broker di Kubernetes | [`03-async-ecommerce-rabbitmq/`](./03-async-ecommerce-rabbitmq/) | [`order-service`](https://github.com/arighmt67-bit/a433-microservices/pkgs/container/order-service) & [`shipping-service`](https://github.com/arighmt67-bit/a433-microservices/pkgs/container/shipping-service) |

---

## 🏗️ Ringkasan Arsitektur per Submission

### 1. [Submission 1 — Item App (Docker Compose)](./01-item-app-docker-compose/)
* Mengemas aplikasi web monolitik Node.js menjadi container image berbasis `Dockerfile`.
* Otomatisasi proses build dan push image ke **GitHub Container Registry (GHCR)** via `build_push_image.sh`.
* Orkestrasi multi-container (`item-app` dan `item-db` MongoDB) via `docker-compose.yml` dengan restart policy `always` dan volume persistence `app-db`.

### 2. [Submission 2 — Karsa Jobs (Kubernetes Orchestration)](./02-karsajobs-kubernetes/)
* Arsitektur multi-tier microservices:
  - **Backend API**: Go standard library / REST API.
  - **Frontend UI**: Vue.js + Tailwind CSS.
  - **Database**: MongoDB dengan PersistentVolumeClaim (PVC).
* Total **11 manifest Kubernetes** declarative mencakup:
  - Secret & ConfigMap terpisah per tier.
  - Deployment controller dengan `readinessProbe` & `livenessProbe`.
  - Service Networking: `ClusterIP` untuk komunikasi internal database/backend dan `NodePort` untuk akses publik frontend.

### 3. [Submission 3 — E-Commerce Async Communication (RabbitMQ & K8s)](./03-async-ecommerce-rabbitmq/)
* Memisahkan proses pemesanan sinkron dari proses logistik pengiriman via **Event-Driven Architecture (EDA)**.
* **Order Service**: Menerima request order dari client dan mem-publish payload event pesanan ke exchange / antrean RabbitMQ (`amqp`).
* **Shipping Service**: Konsumen worker independen yang standby mendengarkan antrean RabbitMQ dan memproses notifikasi pengiriman.
* Seluruh komponen dideploy ke cluster Kubernetes menggunakan deklarasi manifest pada direktori `kubernetes/`.

---

## 🐳 Container Images di GitHub Packages (GHCR)

Semua container image bersifat **Public** dan telah diverifikasi dapat di-pull langsung tanpa kredensial:

```bash
# Proyek 1
docker pull ghcr.io/arighmt67-bit/item-app:v1

# Proyek 2
docker pull ghcr.io/arighmt67-bit/karsajobs:latest
docker pull ghcr.io/arighmt67-bit/karsajobs-ui:latest

# Proyek 3
docker pull ghcr.io/arighmt67-bit/order-service:latest
docker pull ghcr.io/arighmt67-bit/shipping-service:latest
```

---

## 👤 Author

**Ari Rahmat Romadhon**
- GitHub: [@arighmt67-bit](https://github.com/arighmt67-bit)
- Portfolio: [arighmt67-bit.github.io](https://arighmt67-bit.github.io/)
