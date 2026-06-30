import api from './client';
import type { AuditLog, PaginatedResponse } from '../types';

export async function fetchAuditLogs(
  params?: { action?: string; page?: number; page_size?: number },
): Promise<PaginatedResponse<AuditLog>> {
  const { data } = await api.get<PaginatedResponse<AuditLog>>('/api/audit-logs', { params });
  return data;
}
