import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import DataTable, { type Column } from '../components/DataTable';
import { fetchReconciliation, runReconciliation, runBatchNotify } from '../api/reconciliation';
import { formatVND, formatDate } from '../lib/format';
import type { Reconciliation as ReconType } from '../types';

function toApiDate(yyyy_mm_dd: string): string {
  const [y, m, d] = yyyy_mm_dd.split('-');
  return `${d}/${m}/${y}`;
}

function todayISO(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

const columns: Column<ReconType>[] = [
  {
    key: 'txn_id',
    header: 'Mã GD',
    render: (item) => (
      <span className="font-mono text-xs">
        {(item.txn_id as string).substring(0, 8)}...
      </span>
    ),
  },
  {
    key: 'recon_date',
    header: 'Ngày',
    render: (item) => formatDate(item.recon_date as string),
  },
  {
    key: 'ledger_amount',
    header: 'Ledger (1Hub)',
    render: (item) => formatVND(item.ledger_amount as number),
  },
  {
    key: 'napas_amount',
    header: 'Napas',
    render: (item) => formatVND(item.napas_amount as number),
  },
  {
    key: 'result',
    header: 'Kết quả',
    render: (item) => {
      const isMatch = item.result === 'KHOP';
      return (
        <span
          className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
            isMatch
              ? 'bg-emerald-100 text-emerald-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {isMatch ? 'Khớp' : 'Lệch'}
        </span>
      );
    },
  },
  {
    key: 'diff',
    header: 'Chênh lệch',
    render: (item) => {
      const diff = Math.abs(
        (item.ledger_amount as number) - (item.napas_amount as number)
      );
      return diff === 0 ? '-' : formatVND(diff);
    },
  },
];

export default function Reconciliation() {
  const queryClient = useQueryClient();
  const [date, setDate] = useState(todayISO());
  const [message, setMessage] = useState<string | null>(null);

  const apiDate = toApiDate(date);

  const { data: reconData = [], isLoading } = useQuery({
    queryKey: ['reconciliation', apiDate],
    queryFn: () => fetchReconciliation(apiDate),
  });

  const reconMutation = useMutation({
    mutationFn: () => runReconciliation(apiDate),
    onSuccess: (result) => {
      setMessage(
        `Đối soát xong: ${result.matched} khớp, ${result.mismatched} lệch`
      );
      queryClient.invalidateQueries({ queryKey: ['reconciliation', apiDate] });
    },
    onError: () => setMessage('Lỗi khi chạy đối soát'),
  });

  const batchMutation = useMutation({
    mutationFn: runBatchNotify,
    onSuccess: (result) => {
      setMessage(`Batch: ${result.notifications_sent} thông báo đã gửi`);
    },
    onError: () => setMessage('Lỗi khi chạy batch'),
  });

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-xl font-semibold">Đối soát</h2>

      {/* Top action bar */}
      <div className="flex flex-wrap items-center gap-4">
        <input
          type="date"
          value={date}
          onChange={(e) => {
            setDate(e.target.value);
            setMessage(null);
          }}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="button"
          onClick={() => reconMutation.mutate()}
          disabled={reconMutation.isPending}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {reconMutation.isPending ? 'Đang chạy...' : 'Chạy đối soát'}
        </button>
        <button
          type="button"
          onClick={() => batchMutation.mutate()}
          disabled={batchMutation.isPending}
          className="px-4 py-2 bg-white border border-gray-300 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {batchMutation.isPending ? 'Đang chạy...' : 'Chạy batch 12h'}
        </button>

        {message && (
          <span className="text-sm font-medium text-gray-700 bg-gray-100 px-3 py-2 rounded-lg">
            {message}
          </span>
        )}
      </div>

      {/* Reconciliation table */}
      <DataTable
        columns={columns}
        data={reconData}
        total={reconData.length}
        loading={isLoading}
      />
    </div>
  );
}
