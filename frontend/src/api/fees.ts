import api from './client';
import type { Fee, PaginatedResponse } from '../types';

interface FeeFilters {
  status?: string;
  merchant_id?: string;
  page?: number;
  page_size?: number;
}

export async function fetchFees(filters: FeeFilters = {}): Promise<PaginatedResponse<Fee>> {
  const { data } = await api.get<PaginatedResponse<Fee>>('/api/fees', { params: filters });
  return data;
}
