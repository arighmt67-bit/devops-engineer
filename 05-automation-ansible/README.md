# Automated Configuration Management & Server Hardening with Ansible

Modul otomasi infrastruktur berbasis Ansible Playbook untuk provisioning server Ubuntu production secara idempotent.

## Fitur Otomasi
1. Package Management: Automated update apt cache & instalasi security tools (htop, fail2ban, curl).
2. Network Security & Hardening: Konfigurasi firewall ufw default deny, hanya port 22/80/443.
3. Web Server Setup: Provisioning service systemd Nginx web server.
