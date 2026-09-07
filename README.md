# DevOps Engineer Portfolio Showcase

Repositori ini merupakan showcase terpadu dan monorepo portofolio untuk seluruh submission proyek pada **Dicoding DevOps Learning Path**, yang mencakup 4 pilar utama rekayasa infrastruktur:
1. **Computer Networking** (Jaringan Komputer & Reverse Proxy)
2. **Linux System Administration** (Otomasi Bash & Hardening Server SSH)
3. **CI/CD Automation Pipeline** (Jenkins Scripted Pipeline & Container Agent)
4. **Microservices Architecture** (Containerization, Kubernetes Cluster, & Asynchronous EDA RabbitMQ)

---

## 🗺️ Learning Path & Project Directory

```text
devops-engineer/
├── 01-computer-networking/             # Dasar Jaringan Komputer & Web Server
├── 02-linux-system-admin/              # Administrasi Sistem Linux & Keamanan Server
│   ├── 01-shell-scripting/             # Otomasi Bash Scripting & Backup
│   └── 02-ssh-server-configuration/    # Hardening SSH Server, Audit Log, & Web Report
├── 03-cicd-pipeline/                   # Automasi CI/CD Pipeline dengan Jenkins
│   ├── Jenkinsfile                     # Pipeline CI/CD Proyek Akhir (Build -> Test -> Approval -> Deploy)
│   ├── jenkins/                        # Pipeline CI Proyek Pertama
│   └── submission-artifacts/           # Log eksekusi, status container, & screenshot verifikasi
└── 04-microservices/                   # Arsitektur Aplikasi Microservices
    ├── 01-item-app-docker-compose/     # Multi-container Node.js + MongoDB via Docker Compose
    ├── 02-karsajobs-kubernetes/        # Multi-service Go & Vue.js orkestrasi di Kubernetes
    └── 03-async-ecommerce-rabbitmq/    # Asynchronous Event-Driven Architecture dengan RabbitMQ
```

---

## 🛠️ Ringkasan Modul & Kompetensi

### 1. [01-computer-networking](./01-computer-networking) — Jaringan Komputer & Web Server
* **Teknologi**: Node.js, Express, Nginx, Apache2, Linux Networking.
* **Fokus Proyek**:
  * Pembangunan REST API Node.js/Express dengan implementasi reverse proxy ganda (NGINX & Apache2).
  * Konfigurasi port forwarding, IP routing, serta proteksi keamanan web server (rate limiting & header forwarding `X-Real-IP`, `X-Forwarded-For`).

### 2. [02-linux-system-admin](./02-linux-system-admin) — Linux System Administration
* **Teknologi**: Bash Shell Scripting, Cron, OpenSSH Server, GPG Encryption, HTML5.
* **Fokus Proyek**:
  * **Shell Scripting Automation**: Skrip Bash otomatis untuk audit sistem, backup direktori dengan timestamping, dan scheduling via Cron.
  * **SSH Server Hardening**: Modifikasi port SSH non-standar, disable root login & password authentication, enforcement Public-Key authentication, serta parsing log autentikasi SSH ke format JSON dan dashboard HTML.

### 3. [03-cicd-pipeline](./03-cicd-pipeline) — Continuous Integration & Continuous Delivery
* **Teknologi**: Jenkins (Scripted & Declarative Pipeline), Docker-in-Docker (DinD), Node.js LTS, Jest, Nginx.
* **Fokus Proyek**:
  * **Proyek Pertama (CI)**: Pipeline deklaratif otomatisasi install dependencies, unit testing Jest, dan deliver preview application.
  * **Proyek Akhir (CI/CD)**: Pipeline Scripted Jenkinsfile terpadu dengan tahapan:
    1. **Build**: Build React app di dalam container isolated `node:lts-buster-slim`.
    2. **Test**: Eksekusi pengujian otomatis Jest.
    3. **Manual Approval**: Interactive gate approval sebelum proses deployment.
    4. **Deploy**: Penyebaran otomatis artefak static site ke web server container Nginx di port 80.
    5. **Artifact Archival**: Pencatatan log eksekusi otomatis ke `log.txt` sebagai build artifact.

### 4. [04-microservices](./04-microservices) — Arsitektur Microservices Modern
* **Teknologi**: Docker, Docker Compose, Kubernetes (K8s), Go, Vue.js, Node.js, MongoDB, RabbitMQ.
* **Fokus Proyek**:
  * **01 - Docker Compose**: Orkestrasi multi-container `item-app` (aplikasi web Node.js terhubung ke MongoDB database) dengan custom bridge network dan volume persistence.
  * **02 - Kubernetes Cluster**: Deployment arsitektur decoupled (Backend Golang + Frontend Vue.js + MongoDB StatefulSet) menggunakan K8s Deployment, ClusterIP/NodePort Services, ConfigMaps, PersistentVolumes, dan Secrets.
  * **03 - Asynchronous EDA**: Implementasi Event-Driven Architecture menggunakan message broker RabbitMQ yang menghubungkan `order-service` dan `shipping-service` secara asynchronous dan decoupled.

---

## 👤 Author

* **Nama**: Ari Rahmat Romadhon
* **GitHub**: [@arighmt67-bit](https://github.com/arighmt67-bit)
* **LinkedIn**: [Ari Rahmat Romadhon](https://www.linkedin.com/in/arirahmatr/)
* **Platform**: Dicoding Indonesia - DevOps Learning Path
