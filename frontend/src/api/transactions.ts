import api from './client';
import type { Transaction, PaginatedResponse } from '../types';

interface TxnFilters {
  merchant_id?: string;
  state?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
}

export async function fetchTransactions(filters: TxnFilters = {}): Promise<PaginatedResponse<Transaction>> {
  const { data } = await api.get<PaginatedResponse<Transaction>>('/api/transactions', { params: filters });
  return data;
}

export async function fetchTransaction(id: string): Promise<Transaction> {
  const { data } = await api.get<Transaction>(`/api/transactions/${id}`);
  return data;
}
