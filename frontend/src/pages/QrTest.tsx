import { useState, useEffect, type FormEvent } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { QRCodeSVG } from 'qrcode.react';
import { fetchMerchants } from '../api/merchants';
import { generateQr, type QrGenerateResponse } from '../api/qr';
import { formatVND } from '../lib/format';

export default function QrTest() {
  const { data: merchants = [] } = useQuery({
    queryKey: ['merchants'],
    queryFn: fetchMerchants,
  });

  const [merchantId, setMerchantId] = useState('');
  const [amount, setAmount] = useState('');
  const [reference, setReference] = useState('');
  const [purpose, setPurpose] = useState('');
  const [result, setResult] = useState<QrGenerateResponse | null>(null);

  useEffect(() => {
    if (merchants.length > 0 && !merchantId) {
      setMerchantId(merchants[0].id);
    }
  }, [merchants, merchantId]);

  const mutation = useMutation({
    mutationFn: generateQr,
    onSuccess: (data) => setResult(data),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const amt = parseInt(amount, 10);
    if (!amt || amt <= 0) return;
    mutation.mutate({
      merchant_id: merchantId,
      amount: amt,
      reference: reference || undefined,
      purpose: purpose || undefined,
    });
  }

  const selectedMerchant = merchants.find((m) => m.id === merchantId);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Test QR VietQR</h1>
        <p className="text-sm text-gray-500 mt-1">
          Sinh mã QR động NAPAS IBFT — dùng để test luồng thanh toán
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Form */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Tham số QR
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Merchant
              </label>
              <select
                value={merchantId}
                onChange={(e) => setMerchantId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                {merchants.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} — {m.bank_name} ({m.bank_account})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Số tiền (VND)
              </label>
              <input
                type="number"
                required
                min={2000}
                max={499999999}
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="50000"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <p className="text-xs text-gray-400 mt-1">
                Hạn mức APG: 2.000đ – 499.999.999đ
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mã tham chiếu (Order ID)
              </label>
              <input
                type="text"
                maxLength={25}
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                placeholder="ORD-001"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nội dung thanh toán
              </label>
              <input
                type="text"
                maxLength={25}
                value={purpose}
                onChange={(e) => setPurpose(e.target.value)}
                placeholder="thanh toan cafe"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {mutation.isError && (
              <div className="rounded-md bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
                {(mutation.error as { response?: { data?: { detail?: string } } })
                  ?.response?.data?.detail || 'Lỗi khi sinh QR'}
              </div>
            )}

            <button
              type="submit"
              disabled={mutation.isPending || !amount}
              className="w-full py-2.5 px-4 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {mutation.isPending ? 'Đang tạo...' : 'Tạo mã QR'}
            </button>
          </form>
        </div>

        {/* QR Result */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Kết quả
          </h2>

          {!result && !mutation.isPending && (
            <div className="flex flex-col items-center justify-center py-16 text-gray-400">
              <svg className="w-16 h-16 mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                <rect x="3" y="3" width="7" height="7" rx="1" />
                <rect x="14" y="3" width="7" height="7" rx="1" />
                <rect x="3" y="14" width="7" height="7" rx="1" />
                <rect x="14" y="14" width="3" height="3" />
                <rect x="18" y="14" width="3" height="3" />
                <rect x="14" y="18" width="3" height="3" />
                <rect x="18" y="18" width="3" height="3" />
              </svg>
              <p className="text-sm">Nhập tham số và bấm Tạo mã QR</p>
            </div>
          )}

          {result && (
            <div className="space-y-5">
              {/* QR Image */}
              <div className="flex justify-center">
                <div className="bg-white p-4 rounded-lg border-2 border-gray-100">
                  <QRCodeSVG
                    value={result.qr_string}
                    size={240}
                    level="M"
                    includeMargin
                  />
                </div>
              </div>

              {/* Info */}
              <div className="space-y-2 text-sm">
                {selectedMerchant && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Merchant</span>
                    <span className="font-medium text-gray-900">
                      {selectedMerchant.name}
                    </span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-500">Số tiền</span>
                  <span className="font-semibold text-gray-900">
                    {formatVND(result.amount)}
                  </span>
                </div>
                {result.reference && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Mã tham chiếu</span>
                    <span className="font-mono text-gray-800">
                      {result.reference}
                    </span>
                  </div>
                )}
                {result.purpose && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Nội dung</span>
                    <span className="text-gray-800">{result.purpose}</span>
                  </div>
                )}
              </div>

              {/* Raw string */}
              <div>
                <p className="text-xs font-medium text-gray-500 mb-1">
                  QR Payload (raw)
                </p>
                <div className="bg-gray-50 border border-gray-200 rounded-md p-3 relative group">
                  <code className="text-xs font-mono text-gray-700 break-all leading-relaxed">
                    {result.qr_string}
                  </code>
                  <button
                    type="button"
                    onClick={() => navigator.clipboard.writeText(result.qr_string)}
                    className="absolute top-2 right-2 px-2 py-1 text-xs rounded bg-white border border-gray-300 text-gray-600 hover:bg-gray-100 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    Copy
                  </button>
                </div>
              </div>

              <div className="rounded-md bg-amber-50 border border-amber-200 px-4 py-3 text-xs text-amber-700">
                <strong>Lưu ý:</strong> QR dùng BNB ID + Consumer ID mẫu (TODO[NAPAS-Q2]).
                Scan bằng app ngân hàng sẽ không transact thật — chỉ verify format đúng chuẩn EMVCo.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
