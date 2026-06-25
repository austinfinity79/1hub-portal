import api from './client';
import type { Reconciliation } from '../types';

export async function fetchReconciliation(recon_date: string): Promise<Reconciliation[]> {
  const { data } = await api.get<Reconciliation[]>('/api/reconciliation', { params: { recon_date } });
  return data;
}

export async function runReconciliation(recon_date: string): Promise<{ date: string; total: number; matched: number; mismatched: number }> {
  const { data } = await api.post('/api/reconciliation/run', null, { params: { recon_date } });
  return data;
}

export async function runBatchNotify(): Promise<{ merchants_processed: number; notifications_sent: number }> {
  const { data } = await api.post('/api/notify/batch/run');
  return data;
}
