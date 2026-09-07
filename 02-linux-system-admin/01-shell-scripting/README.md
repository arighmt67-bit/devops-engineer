# 🐧 Proyek 1: Otomatisasi Shell Scripting

Proyek Pertama dari kelas **Menjadi Linux System Administrator** (Dicoding). Script otomatisasi sederhana menggunakan Bash shell script untuk memantau performa dan penggunaan resource sistem (Memory dan Disk) secara berkala.

---

## 📋 Berkas Proyek

- `script.sh` : Script bash utama untuk automasi monitoring memory & disk.
- `history.txt` : Log riwayat command selama pengerjaan submission di terminal Linux.

---

## ⚙️ Fitur Script (`script.sh`)

1. **Header Informasi Personal**: Menampilkan pesan pembuka dengan variabel nama pengguna.
2. **Monitoring RAM (Memory)**: Menampilkan kapasitas dan penggunaan memori RAM dalam satuan Megabytes (`free -m`).
3. **Monitoring Filesystem (Disk)**:
   - Menampilkan kapasitas filesystem dalam Gigabytes (`df -BG`).
   - Melakukan filtering spesifik hanya kolom `Filesystem` dan `Use%`, serta mengecualikan mount point temporary (`tmpfs`) menggunakan `awk`.
4. **Eksekusi Otomatis Berulang**: Menggunakan loop `while` sebanyak 3 kali iterasi dengan jeda delay 1 detik antar proses.
5. **Komentar Penjelasan**: Seluruh baris kode dilengkapi dokumentasi penjelasan fungsi perintah.

---

## 🚀 Cara Menjalankan

Beri izin eksekusi lalu jalankan script di lingkungan Linux / Bash:

```bash
chmod +x script.sh
./script.sh
```
