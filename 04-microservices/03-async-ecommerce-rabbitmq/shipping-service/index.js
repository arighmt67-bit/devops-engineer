// Memuat variabel lingkungan dari berkas .env ke dalam process.env.
require('dotenv').config()

// Mengimpor framework Express untuk membangun HTTP server.
const express = require("express");
// Membuat instance aplikasi Express.
const app = express();

// Mengimpor body-parser sebagai utilitas pembaca body request.
const bp = require("body-parser");

// Mengimpor amqplib sebagai klien protokol AMQP (RabbitMQ).
const amqp = require("amqplib");
// Mengambil URL koneksi RabbitMQ dari environment variable.
const amqpServer = process.env.AMQP_URL;
// Menyiapkan variabel penampung channel dan connection RabbitMQ.
var channel, connection;

// Memanggil fungsi koneksi ke RabbitMQ saat aplikasi dijalankan.
connectToQueue();

// Fungsi asynchronous untuk menyambung dan mengonsumsi pesan dari queue.
async function connectToQueue() {
    // Membungkus seluruh proses agar kegagalan koneksi tertangani.
    try {
        // Membuka koneksi TCP ke server RabbitMQ sesuai AMQP_URL.
        connection = await amqp.connect(amqpServer);
        // Membuat channel sebagai jalur komunikasi di atas koneksi tersebut.
        channel = await connection.createChannel();
        // Memastikan queue "order" tersedia sebelum mulai dikonsumsi.
        await channel.assertQueue("order");
        // Berlangganan queue "order" untuk menerima pesan yang masuk.
        channel.consume("order", data => {
            // Mencetak isi pesan order yang diterima dari queue.
            console.log(`Order received: ${Buffer.from(data.content)}`);
            // Menampilkan penanda bahwa order akan segera dikirim.
            console.log("** Will be shipped soon! **\n")
            // Mengirim acknowledgement agar pesan dihapus dari queue.
            channel.ack(data);
        });
    // Menangkap kesalahan yang terjadi selama proses koneksi/konsumsi.
    } catch (ex) {
        // Mencetak detail kesalahan ke console untuk keperluan debugging.
        console.error(ex);
    }
}

// Menjalankan HTTP server pada port sesuai environment variable PORT.
app.listen(process.env.PORT, () => {
    // Menampilkan informasi port tempat server berjalan.
    console.log(`Server running at ${process.env.PORT}`);
});
