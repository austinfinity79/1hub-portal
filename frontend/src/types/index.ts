export interface Merchant {
  id: string;
  name: string;
  notify_mode: number; // 1=realtime, 2=batch
  fee_flat: number; // VND per txn
  bank_account: string;
  bank_name: string;
  status: string;
  created_at: string;
}

export interface Transaction {
  id: string;
  full_order_id: string;
  merchant_id: string;
  amount: number;
  state: string;
  notice_acsp_at: string | null;
  notice_acsc_at: string | null;
  notified_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Fee {
  id: string;
  txn_id: string;
  merchant_id: string;
  fee_amount: number;
  status: string; // PHAI_THU | DA_NHAN
  remitted_at: string | null;
  created_at: string;
}

export interface Reconciliation {
  id: string;
  recon_date: string;
  txn_id: string;
  ledger_amount: number;
  napas_amount: number;
  result: string; // KHOP | LECH
  created_at: string;
}

export interface Metrics {
  gmv_settled: number;
  gmv_pending: number;
  fee_receivable: number;
  fee_received: number;
  queue_pending: number;
  dispute_count: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
