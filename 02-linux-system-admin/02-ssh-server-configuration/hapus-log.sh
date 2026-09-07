#!/bin/bash
#
# hapus-log.sh
# Proyek Konfigurasi SSH Server - Saran ke-3
#
# Tujuan script ini:
#   1. Menampilkan informasi penggunaan disk dari semua berkas journalctl
#      (baik yang aktif maupun yang diarsipkan).
#   2. Menghapus journalctl log hingga ruang disk yang digunakan untuk log
#      berkisar 10 MB.
#   3. Menampilkan kembali informasi penggunaan disk dari semua berkas
#      journalctl setelah penghapusan dilakukan.
#
# Perulangan while di bawah digunakan untuk menjalankan tahap "tampilkan
# penggunaan disk" sebanyak 2 kali (sebelum dan sesudah penghapusan log),
# sehingga proses tampil-hapus-tampil berjalan secara konsisten dan mudah
# dibaca outputnya.

# Batas ukuran log target setelah dibersihkan
UKURAN_TARGET="10M"

# Variabel counter untuk mengontrol perulangan while.
# counter=1 -> tahap "sebelum penghapusan"
# counter=2 -> tahap "sesudah penghapusan"
counter=1

echo "############################################################"
echo "#   SCRIPT PEMBERSIHAN LOG JOURNALCTL - hapus-log.sh        #"
echo "############################################################"
echo ""

# Perulangan while agar proses tampil-hapus-tampil berjalan terstruktur
while [ $counter -le 2 ]
do
    if [ $counter -eq 1 ]; then
        echo "============================================================"
        echo " TAHAP $counter: Penggunaan disk log SEBELUM dibersihkan"
        echo "============================================================"
    else
        echo "============================================================"
        echo " TAHAP $counter: Penggunaan disk log SESUDAH dibersihkan"
        echo "============================================================"
    fi
    echo ""

    # Menampilkan informasi penggunaan disk dari seluruh berkas journalctl,
    # baik yang aktif (active) maupun yang sudah diarsipkan (archived)
    echo "-> Menjalankan: journalctl --disk-usage"
    journalctl --disk-usage
    echo ""
    # Jeda sejenak agar output mudah diikuti
    sleep 1

    # Setelah tahap "sebelum" ditampilkan, lakukan proses penghapusan log
    if [ $counter -eq 1 ]; then
        echo "------------------------------------------------------------"
        echo " Menghapus log journalctl hingga tersisa sekitar $UKURAN_TARGET ..."
        echo "------------------------------------------------------------"
        echo ""
        echo "-> Menjalankan: journalctl --vacuum-size=$UKURAN_TARGET"
        # Menghapus journalctl log (baik aktif maupun archived) hingga
        # total ruang disk yang terpakai berkisar pada UKURAN_TARGET
        journalctl --vacuum-size=$UKURAN_TARGET
        echo ""
        sleep 1
    fi

    # Baris pemisah antar tahap
    echo ""

    # Menaikkan nilai counter agar perulangan while berlanjut/berhenti
    counter=$((counter+1))
done

echo "############################################################"
echo "#   SELESAI. Log journalctl telah dibersihkan.              #"
echo "############################################################"
