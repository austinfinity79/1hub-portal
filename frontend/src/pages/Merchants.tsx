import { useQuery } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { fetchMerchants } from '../api/merchants';
import { fetchTransactions } from '../api/transactions';
import { formatVND } from '../lib/format';
import { getStateInfo } from '../lib/states';
import type { Merchant, Transaction } from '../types';

const SETTLED_STATES = ['SETTLED', 'NOTIFIED', 'RECONCILED'];

function MerchantCard({ merchant }: { merchant: Merchant }) {
  const { data: txnResponse, isLoading } = useQuery({
    queryKey: ['merchant-transactions', merchant.id],
    queryFn: () =>
      fetchTransactions({ merchant_id: merchant.id, page_size: 100 }),
  });

  const transactions: Transaction[] = txnResponse?.items ?? [];

  const totalCount = txnResponse?.total ?? transactions.length;
  const totalGMV = transactions
    .filter((txn) => SETTLED_STATES.includes(txn.state))
    .reduce((sum, txn) => sum + txn.amount, 0);

  const chartData = Object.entries(
    transactions.reduce(
      (acc, txn) => {
        const label = getStateInfo(txn.state).label;
        acc[label] = (acc[label] || 0) + txn.amount;
        return acc;
      },
      {} as Record<string, number>
    )
  ).map(([name, value]) => ({ name, value }));

  const isActive = merchant.status === 'ACTIVE';
  const notifyLabel = merchant.notify_mode === 1 ? 'Realtime' : 'Batch 12h';

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          {merchant.name}
        </h3>
        <span
          className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${
            isActive
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-600'
          }`}
        >
          {isActive ? 'Active' : merchant.status}
        </span>
      </div>

      {/* Info rows */}
      <div className="grid grid-cols-2 gap-y-2 text-sm">
        <span className="text-gray-500">Mode thông báo</span>
        <span className="text-gray-800 font-medium">{notifyLabel}</span>

        <span className="text-gray-500">Phi/GD</span>
        <span className="text-gray-800 font-medium">
          {formatVND(merchant.fee_flat)}
        </span>

        <span className="text-gray-500">Ngân hàng</span>
        <span className="text-gray-800 font-medium">
          {merchant.bank_name} &mdash; {merchant.bank_account}
        </span>
      </div>

      {/* Transaction summary */}
      <div className="flex gap-6 pt-2 border-t border-gray-100">
        <div>
          <p className="text-xs text-gray-500">Tổng GD</p>
          <p className="text-lg font-semibold text-gray-900">
            {isLoading ? '...' : totalCount}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Tổng GMV</p>
          <p className="text-lg font-semibold text-gray-900">
            {isLoading ? '...' : formatVND(totalGMV)}
          </p>
        </div>
      </div>

      {/* Bar chart */}
      {chartData.length > 0 && (
        <div className="pt-2">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(value) => formatVND(Number(value))}
              />
              <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {isLoading && (
        <p className="text-xs text-gray-400 text-center">
          Dang tai giao dich...
        </p>
      )}
    </div>
  );
}

export default function Merchants() {
  const {
    data: merchants = [],
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['merchants'],
    queryFn: fetchMerchants,
  });

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-xl font-semibold">Merchant</h2>

      {isLoading && (
        <p className="text-sm text-gray-500">Dang tai...</p>
      )}

      {isError && (
        <p className="text-sm text-red-600">
          Loi khi tai danh sach merchant.
        </p>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {merchants.map((merchant) => (
          <MerchantCard key={merchant.id} merchant={merchant} />
        ))}
      </div>
    </div>
  );
}
