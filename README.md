# 1Hub Control Portal

Hệ thống quản lý thanh toán NAPAS — dashboard giám sát giao dịch, đối soát, quản lý merchant, và sinh mã QR VietQR IBFT. 1Hub **KHÔNG** giữ tiền — chỉ nhận notice từ NAPAS, ghi ledger, thông báo merchant, đối soát.

## Stack

| Layer | Tech |
|-------|------|
| Backend | Python 3.11, FastAPI, SQLAlchemy, SQLite |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS v4, TanStack Query, recharts |
| Auth | JWT (HS256) + bcrypt + refresh token rotation + RBAC (admin/ops/viewer) |
| QR | NAPAS VietQR IBFT EMVCo (TLV + CRC-16/CCITT-FALSE) |
| NAPAS API | RSA-2048 SHA256withRSA, CSR-based cert, IP whitelist |

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
python seed.py            # tạo DB + admin user + 3 merchant + 20 txn
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev               # http://localhost:5173
```

Login: `admin` / `admin123`

## Project Structure

```
backend/
  app/
    config.py             # Settings + NAPAS sandbox endpoints
    main.py               # FastAPI app, CORS, router registration
    database.py           # SQLAlchemy engine, session, Base
    core/
      auth.py             # JWT, bcrypt, AES-256-GCM (API key crypto)
      crypto_napas.py     # RSA sign/verify PEM key cho NAPAS APG
      security.py         # IP whitelist, signature verify
      deps.py             # FastAPI dependencies (auth, RBAC)
      idempotency.py      # Duplicate notice check
      exceptions.py       # AppException + handler
    models/               # SQLAlchemy ORM (9 models)
    schemas/              # Pydantic request/response
    repositories/         # CRUD (không business logic)
    services/             # Business logic
    napas/
      client.py           # Abstract NapasClient
      mock.py             # MockNapasClient (dev)
      real.py             # RealNapasClient (sandbox/prod)
    routes/
      auth.py             # POST /api/auth/login, /refresh, /logout, GET /me
      users.py            # GET/POST /api/users (admin)
      api_keys.py         # CRUD /api/merchant-keys (admin)
      audit.py            # GET /api/audit-logs (admin)
      webhook.py          # POST /webhook/napas/notice (IP whitelist)
      transactions.py     # GET /api/transactions
      merchants.py        # GET /api/merchants
      fees.py             # CRUD /api/fees
      reconciliation.py   # GET /api/reconciliation
      metrics.py          # GET /api/metrics/dashboard
      qr.py               # POST /api/qr/generate
      ops.py              # POST /api/ops/seed-demo
  napas_qr/               # NAPAS VietQR IBFT module (standalone)
    crc.py                # CRC-16/CCITT-FALSE (ISO 13239)
    tlv.py                # EMVCo TLV encode/parse
    builder.py            # generate_dynamic_qr()
    validators.py         # Amount + ANS validation
    test_qr.py            # 19 test cases (pytest)
    demo_real.py          # Demo chuyển khoản thật VCB
  keys/                   # RSA keys + CSR (gitignored)
  seed.py                 # DB seeder

frontend/
  src/
    contexts/AuthContext.tsx   # JWT auth state + axios interceptors
    components/
      RouteGuard.tsx           # PrivateRoute, AdminRoute
      layout/Sidebar.tsx       # Nav with RBAC visibility
      layout/TopBar.tsx        # User info + logout
    pages/
      Login.tsx, Dashboard.tsx, Transactions.tsx, Fees.tsx,
      Reconciliation.tsx, Merchants.tsx, ApiKeys.tsx,
      Users.tsx, AuditLogs.tsx, QrTest.tsx
    api/                       # Axios API clients
```

## API Endpoints

| Method | Path | Mô tả | Auth |
|--------|------|-------|------|
| POST | `/api/auth/login` | Đăng nhập → JWT | Public |
| POST | `/api/auth/refresh` | Refresh token rotation | Public |
| POST | `/api/auth/logout` | Revoke refresh token | Bearer |
| GET | `/api/auth/me` | User hiện tại | Bearer |
| GET | `/api/users` | Danh sách user | Admin |
| POST | `/api/users` | Tạo user | Admin |
| GET | `/api/merchant-keys/{merchant_id}` | API keys merchant | Admin |
| POST | `/api/merchant-keys` | Tạo API key | Admin |
| DELETE | `/api/merchant-keys/{key_id}` | Revoke API key | Admin |
| POST | `/api/merchant-keys/{key_id}/reveal` | Hiện API key (re-auth) | Admin |
| GET | `/api/audit-logs` | Nhật ký hệ thống | Admin |
| POST | `/webhook/napas/notice` | Nhận notice ACSP/ACSC/RJCT | IP whitelist |
| GET | `/api/merchants` | Danh sách merchant | Bearer |
| GET | `/api/transactions` | Sổ GD (filter, pagination) | Bearer |
| GET | `/api/fees` | Fee ledger | Bearer |
| GET | `/api/reconciliation` | Đối soát theo ngày | Bearer |
| GET | `/api/metrics/dashboard` | 6 KPI tổng hợp | Bearer |
| POST | `/api/qr/generate` | Sinh mã QR VietQR IBFT | Bearer |
| POST | `/api/ops/seed-demo` | Seed demo data | Bearer |
| POST | `/api/reconciliation/run` | Chạy đối soát thủ công | Bearer |

## Mô hình nghiệp vụ

**State machine giao dịch:**

```
INITIATED → AUTHORIZED(ACSP) → SETTLED(ACSC) → NOTIFIED/QUEUED → RECONCILED/DISPUTE
         → REJECTED(RJCT)
```

- **ACSP**: tiền chưa về, chỉ authorized
- **ACSC**: tiền đã về TK merchant, trigger thông báo
- **Mode 1 (realtime)**: ACSC → thông báo ngay
- **Mode 2 (batch 12h)**: ACSC → queue → batch gom thông báo
- **Phí**: FLAT per-txn (không %), NAPAS thu hộ → trả 1Hub theo kỳ
- **Đối soát**: so ledger 1Hub vs NAPAS report → KHỚP/LỆCH

## NAPAS APG Integration

### Sandbox Config

```
Base URL:      https://apg-stg.napas.com.vn
Simulator:     https://apg-stg.napas.com.vn/bankdemo/app
Source IP:     103.9.4.46 (whitelist webhook)
Outbound:      103.9.4.116:443
```

Endpoints: `POST {base}/apg/notification`, `POST {base}/apg/investigation`, `POST {base}/apg/reconciliation`

### CSR Flow (cert signing)

```bash
cd backend/keys
openssl genrsa -out client-privatekey.key 2048
openssl req -key client-privatekey.key -new -out client-apg-XX.csr
# Gửi nội dung CSR cho NAPAS (paste email, không gửi file .csr)
# NAPAS ký → trả cert → đặt vào keys/
chmod 600 client-privatekey.key
```

Env config:
```
NAPAS_PRIVATE_KEY_PATH=./keys/client-privatekey.key
NAPAS_CERT_PATH=./keys/napas-signed-cert.pem
```

### Test Flow qua Simulator

1. Mở firewall tới `apg-stg.napas.com.vn`
2. Truy cập Simulator: `https://apg-stg.napas.com.vn/bankdemo/app`
3. Đẩy lệnh chuyển tiền giả lập → NAPAS gửi notification về webhook 1Hub
4. Verify: webhook nhận đúng, parse payload, tạo transaction, đối soát

### QR Demo (tiền thật)

```bash
cd backend
pip install "qrcode[pil]"
python -m napas_qr.demo_real
# Quét demo_real.png bằng app NH → chuyển 2.000đ tới VCB REDACTED_ACCOUNT
```

### Cắm NAPAS thật

1. Điền env: `NAPAS_SENDER_ID`, `NAPAS_RECEIVER_ID`, `NAPAS_CLIENT_ID`, `NAPAS_CLIENT_SECRET`, `NAPAS_TOKEN_URL`
2. Đặt key + cert: `NAPAS_PRIVATE_KEY_PATH`, `NAPAS_CERT_PATH`
3. Đổi `NAPAS_CLIENT_TYPE=real` trong `.env`
4. Không cần sửa services, routes, hay frontend

## Pending — Chờ NAPAS

| Marker | Mô tả |
|--------|-------|
| `TODO[NAPAS-A1]` | Master Merchant code (2 ký tự) — đặt tên CSR |
| `TODO[NAPAS-A2]` | senderId / receiverId — header mọi thông điệp |
| `TODO[NAPAS-A3]` | OAuth2 client_id / client_secret / token URL |
| `TODO[NAPAS-B1]` | Canonical JSON rule + mẫu payload/chữ ký |
| `TODO[NAPAS-B2]` | senderDateTime vs creationDateTime |
| `TODO[NAPAS-Q2]` | Map alias 19 ký tự → block ID 38 QR |
| `TODO[NAPAS-D2]` | MCC chính thức (giáo dục) |

Grep: `grep -rn "TODO\[NAPAS-" --include="*.py" backend/`

## Bảo mật

- JWT auth + RBAC (admin/ops/viewer) trên tất cả protected routes
- AES-256-GCM encrypt API keys (reveal yêu cầu re-auth)
- RSA-2048 SHA256withRSA cho chữ ký NAPAS
- IP whitelist webhook (NAPAS source IP, X-Forwarded-For aware)
- Idempotency theo `full_order_id` (chặn double-credit)
- Audit log: LOGIN, USER_CREATED, KEY_CREATED, KEY_REVOKED, KEY_REVEALED
- Input validation toàn bộ (Pydantic)
- Ledger read-only — không endpoint nào cho sửa số tiền thủ công
- CORS chỉ mở frontend origin
- Secrets qua biến môi trường (`.env.example`)

## Tests

```bash
cd backend
python -m pytest napas_qr/test_qr.py -v   # 19 tests — QR + CRC + TLV + validation
```
