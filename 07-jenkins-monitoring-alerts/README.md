# Jenkins Monitoring dengan Alert Prometheus

Lab ini memantau Jenkins dengan Prometheus dan Grafana, lalu menambahkan aturan alert supaya
kegagalan layanan terdeteksi tanpa harus membuka dashboard.

## Komponen

| Komponen | Port | Keterangan |
| --- | --- | --- |
| Jenkins (`jenkins-blueocean`) | 49000 | Mengekspos metrik di `/prom` lewat plugin Prometheus metrics |
| Prometheus | 9091 | Men-*scrape* Jenkins setiap 10 detik dan mengevaluasi aturan alert |
| Grafana | 3031 | Dashboard kesehatan Jenkins, jumlah executor, antrean, dan JVM heap |

Semua berjalan sebagai container Docker di VM Ubuntu 24.04 (Multipass).

## Aturan alert

Berkas: [`alert_rules.yml`](alert_rules.yml), dimuat lewat `rule_files` di [`prometheus.yml`](prometheus.yml).

| Alert | Kondisi | Durasi | Tingkat |
| --- | --- | --- | --- |
| `JenkinsDown` | `up{job="jenkins"} == 0` | 30 detik | critical |
| `JenkinsQueueHigh` | `jenkins_queue_size_value > 3` | 1 menit | warning |

Sintaks aturan divalidasi dengan `promtool check rules` (2 aturan valid).

## Pembuktian

Container Jenkins dimatikan dengan sengaja, lalu dinyalakan kembali. Cuplikan dari
[`bukti-alert-firing.txt`](bukti-alert-firing.txt) (waktu UTC):

```text
03:28:11 SEBELUM: up=1 JenkinsDown=inactive
03:28:11 MATIKAN Jenkins (docker stop)
03:28:16 setelah mati: up=0 JenkinsDown=inactive
03:28:52 setelah mati: up=0 JenkinsDown=firing
         JenkinsDown firing critical - Jenkins tidak dapat di-scrape
03:28:52 NYALAKAN Jenkins lagi (docker start)
03:33:18 pemulihan: up=1 JenkinsDown=inactive
```

Alert berpindah ke `firing` sekitar 41 detik setelah Jenkins dimatikan (jeda `for: 30s` ditambah
interval scrape), lalu kembali normal setelah Jenkins hidup lagi.

## Batasan

- Alert hanya terlihat di Prometheus dan Grafana. **Belum ada Alertmanager**, jadi tidak ada
  notifikasi ke email atau chat.
- `JenkinsQueueHigh` terdaftar dan valid, tetapi belum dipicu dalam pengujian ini.
- Ini lab lokal untuk satu instance Jenkins, bukan sistem produksi.
