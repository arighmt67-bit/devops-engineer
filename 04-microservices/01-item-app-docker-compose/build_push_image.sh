#!/bin/bash

# ============================================================
# build_push_image.sh — Build & Push Docker image ke GitHub Packages
# (GitHub Container Registry / ghcr.io)
# ============================================================

# Variabel konfigurasi
GHCR_USER=arighmt67-bit        # username GitHub
IMAGE_NAME=item-app            # nama image
TAG=v1                         # tag image
GHCR_IMAGE=ghcr.io/${GHCR_USER}/${IMAGE_NAME}:${TAG}   # nama image format GHCR

# 1. Membuat Docker image dari Dockerfile dengan nama item-app dan tag v1
docker build -t item-app:v1 .

# 2. Melihat daftar image di lokal
docker images

# 3. Mengubah nama image agar sesuai format GitHub Packages (ghcr.io)
docker tag item-app:v1 ${GHCR_IMAGE}

# 4. Login ke GitHub Packages (GHCR) via token dari gh CLI
echo $GHCR_TOKEN | docker login ghcr.io -u ${GHCR_USER} --password-stdin

# 5. Mengunggah image ke GitHub Packages
docker push ${GHCR_IMAGE}
