# Runbook: IAM User Access Lifecycle & Least-Privilege Policy

## 1. Tujuan
SOP pengelolaan daur hidup akses pengguna (onboarding, privilege escalation, offboarding) dengan prinsip Least Privilege dan audit trail terpusat.

## 2. Daur Hidup Akses
- Onboarding: Role spesifik tanpa administrative privilege default. Wajib MFA.
- Audit Akses Berkala: Review izin akses setiap 90 hari, pencabutan token non-aktif > 30 hari.
- Offboarding: Revokasi seketika (< 15 menit dari tiket HR/ITSM) atas kredensial SSO, AWS IAM, dan GitHub.
