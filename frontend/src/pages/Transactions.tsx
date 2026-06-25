import { useState, useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import DataTable, { type Column } from '../components/DataTable';
import FilterBar, { type FilterOption } from '../components/FilterBar';
import StatePill from '../components/StatePill';
import { fetchTransactions } from '../api/transactions';
import { fetchMerchants } from '../api/merchants';
import { formatVND, formatDateTime } from '../lib/format';
import { getStateInfo } from '../lib/states';
import type { Transaction } from '../types';

const PAGE_SIZE = 20;

const STATE_KEYS = [
  'INITIATED',
  'AUTHORIZED',
  'SETTLED',
  'QUEUED',
  'NOTIFIED',
  'RECONCILED',
  'DISPUTE',
  'REJECTED',
] as const;

function convertDate(yyyymmdd: string): string {
  // YYYY-MM-DD -> dd/mm/yyyy
  const [y, m, d] = yyyymmdd.split('-');
  return `${d}/${m}/${y}`;
}

export default function Transactions() {
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [page, setPage] = useState(1);

  // Merchant list for dropdown
  const { data: merchants } = useQuery({
    queryKey: ['merchants'],
    queryFn: fetchMerchants,
    staleTime: 5 * 60 * 1000,
  });

  const merchantOptions: FilterOption[] = useMemo(
    () => (merchants ?? []).map((m) => ({ value: m.id, label: m.name })),
    [merchants],
  );

  const statusOptions: FilterOption[] = useMemo(
    () => STATE_KEYS.map((key) => ({ value: key, label: getStateInfo(key).label })),
    [],
  );

  // Build API params
  const apiParams = useMemo(() => {
    const params: Record<string, string | number> = { page, page_size: PAGE_SIZE };
    if (filters.merchant_id) params.merchant_id = filters.merchant_id;
    if (filters.state) params.state = filters.state;
    if (filters.date_from) params.date_from = filters.date_from;
    if (filters.date_to) params.date_to = filters.date_to;
    return params;
  }, [filters, page]);

  const { data, isLoading } = useQuery({
    queryKey: ['transactions', apiParams],
    queryFn: () =>
      fetchTransactions(apiParams as Parameters<typeof fetchTransactions>[0]),
  });

  const handleFilterChange = useCallback((raw: Record<string, string>) => {
    const next: Record<string, string> = {};
    if (raw.merchant) next.merchant_id = raw.merchant;
    if (raw.status) next.state = raw.status;
    if (raw.dateFrom) next.date_from = convertDate(raw.dateFrom);
    if (raw.dateTo) next.date_to = convertDate(raw.dateTo);
    setFilters(next);
    setPage(1);
  }, []);

  const columns: Column<Transaction>[] = useMemo(
    () => [
      {
        key: 'full_order_id',
        header: 'Mã đơn',
        render: (t) => <span className="font-medium">{t.full_order_id}</span>,
      },
      {
        key: 'amount',
        header: 'Số tiền',
        render: (t) => <span className="text-right block">{formatVND(t.amount)}</span>,
      },
      {
        key: 'state',
        header: 'Trạng thái',
        render: (t) => <StatePill state={t.state} />,
      },
      {
        key: 'notice_acsp_at',
        header: 'ACSP',
        render: (t) => (t.notice_acsp_at ? formatDateTime(t.notice_acsp_at) : '-'),
      },
      {
        key: 'notice_acsc_at',
        header: 'ACSC',
        render: (t) => (t.notice_acsc_at ? formatDateTime(t.notice_acsc_at) : '-'),
      },
      {
        key: 'created_at',
        header: 'Thời gian',
        render: (t) => formatDateTime(t.created_at),
      },
    ],
    [],
  );

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-xl font-semibold">Giao dịch</h2>

      <FilterBar
        merchants={merchantOptions}
        statuses={statusOptions}
        onFilterChange={handleFilterChange}
        showDateRange
      />

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        total={data?.total ?? 0}
        page={page}
        pageSize={PAGE_SIZE}
        onPageChange={setPage}
        loading={isLoading}
      />
    </div>
  );
}
