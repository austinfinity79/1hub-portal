# 1Hub Control Portal

Dashboard giám sát dòng tiền Napas cho merchant. 1Hub **KHÔNG** giữ tiền — chỉ nhận notice từ Napas, ghi ledger, thông báo merchant, đối soát.

## Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0, SQLite, Pydantic v2
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS v4, TanStack Query, recharts
- **Napas API**: Mock — chưa có spec thật

## Chạy nhanh

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py          # seed 3 merchant + 20 txn
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --port 5173
```

Mở http://localhost:5173 — proxy tự động tới backend :8000.

### Docker Compose (cả 2 cùng lúc)

```bash
docker compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## Cấu trúc dự án

```
1hub-portal/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, lifespan
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # SQLAlchemy engine, session, Base
│   │   ├── models/              # 5 ORM models
│   │   ├── schemas/             # Pydantic request/response
│   │   ├── repositories/        # CRUD thuần (không business logic)
│   │   ├── services/            # TOÀN BỘ business logic
│   │   ├── napas/               # Adapter cổng Napas (mock + real)
│   │   ├── routes/              # API endpoints (thin)
│   │   └── core/                # Security, idempotency, exceptions
│   ├── seed.py                  # Seed data demo
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/                 # Axios API client
        ├── types/               # TypeScript types
        ├── lib/                 # format, states
        ├── components/          # KpiCard, StatePill, DataTable, FilterBar
        └── pages/               # Dashboard, Transactions, Fees, Reconciliation, Merchants
```

## API Endpoints

| Method | Path | Mô tả |
|--------|------|-------|
| POST | `/webhook/napas/notice` | Nhận notice ACSP/ACSC/RJCT |
| GET | `/api/merchants` | Danh sách merchant |
| GET | `/api/transactions` | Sổ GD (filter, pagination) |
| GET | `/api/transactions/{id}` | Chi tiết GD |
| GET | `/api/fees` | Fee ledger |
| GET | `/api/reconciliation` | Kết quả đối soát theo ngày |
| GET | `/api/metrics` | 6 KPI tổng hợp |
| POST | `/api/reconciliation/run` | Chạy đối soát thủ công |
| POST | `/api/notify/batch/run` | Chạy batch thông báo 12h |

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
- **Phí**: FLAT per-txn (không %), Napas thu hộ → trả 1Hub theo kỳ
- **Đối soát**: so ledger 1Hub vs Napas report → KHỚP/LỆCH

## Cắm Napas thật

Khi có spec Napas, chỉ cần:

1. Implement `backend/app/napas/real.py` — class `RealNapasClient` (đã có skeleton)
2. Đổi `NAPAS_CLIENT_TYPE=real` trong `.env`
3. Cập nhật inject dependency trong config/main

Tìm tất cả điểm cần sửa: `grep -r "TODO\[NAPAS\]" backend/`

**KHÔNG cần** sửa services, routes, hay frontend.

## Bảo mật

- Verify chữ ký webhook (mock pass, vị trí đúng tại `core/security.py`)
- Idempotency theo `full_order_id` (chặn double-credit)
- Input validation toàn bộ (Pydantic)
- Ledger read-only — không endpoint nào cho sửa số tiền thủ công
- CORS chỉ mở frontend origin
- Secrets qua biến môi trường (`.env.example`)
- JWT auth middleware: chừa hook, chưa implement (`# TODO` trong `main.py`)

## MVP vs Cần làm tiếp

| Đã có (MVP) | Cần thêm khi production |
|-------------|------------------------|
| Mock Napas client | Real Napas client |
| SQLite | PostgreSQL |
| Không auth | JWT + RBAC |
| Manual batch/recon trigger | Cron job (APScheduler / Celery) |
| Seed data | Real webhook integration |
| Single-process | Docker + load balancer |
