# Menggunakan image resmi Node.js versi 18 varian Alpine yang berukuran kecil.
FROM node:18-alpine

# Menetapkan /app sebagai direktori kerja di dalam container.
WORKDIR /app

# Menyalin berkas manifest dependensi terlebih dahulu agar cache build optimal.
COPY package*.json ./

# Memasang dependensi production saja supaya ukuran image tetap ramping.
RUN npm install --omit=dev

# Menyalin seluruh sisa kode sumber aplikasi ke dalam image.
COPY . .

# Menetapkan nilai default port aplikasi shipping service.
ENV PORT=3001

# Mendokumentasikan bahwa container mendengarkan pada port 3001.
EXPOSE 3001

# Menjalankan aplikasi melalui script start ketika container dijalankan.
CMD ["npm", "start"]
