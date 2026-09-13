# Infrastructure as Code (IaC) — AWS Microservices and Observability

Modul Terraform modular untuk provisioning infrastruktur cloud AWS yang aman, terdokumentasi, dan siap menopang containerized backend serta monitoring stack.

## Arsitektur Infrastruktur
* **Network Foundation**: Custom AWS VPC (10.0.0.0/16) dengan isolated public subnet, Internet Gateway, dan custom routing table.
* **Security Hardening**: Security Group granular yang membatasi akses:
  - Port 80 dan 443: HTTP/HTTPS publik.
  - Port 5000: API Gateway / Forum API.
  - Port 3000: Grafana Dashboard.
  - Port 9090: Prometheus metrics scraping (dibatasi khusus internal VPC CIDR).
* **Frugal and Cost Protection ($0 Cloud Guard)**: Dilengkapi dengan skrip `teardown.sh` untuk memastikan seluruh resource lab langsung dihancurkan setelah pengujian selesai.

## Eksekusi Cepat
```bash
# Format dan Validasi
terraform fmt -check
terraform init -backend=false
terraform validate

# Provisioning (On-Demand Lab)
terraform apply

# Auto-Destroy (Bebas Biaya)
./teardown.sh
```
