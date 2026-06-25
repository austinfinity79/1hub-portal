import api from './client';
import type { Metrics } from '../types';

export async function fetchMetrics(): Promise<Metrics> {
  const { data } = await api.get<Metrics>('/api/metrics');
  return data;
}
