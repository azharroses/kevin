# Deploy RAC DBR ke Render

## Opsi Service

Gunakan **Web Service**, bukan Static Site.

Render akan memakai:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn app:app
```

File `render.yaml` dan `Procfile` sudah disiapkan.

## Environment Variables

Isi jika backend Render memang akan mengakses database/API kantor:

```text
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
ORACLE_DSN
ORACLE_USER
ORACLE_PASSWORD
MUF_OID_API_ENDPOINT
```

Jika database hanya bisa diakses dari jaringan kantor/VPN, backend Render kemungkinan tidak bisa memakai `Cek Angsuran` otomatis secara langsung.

## URL API Cek Angsuran

Di halaman web ada field **URL API Cek Angsuran**.

Kosongkan jika ingin memakai backend yang sama dengan web Render:

```text
/api/cek-angsuran
```

Isi dengan backend lokal/internal jika `Cek Angsuran` dijalankan dari laptop/server kantor:

```text
http://localhost:5000
```

atau:

```text
http://10.20.203.31:5000
```

## Health Check

Endpoint cek server:

```text
/healthz
```

Jika sukses akan mengembalikan:

```json
{"status":"ok"}
```
