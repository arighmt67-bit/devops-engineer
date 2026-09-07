#!/bin/bash
# =============================================================================
# build_push_image_karsajobs.sh
# Script untuk build Docker image backend (Karsa Jobs) lalu push ke
# GitHub Container Registry / GHCR (menerapkan Saran ke-2).
# Tahapan dijalankan BERURUTAN: build -> login -> push.
# =============================================================================

# Hentikan eksekusi bila ada perintah yang gagal (biar tidak lanjut push image rusak)
set -e

# Konfigurasi variabel image (ganti USERNAME bila perlu)
USERNAME="arighmt67-bit"                       # username GitHub (owner package GHCR)
IMAGE="ghcr.io/${USERNAME}/karsajobs:latest"   # nama image lengkap sesuai kriteria

# 1) BUILD: membuat Docker image dari Dockerfile di direktori saat ini (.)
#    -t memberi tag/nama pada image sesuai ketentuan <username>/karsajobs:latest
docker build -t "${IMAGE}" .

# 2) LOGIN ke GHCR menggunakan Personal Access Token (PAT) yang disimpan di
#    environment variable PASSWORD_GHCR agar password tidak tertulis di script.
#    Jalankan dahulu: export PASSWORD_GHCR=<PAT_write:packages_Anda>
echo "${PASSWORD_GHCR}" | docker login ghcr.io -u "${USERNAME}" --password-stdin

# 3) PUSH: mengunggah image yang sudah di-build ke GHCR
docker push "${IMAGE}"

echo "Selesai: ${IMAGE} berhasil di-push ke GHCR."
