#!/bin/bash
# =============================================================================
# build_push_image_karsajobs_ui.sh
# Script untuk build Docker image frontend (Karsa Jobs UI) lalu push ke
# GitHub Container Registry / GHCR (menerapkan Saran ke-2).
# Tahapan dijalankan BERURUTAN: build -> login -> push.
# =============================================================================

# Hentikan eksekusi bila ada perintah yang gagal
set -e

# Konfigurasi variabel image
USERNAME="arighmt67-bit"                          # username GitHub (owner package GHCR)
IMAGE="ghcr.io/${USERNAME}/karsajobs-ui:latest"   # nama image lengkap sesuai kriteria

# 1) BUILD: membuat Docker image frontend dari Dockerfile di direktori saat ini (.)
docker build -t "${IMAGE}" .

# 2) LOGIN ke GHCR memakai PAT dari environment variable PASSWORD_GHCR
#    Jalankan dahulu: export PASSWORD_GHCR=<PAT_write:packages_Anda>
echo "${PASSWORD_GHCR}" | docker login ghcr.io -u "${USERNAME}" --password-stdin

# 3) PUSH image frontend ke GHCR
docker push "${IMAGE}"

echo "Selesai: ${IMAGE} berhasil di-push ke GHCR."
