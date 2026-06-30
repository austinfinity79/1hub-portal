import api from './client';
import type { ApiKey } from '../types';

export async function fetchApiKeys(merchantId: string): Promise<ApiKey[]> {
  const { data } = await api.get<ApiKey[]>(`/api/merchant-keys/${merchantId}`);
  return data;
}

export async function createApiKey(
  merchantId: string,
  label: string,
): Promise<ApiKey & { full_key: string }> {
  const { data } = await api.post<ApiKey & { full_key: string }>(
    '/api/merchant-keys',
    { merchant_id: merchantId, label },
  );
  return data;
}

export async function revokeApiKey(keyId: string): Promise<void> {
  await api.delete(`/api/merchant-keys/${keyId}`);
}

export async function revealApiKey(
  keyId: string,
  password: string,
): Promise<{ key: string }> {
  const { data } = await api.post<{ key: string }>(
    `/api/merchant-keys/${keyId}/reveal`,
    { password },
  );
  return data;
}
