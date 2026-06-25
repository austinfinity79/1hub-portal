import { useQuery } from '@tanstack/react-query';
import { fetchMetrics } from '../api/metrics';
import { fetchTransactions } from '../api/transactions';
import KpiCard from '../components/KpiCard';
import StatePill from '../components/StatePill';
import { formatVND, formatDateTime } from '../lib/format';

export default function Dashboard() {
  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
  } = useQuery({
    queryKey: ['metrics'],
    queryFn: fetchMetrics,
  });

  const {
    data: txnData,
    isLoading: txnLoading,
    error: txnError,
  } = useQuery({
    queryKey: ['transactions', 'recent'],
    queryFn: () => fetchTransactions({ page_size: 10 }),
  });

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Tổng quan</h1>

      {/* KPI Cards */}
      {metricsError && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          Không thể tải dữ liệu chỉ số. Vui lòng thử lại.
        </div>
      )}

      {metricsLoading && (
        <div className="text-gray-500">Đang tải...</div>
      )}

      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <KpiCard
            title="GMV đã settle"
            value={formatVND(metrics.gmv_settled)}
            variant="success"
          />
          <KpiCard
            title="Đang chờ settle"
            value={formatVND(metrics.gmv_pending)}
            variant="warning"
            subtitle="ACSP - Chưa về tiền"
          />
          <KpiCard
            title="Phí phải thu"
            value={formatVND(metrics.fee_receivable)}
            variant="default"
          />
          <KpiCard
            title="Phí đã nhận"
            value={formatVND(metrics.fee_received)}
            variant="success"
          />
          <KpiCard
            title="Chờ batch 12h"
            value={metrics.queue_pending.toString() + ' giao dịch'}
            variant={metrics.queue_pending > 0 ? 'warning' : 'default'}
          />
          <KpiCard
            title="Lệch đối soát"
            value={metrics.dispute_count.toString() + ' giao dịch'}
            variant={metrics.dispute_count > 0 ? 'danger' : 'default'}
          />
        </div>
      )}

      {/* Recent Transactions */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Giao dịch gần đây
        </h2>

        {txnError && (
          <div className="rounded-lg bg-red-50 p-4 text-red-700">
            Không thể tải danh sách giao dịch. Vui lòng thử lại.
          </div>
        )}

        {txnLoading && (
          <div className="text-gray-500">Đang tải...</div>
        )}

        {txnData && (
          <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Mã đơn
                  </th>
                  <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                    Số tiền
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Trạng thái
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                    Thời gian
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {txnData.items.map((txn) => (
                  <tr key={txn.id} className="hover:bg-gray-50">
                    <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900">
                      {txn.full_order_id}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-right text-gray-700">
                      {formatVND(txn.amount)}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm">
                      <StatePill state={txn.state} />
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500">
                      {formatDateTime(txn.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
