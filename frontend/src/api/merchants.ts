import api from './client';
import type { Merchant } from '../types';

export async function fetchMerchants(): Promise<Merchant[]> {
  const { data } = await api.get<Merchant[]>('/api/merchants');
  return data;
}
