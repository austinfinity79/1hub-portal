import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchMerchants } from '../api/merchants';
import { fetchApiKeys, createApiKey, revokeApiKey, revealApiKey } from '../api/apiKeys';
import DataTable, { type Column } from '../components/DataTable';
import { useAuth } from '../contexts/AuthContext';
import { formatDateTime } from '../lib/format';
import type { ApiKey } from '../types';

export default function ApiKeys() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const isAdmin = user?.role === 'admin';

  const [selectedMerchant, setSelectedMerchant] = useState('');

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createLabel, setCreateLabel] = useState('');
  const [createdFullKey, setCreatedFullKey] = useState<string | null>(null);
  const [copiedCreate, setCopiedCreate] = useState(false);

  const [revokeTarget, setRevokeTarget] = useState<ApiKey | null>(null);

  const [revealTarget, setRevealTarget] = useState<ApiKey | null>(null);
  const [revealPassword, setRevealPassword] = useState('');
  const [revealedKey, setRevealedKey] = useState<string | null>(null);
  const [revealError, setRevealError] = useState('');
  const [copiedReveal, setCopiedReveal] = useState(false);
  const [revealTimer, setRevealTimer] = useState(30);

  // Fetch merchants
  const { data: merchants = [] } = useQuery({
    queryKey: ['merchants'],
    queryFn: fetchMerchants,
  });

  // Auto-select first merchant
  useEffect(() => {
    if (merchants.length > 0 && !selectedMerchant) {
      setSelectedMerchant(merchants[0].id);
    }
  }, [merchants, selectedMerchant]);

  // Fetch API keys for selected merchant
  const { data: apiKeys = [], isLoading } = useQuery({
    queryKey: ['api-keys', selectedMerchant],
    queryFn: () => fetchApiKeys(selectedMerchant),
    enabled: !!selectedMerchant,
  });

  // Create mutation
  const createMut = useMutation({
    mutationFn: () => createApiKey(selectedMerchant, createLabel),
    onSuccess: (data) => {
      setCreatedFullKey(data.full_key);
      setCreateLabel('');
      queryClient.invalidateQueries({ queryKey: ['api-keys', selectedMerchant] });
    },
  });

  // Revoke mutation
  const revokeMut = useMutation({
    mutationFn: (keyId: string) => revokeApiKey(keyId),
    onSuccess: () => {
      setRevokeTarget(null);
      queryClient.invalidateQueries({ queryKey: ['api-keys', selectedMerchant] });
    },
  });

  // Reveal mutation
  const revealMut = useMutation({
    mutationFn: ({ keyId, password }: { keyId: string; password: string }) =>
      revealApiKey(keyId, password),
    onSuccess: (data) => {
      setRevealedKey(data.key);
      setRevealPassword('');
      setRevealError('');
      setRevealTimer(30);
    },
    onError: () => {
      setRevealError('Mật khẩu không đúng hoặc không thể hiện key.');
    },
  });

  // Auto-hide timer for revealed key
  useEffect(() => {
    if (!revealedKey) return;
    if (revealTimer <= 0) {
      setRevealedKey(null);
      setRevealTarget(null);
      return;
    }
    const interval = setInterval(() => setRevealTimer((t) => t - 1), 1000);
    return () => clearInterval(interval);
  }, [revealedKey, revealTimer]);

  const copyToClipboard = useCallback((text: string, setter: (v: boolean) => void) => {
    navigator.clipboard.writeText(text);
    setter(true);
    setTimeout(() => setter(false), 2000);
  }, []);

  const columns: Column<ApiKey>[] = [
    { key: 'label', header: 'Nhãn' },
    {
      key: 'key_prefix',
      header: 'Key prefix',
      render: (item) => (
        <code className="text-xs bg-gray-100 px-2 py-0.5 rounded font-mono">
          {item.key_prefix}****
        </code>
      ),
    },
    {
      key: 'is_active',
      header: 'Trạng thái',
      render: (item) =>
        item.is_active ? (
          <span className="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Active
          </span>
        ) : (
          <span className="inline-block px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
            Revoked
          </span>
        ),
    },
    {
      key: 'created_at',
      header: 'Ngày tạo',
      render: (item) => formatDateTime(item.created_at),
    },
    {
      key: 'last_used_at',
      header: 'Sử dụng lần cuối',
      render: (item) => (item.last_used_at ? formatDateTime(item.last_used_at) : '-'),
    },
    ...(isAdmin
      ? [
          {
            key: '_actions',
            header: 'Thao tác',
            render: (item: ApiKey) => (
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setRevealTarget(item);
                    setRevealedKey(null);
                    setRevealPassword('');
                    setRevealError('');
                  }}
                  className="text-xs px-2 py-1 rounded border border-gray-300 text-gray-700 hover:bg-gray-100"
                >
                  Hiện key
                </button>
                {item.is_active && (
                  <button
                    type="button"
                    onClick={() => setRevokeTarget(item)}
                    className="text-xs px-2 py-1 rounded border border-red-300 text-red-600 hover:bg-red-50"
                  >
                    Thu hồi
                  </button>
                )}
              </div>
            ),
          } as Column<ApiKey>,
        ]
      : []),
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Quản lý API Key</h1>
        {isAdmin && selectedMerchant && (
          <button
            type="button"
            onClick={() => {
              setShowCreateModal(true);
              setCreatedFullKey(null);
              setCreateLabel('');
              setCopiedCreate(false);
            }}
            className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 transition-colors"
          >
            Tạo key mới
          </button>
        )}
      </div>

      {/* Merchant selector */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Chọn Merchant
        </label>
        <select
          value={selectedMerchant}
          onChange={(e) => setSelectedMerchant(e.target.value)}
          className="w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          {merchants.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      <DataTable columns={columns} data={apiKeys} loading={isLoading} />

      {/* ===== CREATE MODAL ===== */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            {createdFullKey ? (
              <>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  API Key đã tạo thành công
                </h3>
                <p className="text-sm text-red-600 mb-3">
                  Key chỉ hiển thị một lần duy nhất. Hãy sao chép và lưu lại ngay.
                </p>
                <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-md p-3">
                  <code className="flex-1 text-sm font-mono break-all">
                    {createdFullKey}
                  </code>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(createdFullKey, setCopiedCreate)}
                    className="shrink-0 px-3 py-1 text-xs rounded border border-gray-300 bg-white hover:bg-gray-100"
                  >
                    {copiedCreate ? 'Đã sao chép' : 'Sao chép'}
                  </button>
                </div>
                <div className="mt-6 flex justify-end">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-sm font-medium rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200"
                  >
                    Đóng
                  </button>
                </div>
              </>
            ) : (
              <>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Tạo API Key mới
                </h3>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nhãn
                  </label>
                  <input
                    type="text"
                    value={createLabel}
                    onChange={(e) => setCreateLabel(e.target.value)}
                    placeholder="VD: production-key"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                {createMut.isError && (
                  <p className="text-sm text-red-600 mb-3">
                    Không thể tạo key. Vui lòng thử lại.
                  </p>
                )}
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-sm font-medium rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200"
                  >
                    Hủy
                  </button>
                  <button
                    type="button"
                    disabled={!createLabel.trim() || createMut.isPending}
                    onClick={() => createMut.mutate()}
                    className="px-4 py-2 text-sm font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {createMut.isPending ? 'Đang tạo...' : 'Tạo key'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* ===== REVOKE CONFIRM DIALOG ===== */}
      {revokeTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Thu hồi API Key
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Bạn có chắc muốn thu hồi key{' '}
              <strong>{revokeTarget.label}</strong> (
              <code className="text-xs">{revokeTarget.key_prefix}****</code>)?
              Hành động này không thể hoàn tác.
            </p>
            {revokeMut.isError && (
              <p className="text-sm text-red-600 mb-3">
                Không thể thu hồi. Vui lòng thử lại.
              </p>
            )}
            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setRevokeTarget(null)}
                className="px-4 py-2 text-sm font-medium rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200"
              >
                Hủy
              </button>
              <button
                type="button"
                disabled={revokeMut.isPending}
                onClick={() => revokeMut.mutate(revokeTarget.id)}
                className="px-4 py-2 text-sm font-medium rounded-md bg-red-600 text-white hover:bg-red-700 disabled:opacity-50"
              >
                {revokeMut.isPending ? 'Đang xử lý...' : 'Thu hồi'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ===== REVEAL KEY MODAL ===== */}
      {revealTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            {revealedKey ? (
              <>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  API Key
                </h3>
                <p className="text-xs text-gray-500 mb-3">
                  Key sẽ tự động ẩn sau {revealTimer} giây.
                </p>
                <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-md p-3">
                  <code className="flex-1 text-sm font-mono break-all">
                    {revealedKey}
                  </code>
                  <button
                    type="button"
                    onClick={() => copyToClipboard(revealedKey, setCopiedReveal)}
                    className="shrink-0 px-3 py-1 text-xs rounded border border-gray-300 bg-white hover:bg-gray-100"
                  >
                    {copiedReveal ? 'Đã sao chép' : 'Sao chép'}
                  </button>
                </div>
                <div className="mt-6 flex justify-end">
                  <button
                    type="button"
                    onClick={() => {
                      setRevealedKey(null);
                      setRevealTarget(null);
                    }}
                    className="px-4 py-2 text-sm font-medium rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200"
                  >
                    Đóng
                  </button>
                </div>
              </>
            ) : (
              <>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Xác nhận mật khẩu
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  Nhập mật khẩu của bạn để hiện key{' '}
                  <strong>{revealTarget.label}</strong>.
                </p>
                <input
                  type="password"
                  value={revealPassword}
                  onChange={(e) => setRevealPassword(e.target.value)}
                  placeholder="Mật khẩu"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 mb-3"
                />
                {revealError && (
                  <p className="text-sm text-red-600 mb-3">{revealError}</p>
                )}
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setRevealTarget(null);
                      setRevealPassword('');
                      setRevealError('');
                    }}
                    className="px-4 py-2 text-sm font-medium rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200"
                  >
                    Hủy
                  </button>
                  <button
                    type="button"
                    disabled={!revealPassword || revealMut.isPending}
                    onClick={() =>
                      revealMut.mutate({
                        keyId: revealTarget.id,
                        password: revealPassword,
                      })
                    }
                    className="px-4 py-2 text-sm font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {revealMut.isPending ? 'Đang xử lý...' : 'Hiện key'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
