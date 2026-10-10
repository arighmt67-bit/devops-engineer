# Linux & PostgreSQL Operations Lab

Lab Ubuntu terpisah untuk menjalankan Forum API sebagai service nonroot, menguji akses database, troubleshooting, dan backup–restore.

**Hasil uji:** 32 tes offline dan 41 pemeriksaan integrasi lulus pada Ubuntu 24.04 / PostgreSQL 16.15. Tiga jalur cleanup gagal juga diuji dengan efek nyata di guest; kegagalan boundary-nya diinjeksi. Bukti rerun ekstrak ZIP ada di `evidence/zip-rerun-verification.json`.

## Jalankan

Prasyarat: Python 3.9+, Multipass, internet saat instalasi pertama. VM `ops-db-lab`: 2 CPU, RAM 1 GB, disk 8 GB.

```bash
python3 lab.py up
python3 lab.py status
python3 lab.py test
python3 lab.py stop
```

`test` melakukan register/login/buat/baca thread, tes constraint dan transaksi SQL, akses read-only, gangguan koneksi/service, serta `pg_dump` → restore ke **database baru** → perbandingan fingerprint seluruh baris di schema non-system dan definisi schema → pembacaan lewat API.

- Aplikasi di `assets/` adalah snapshot commit terpin; kode aplikasi tidak diubah.
- Data sintetis selalu berlabel **TEST FIXTURE**. Ini bukan data keuangan atau pengalaman production.
- Gangguan hanya di guest; rule spesifik run diverifikasi sudah hilang dan restart tetap dicoba meski cleanup gagal. VM lain tidak disentuh.
- Secret dan dump tetap di guest. ZIP hanya berisi source, tes, dan evidence tersanitasi; tidak ada `.env` atau dump database.
- Laporan wajib cocok dengan ID invocation dan exit code; laporan basi/inkonsisten tidak dipublikasikan. `evidence/report-summary.json` memuat hasil run terakhir; `evidence/tdd/` menyimpan output aktual RED/GREEN. Kegagalan historis tetap disimpan—nilai `exit_code`, bukan nama fase, menentukan hasil.
- Reuse instalasi membandingkan byte dan inventory source terpin, bukan marker saja. Symlink, source tambahan/hilang/berubah ditolak; `node_modules` adalah dependensi runtime di luar cakupan pin.
- Restore tidak menimpa sumber/target lama. ACL dump tidak disalin; akses aplikasi diberikan khusus pada target baru. Definisi schema dan baris semua tabel non-system dibandingkan; ACL dan state sequence tidak diklaim identik. Akses read-only serta larangan DDL/TEMP di target diuji langsung.
- Durasi recovery adalah observasi lab, **bukan jaminan RTO/RPO production**. Endpoint `/` tidak memeriksa kesiapan database.
- Run menambah fixture, backup, dan database restore di guest. `stop` hanya mematikan VM, tidak menghapus data.
