# 🔐 Konfigurasi SSH Server — Linux System Administrator

Proyek akhir dari kelas **Menjadi Linux System Administrator** (Dicoding). Simulasi nyata mengelola server Linux: membuat user baru, mengamankan akses remote lewat SSH key-based authentication, mengganti port default, menonaktifkan login root, hingga mengotomatiskan pembersihan log sistem.

## Apa yang Dikerjakan

- Membuat regular user baru (`dicoding`) dengan full name `Dicoding Indonesia`.
- Login SSH dari mesin pertama ke `localhost` (mesin kedua) memakai autentikasi password.
- Membuat SSH key pair (ed25519), menyalin public key ke mesin kedua, lalu login ulang memakai key-based authentication.
- Mengubah konfigurasi `sshd_config` agar:
  - Hanya menerima autentikasi via public key.
  - Menolak autentikasi via password.
  - Mengganti port SSH default (22) menjadi 2000.
  - Menonaktifkan remote login sebagai root.
- Mendokumentasikan seluruh aktivitas lewat log SSH (`journalctl`).
- Membuat script otomatisasi pembersihan log (`hapus-log.sh`) yang menampilkan penggunaan disk journal, melakukan vacuum hingga batas 10 MB, lalu menampilkan ulang hasilnya — dijalankan berulang memakai loop `while`.

## Struktur Berkas

| Berkas | Keterangan |
|---|---|
| `daftar-user.txt` | Daftar seluruh user di sistem |
| `daftar-user.txt.gpg` | Versi terenkripsi dari `daftar-user.txt` (GPG) |
| `log-ssh.txt` | Log aktivitas SSH (format teks) |
| `log-ssh.json` | Log aktivitas SSH (format JSON) |
| `sshd_config` | Konfigurasi akhir SSH server |
| `hapus-log.sh` | Script otomatisasi pembersihan log journal |

## Stack & Tools

Ubuntu 26.04 LTS (via Multipass VM di macOS), OpenSSH Server, systemd/journalctl, GPG.

## Catatan

Proyek ini dikerjakan sebagai bagian dari submission kelas Dicoding *Menjadi Linux System Administrator*. Seluruh konfigurasi diuji langsung di virtual machine, bukan simulasi.
