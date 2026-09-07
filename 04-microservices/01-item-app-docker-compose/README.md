# 📦 Proyek 1: Deploy Aplikasi Item App dengan Docker Compose

Proyek Pertama dari kelas **Belajar Membangun Arsitektur Microservices** (Dicoding). Mengimplementasikan kontainerisasi aplikasi Node.js (Item App) dan database MongoDB menggunakan Docker dan Docker Compose, serta mempublikasikan image ke GitHub Packages (GHCR).

---

## 📋 Berkas Utama

- `Dockerfile` : Blueprint container image untuk aplikasi Node.js.
- `docker-compose.yml` : Konfigurasi orkestrasi multi-container (`item-app` + `item-db` MongoDB) dengan restart policy `always` dan volume persistent `app-db`.
- `build_push_image.sh` : Bash automation script untuk build dan push container image ke GHCR.
- `link.txt` : Tautan publik container image di GitHub Packages (GHCR).

---

## 🐳 Container Image di GitHub Packages (GHCR)

Image publik siap pakai (verified tanpa login):
```bash
docker pull ghcr.io/arighmt67-bit/item-app:v1
```

---

## 🚀 Cara Menjalankan

Jalankan seluruh stack menggunakan Docker Compose:

```bash
docker-compose up -d
```
Akses aplikasi di browser pada port `80`: `http://localhost:80`
