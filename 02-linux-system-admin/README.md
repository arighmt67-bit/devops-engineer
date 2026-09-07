# 🐧 Menjadi Linux System Administrator — Dicoding Submission Showcase

[![Dicoding](https://img.shields.io/badge/Dicoding-Course%20Completed-blue?style=flat-square&logo=dicoding)](https://www.dicoding.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Linux](https://img.shields.io/badge/OS-Linux%20Ubuntu-orange?style=flat-square&logo=ubuntu)](https://ubuntu.com/)
[![Bash](https://img.shields.io/badge/Script-Bash%20Shell-4EAA25?style=flat-square&logo=gnu-bash)](https://www.gnu.org/software/bash/)
[![OpenSSH](https://img.shields.io/badge/Security-OpenSSH%20Server-black?style=flat-square&logo=ssh)](https://www.openssh.com/)

Repositori resmi portofolio dan dokumentasi teknis pengerjaan tugas akhir untuk kelas **[Menjadi Linux System Administrator](https://www.dicoding.com/academies/384)** di **Dicoding Indonesia**. Repositori ini menggabungkan seluruh implementasi proyek dari dasar otomatisasi administrasi sistem hingga pengamanan server Linux tingkat lanjut.

---

## 📑 Daftar Proyek Submission

| No | Proyek | Fokus Materi | Path Direktori | Detail Berkas Kunci |
| :---: | :--- | :--- | :--- | :--- |
| **01** | **Proyek 1: Shell Scripting** | Otomatisasi Monitoring Sistem (RAM & Disk) | [`01-shell-scripting/`](./01-shell-scripting/) | • `script.sh`<br>• `history.txt` |
| **02** | **Proyek 2: Konfigurasi SSH Server** | Hardening Server, Key Auth, User Mgmt & Log Maintenance | [`02-ssh-server-configuration/`](./02-ssh-server-configuration/) | • `sshd_config`<br>• `hapus-log.sh`<br>• `log-ssh.txt` / `.json`<br>• `daftar-user.txt` / `.gpg` |

---

## 🛠️ Detail Implementasi Tiap Proyek

### 1. Proyek 1: Otomatisasi Shell Scripting (`01-shell-scripting/`)
Fokus pada pembuatan skrip otomasi Bash untuk memantau beban sistem Linux:
- **RAM Monitoring**: Membaca memori sistem dalam Megabytes (`free -m`).
- **Disk Monitoring**: Memeriksa penggunaan filesystem dalam Gigabytes (`df -BG`).
- **Data Filtering**: Filter output menggunakan `awk` untuk menampilkan kolom `Filesystem` dan `Use%`, serta mengecualikan partisi virtual `tmpfs`.
- **Looping & Interval**: Eksekusi otomatis berulang sebanyak 3 kali iterasi dengan delay `sleep 1s`.

### 2. Proyek 2: Konfigurasi & Hardening SSH Server (`02-ssh-server-configuration/`)
Fokus pada standarisasi keamanan server Linux berbasis OpenSSH:
- **Port Hardening**: Mengubah port default SSH dari port 22 ke port kustom **2000**.
- **User & Key Authentication**:
  - Menonaktifkan autentikasi password (`PasswordAuthentication no`).
  - Menonaktifkan login user root (`PermitRootLogin no`).
  - Konfigurasi autentikasi berbasis asymmetric key pair (`ssh-rsa` / `ed25519`).
- **Data Security**: Enkripsi file daftar pengguna sistem menggunakan GNU Privacy Guard (`daftar-user.txt.gpg`).
- **System Maintenance & Log Management**:
  - Ekstraksi log aktivitas autentikasi SSH ke format teks dan JSON (`journalctl -u ssh`).
  - Skrip pembersihan dan rotasi log otomatis (`hapus-log.sh`) menggunakan `journalctl --vacuum-size`.
- **Interactive Showcase**: Dilengkapi showcase portofolio interaktif berbasis HTML/CSS di `02-ssh-server-configuration/index.html`.

---

## 🚀 Panduan Eksekusi

### Menjalankan Skrip Monitoring Proyek 1:
```bash
cd 01-shell-scripting
chmod +x script.sh
./script.sh
```

### Menjalankan Skrip Pembersihan Log Proyek 2:
```bash
cd 02-ssh-server-configuration
chmod +x hapus-log.sh
sudo ./hapus-log.sh
```

---

## 👤 Author

**Ari Rahmat Romadhon**
- GitHub: [@arighmt67-bit](https://github.com/arighmt67-bit)
- Portfolio: [arighmt67-bit.github.io](https://arighmt67-bit.github.io/)
