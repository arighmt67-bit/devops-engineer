---
name: jenkins-submission-fixer
description: Gunakan subagent ini untuk memperbaiki submission "CI Pipeline dengan Jenkins" sesuai feedback reviewer — mengecek environment (VM/Jenkins/tunnel), membuat pipeline React baru, mengambil log lengkap dari Blue Ocean, dan menyusun ulang folder submission. Panggil secara eksplisit, jangan didelegasikan otomatis untuk task lain di luar konteks ini.
tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch
model: inherit
---

# Konteks Project

Aku sedang mengerjakan submission "Membangun CI Pipeline dengan Jenkins" (kelas Dicoding a428-cicd-labs).
Environment sudah pernah di-setup sebelumnya (lihat riwayat kerja AI agent sebelumnya bernama "Aconk"):

- Jenkins jalan di VM Multipass Ubuntu 24.04 (nama VM: `jenkins-vm`), via Docker:
  - Container `jenkins-blueocean` (image `jenkins/jenkins:lts-jdk17`, port host 49000 -> container 8080)
  - Container `jenkins-docker` (docker:dind, untuk Docker-in-Docker)
- Akses dari Mac (host) ke Jenkins lewat SSH port-forward: `localhost:49000` -> VM `jenkins-vm:49000`.
- NGINX reverse proxy: listen port 9000, proxy_pass ke `http://localhost:49000`.
- Akun Jenkins:
  - Signup/security realm sudah diaktifkan (Kriteria 2 sudah lolos, JANGAN diutak-atik lagi).
  - User `arirahmatr` sudah dibuat dan bisa login (password sempat di-set manual, cek dulu apakah masih valid).
- Repo GitHub yang sudah ada:
  - `https://github.com/arighmt67-bit/a428-cicd-labs` — fork resmi dari `dicodingacademy/a428-cicd-labs`,
    berisi branch `hello-world`, `main`, `react-app`, `trivia-app`. **Branch `react-app` adalah source code
    React App resmi dari materi kelas** — pakai ini, JANGAN buat React app custom baru.
  - `https://github.com/arighmt67-bit/a428-cicd-python-app` — repo Python custom yang sempat dipakai untuk
    pipeline `submission-cicd-pipeline-arirahmatr` yang lama (ini yang jadi masalah, lihat feedback reviewer).
- Pipeline Jenkins yang sudah ada: `submission-cicd-pipeline-arirahmatr`, menjalankan repo Python di atas,
  Poll SCM tiap 2 menit, build terakhir SUCCESS (build #3).

# Feedback dari Reviewer (WAJIB diperbaiki)

1. **log.txt yang dilampirkan tidak lengkap.** Harus diunduh dari halaman **Artifacts di Blue Ocean**,
   bukan potongan log manual.
2. **log.txt harus berisi log lengkap** dari awal sampai akhir eksekusi pipeline.
3. **Pipeline yang dilampirkan pakai aplikasi Python**, padahal kriteria wajib submission ini minta
   **React App**. Harus diganti/dilampirkan pipeline + repo React App yang benar.

# Checklist Kriteria

- [ ] Perlu diperbaiki: Menggunakan Source Code React App (pakai branch `react-app` dari
      `arighmt67-bit/a428-cicd-labs`, JANGAN bikin app baru dari nol)
- [ ] Perlu diperbaiki: Membuat Jenkins Pipeline baru (job baru, jangan pakai/timpa job Python yang lama)
- [x] Sudah terpenuhi, JANGAN diubah: Mengaktifkan Fitur Signup dan Membuat Akun Baru di Jenkins

# Tugas yang Perlu Dikerjakan

1. Cek environment masih hidup: VM `jenkins-vm` running, container Jenkins & dind up, SSH tunnel ke
   `localhost:49000` aktif dari Mac. Perbaiki kalau ada yang mati sebelum lanjut.
2. Login ke Jenkins sebagai `arirahmatr` untuk verifikasi akun masih berfungsi (Kriteria 2).
3. Buat Jenkins Pipeline job baru (nama jelas, misal `submission-cicd-pipeline-arirahmatr-react`):
   - Pipeline script from SCM, Git
   - Repository URL: `https://github.com/arighmt67-bit/a428-cicd-labs.git`
   - Branch: `*/react-app`
   - Script Path: `Jenkinsfile`
   - Build Trigger: Poll SCM, schedule `H/2 * * * *`
4. Pastikan plugin & tool yang dibutuhkan Jenkinsfile react-app sudah tersedia (NodeJS tool, Docker
   Pipeline plugin, Docker CLI + DOCKER_HOST) sebelum trigger build.
5. Trigger build, pantau sampai SUCCESS. Kalau gagal, analisis akar masalah, jangan asal retry.
6. Ambil log.txt lengkap dari Blue Ocean > Artifacts setelah build SUCCESS.
7. Ambil ulang screenshot relevan: Dashboard, daftar pipeline Blue Ocean, detail activity build sukses.
8. Susun ulang folder submission: ganti log.txt lama, ganti referensi repo Python jadi React, update
   screenshot.

# Batasan & Prinsip Kerja

- Hemat token/waktu: gabungkan command yang bisa digabung, jangan retry command yang sama tanpa
  mengubah apa pun.
- JANGAN ubah konfigurasi security/signup Jenkins yang sudah lolos di Kriteria 2.
- JANGAN hapus atau rusak pipeline `submission-cicd-pipeline-arirahmatr` (Python) yang lama — biarkan
  tetap ada berdampingan dengan pipeline React yang baru.
- Kalau ada credential/password yang perlu dipakai sementara untuk testing lewat API, JANGAN commit ke
  repository publik — cukup pakai di terminal/env var lokal.
- Kerjakan bertahap dan laporkan progress tiap tahap selesai. Berhenti dan minta konfirmasi sebelum
  trigger build final yang akan dipakai untuk screenshot submission.

# Definisi Selesai

- Pipeline React baru ada di Jenkins, build terakhir SUCCESS.
- File log.txt baru berasal dari unduhan Blue Ocean Artifacts, berisi log lengkap dari `Started by...`
  sampai `Finished: SUCCESS`.
- Submission final berisi: log.txt lengkap (React), link/repo React App (branch react-app di fork),
  screenshot Dashboard + Blue Ocean pipeline React, dan bukti Kriteria 2 (signup) tetap disertakan tanpa
  perubahan.