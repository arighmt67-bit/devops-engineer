// Memuat variabel lingkungan dari berkas .env ke dalam process.env.
require('dotenv').config()

// Mengimpor framework Express untuk membangun HTTP server.
const express = require("express");
// Membuat instance aplikasi Express.
const app = express();

// Mengimpor body-parser untuk membaca body request.
const bp = require("body-parser");
// Mendaftarkan middleware agar body ber-format JSON otomatis diurai.
app.use(bp.json());

// Mengimpor amqplib sebagai klien protokol AMQP (RabbitMQ).
const amqp = require("amqplib");
// Mengambil URL koneksi RabbitMQ dari environment variable.
const amqpServer = process.env.AMQP_URL;
// Menyiapkan variabel penampung channel dan connection RabbitMQ.
var channel, connection;

// Memanggil fungsi koneksi ke RabbitMQ saat aplikasi dijalankan.
connectToQueue();

// Fungsi asynchronous untuk membuka koneksi dan channel ke RabbitMQ.
async function connectToQueue() {
    // Membuka koneksi TCP ke server RabbitMQ sesuai AMQP_URL.
    connection = await amqp.connect(amqpServer);
    // Membuat channel sebagai jalur komunikasi di atas koneksi tersebut.
    channel = await connection.createChannel();
    // Membungkus deklarasi queue agar kegagalan tidak menghentikan proses.
    try {
        // Menetapkan nama queue yang dipakai untuk data order.
        const queue = "order";
        // Memastikan queue "order" tersedia; dibuat bila belum ada.
        await channel.assertQueue(queue);
        // Menampilkan konfirmasi bahwa koneksi queue berhasil.
        console.log("Connected to the queue!")
    // Menangkap kesalahan yang terjadi saat proses deklarasi queue.
    } catch (ex) {
        // Mencetak detail kesalahan ke console untuk keperluan debugging.
        console.error(ex);
    }
}

// Mendefinisikan endpoint HTTP POST /order sebagai penerima data order.
app.post("/order", (req, res) => {
    // Mengambil properti order dari body request yang dikirim klien.
    const { order } = req.body;
    // Mengirimkan data order tersebut ke queue RabbitMQ.
    createOrder(order);
    // Mengembalikan data order sebagai response kepada klien.
    res.send(order);
});

// Fungsi asynchronous yang mempublikasikan data order ke queue.
const createOrder = async order => {
    // Menetapkan nama queue tujuan pengiriman pesan.
    const queue = "order";
    // Mengirim data order ke queue setelah diubah menjadi Buffer JSON.
    await channel.sendToQueue(queue, Buffer.from(JSON.stringify(order)));
    // Menampilkan konfirmasi bahwa order berhasil dibuat.
    console.log("Order succesfully created!")
    // Mendaftarkan penanganan sinyal SIGINT satu kali untuk penutupan rapi.
    process.once('SIGINT', async () => {
        // Memberi tahu bahwa sinyal interupsi diterima.
        console.log('got sigint, closing connection');
        // Menutup channel RabbitMQ agar sumber daya dilepaskan.
        await channel.close();
        // Menutup koneksi RabbitMQ sepenuhnya.
        await connection.close();
        // Menghentikan proses Node.js dengan status sukses.
        process.exit(0);
    });
};

// Menjalankan HTTP server pada port sesuai environment variable PORT.
app.listen(process.env.PORT, () => {
    // Menampilkan informasi port tempat server berjalan.
    console.log(`Server running at ${process.env.PORT}`);
});
