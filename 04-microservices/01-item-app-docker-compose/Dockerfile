# ============================================================
# Dockerfile — Membangun image untuk container item-app
# ============================================================

# 1. Base image Node.js versi 14
FROM node:14

# 2. Working directory untuk container adalah /app
WORKDIR /app

# 3. Menyalin seluruh source code ke working directory di container
COPY . .

# 4. Aplikasi berjalan dalam production mode dan memakai item-db sebagai host database
ENV NODE_ENV=production DB_HOST=item-db

# 5. Install dependencies untuk production, lalu build aplikasi
RUN npm install --production --unsafe-perm && npm run build

# 6. Ekspos port 8080 yang digunakan aplikasi
EXPOSE 8080

# 7. Saat container diluncurkan, jalankan server dengan npm start
CMD ["npm", "start"]
