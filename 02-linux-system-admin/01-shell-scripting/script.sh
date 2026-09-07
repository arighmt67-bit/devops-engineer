#!/bin/bash

# Variabel nama lengkap
name="Ari Rahmat R"

# Mencetak salam pembuka dengan nama
echo "Hello, my name is ${name}"
echo ""

# Perulangan while untuk menjalankan semua perintah sebanyak 3 kali
counter=1
while [ $counter -le 3 ]; do
    echo "========================================="
    echo "           ITERASI KE-${counter}              "
    echo "========================================="
    echo ""

    # Keterangan untuk perintah penggunaan memori
    echo "=== Ukuran Memory pada Sistem (dalam Megabytes) ==="
    # Menampilkan ukuran memory dalam satuan megabytes menggunakan free
    free -m
    echo ""

    # Jeda 1 detik sebelum perintah berikutnya
    sleep 1

    # Keterangan untuk perintah penggunaan disk (gigabytes)
    echo "=== Penggunaan Ruang Disk pada Filesystem (dalam Gigabytes) ==="
    # Menampilkan penggunaan ruang disk dalam satuan gigabytes menggunakan df
    df -BG
    echo ""

    # Jeda 1 detik sebelum perintah berikutnya
    sleep 1

    # Keterangan untuk perintah penggunaan disk (hanya kolom Filesystem dan Use%, tanpa tmpfs)
    echo "=== Penggunaan Ruang Disk: Filesystem dan Use% (tanpa tmpfs) ==="
    # Menampilkan hanya kolom Filesystem dan Use%, mengecualikan tmpfs
    df -h | awk 'NR==1 {print "Filesystem", "Use%"} NR>1 && $1 !~ /tmpfs/ {print $1, $5}'
    echo ""

    # Jeda 1 detik sebelum iterasi berikutnya
    sleep 1

    # Menaikkan nilai counter
    counter=$((counter + 1))
done

echo "========================================="
echo "         Script selesai dijalankan.       "
echo "========================================="
