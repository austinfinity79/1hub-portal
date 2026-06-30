import api from './client';

export interface QrGenerateRequest {
  merchant_id: string;
  amount: number;
  reference?: string;
  purpose?: string;
}

export interface QrGenerateResponse {
  qr_string: string;
  amount: number;
  reference: string | null;
  purpose: string | null;
}

export async function generateQr(data: QrGenerateRequest): Promise<QrGenerateResponse> {
  const { data: result } = await api.post<QrGenerateResponse>('/api/qr/generate', data);
  return result;
}
