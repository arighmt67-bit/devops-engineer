# E-Commerce App - Submission Akhir a433 Microservices

Implementasi **Asynchronous Communication** pada aplikasi E-Commerce App
menggunakan RabbitMQ, container image di GitHub Packages, dan deployment
ke Kubernetes.

## Struktur Berkas

```
.
├── order-service/          # Starter branch order-service + Dockerfile
├── shipping-service/       # Starter branch shipping-service + Dockerfile
├── kubernetes/             # Manifest Kubernetes
│   ├── rabbitmq.yaml
│   ├── order-service.yaml
│   └── shipping-service.yaml
└── link.txt                # Tautan container image di GitHub Packages
```

## Container Image (GitHub Packages)

- ghcr.io/arighmt67-bit/order-service:latest
- ghcr.io/arighmt67-bit/shipping-service:latest

Kedua package bersifat **public** sehingga dapat ditarik tanpa autentikasi.

## Cara Menjalankan

```bash
# 1. Deploy RabbitMQ terlebih dahulu
kubectl apply -f kubernetes/rabbitmq.yaml
kubectl wait --for=condition=ready pod -l app=rabbitmq --timeout=180s

# 2. Deploy kedua service
kubectl apply -f kubernetes/order-service.yaml
kubectl apply -f kubernetes/shipping-service.yaml

# 3. Verifikasi seluruh Pod berjalan
kubectl get pods
```

## Pengujian

```bash
kubectl port-forward svc/order-service 3000:3000

curl -X POST http://localhost:3000/order \
  -H 'Content-Type: application/json' \
  -d '{"order":{"book_name":"Harry Potter","author":"J.K Rowling","buyer":"Fikri Helmi Setiawan","shipping_address":"Jl. Batik Kumeli no 50 Bandung"}}'

kubectl logs -l app=shipping-service --tail=5
```

Keluaran shipping service:

```
Order received: {"book_name":"Harry Potter", ...}
** Will be shipped soon! **
```

## Repository

https://github.com/arighmt67-bit/a433-microservices
(branch `order-service` dan `shipping-service`)
