import { useState, useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import DataTable, { type Column } from '../components/DataTable';
import FilterBar, { type FilterOption } from '../components/FilterBar';
import { fetchFees } from '../api/fees';
import { fetchMerchants } from '../api/merchants';
import { formatVND, formatDate } from '../lib/format';
import type { Fee } from '../types';

const PAGE_SIZE = 20;

const FEE_STATUS_OPTIONS: FilterOption[] = [
  { value: 'PHAI_THU', label: 'Phải thu' },
  { value: 'DA_NHAN', label: 'Đã nhận' },
];

function FeeStatusPill({ status }: { status: string }) {
  if (status === 'DA_NHAN') {
    return (
      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
        Đã nhận
      </span>
    );
  }
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">
      Phải thu
    </span>
  );
}

export default function Fees() {
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [page, setPage] = useState(1);

  const { data: merchants } = useQuery({
    queryKey: ['merchants'],
    queryFn: fetchMerchants,
    staleTime: 5 * 60 * 1000,
  });

  const merchantOptions: FilterOption[] = useMemo(
    () => (merchants ?? []).map((m) => ({ value: m.id, label: m.name })),
    [merchants],
  );

  const apiParams = useMemo(() => {
    const params: Record<string, string | number> = { page, page_size: PAGE_SIZE };
    if (filters.merchant_id) params.merchant_id = filters.merchant_id;
    if (filters.status) params.status = filters.status;
    return params;
  }, [filters, page]);

  const { data, isLoading } = useQuery({
    queryKey: ['fees', apiParams],
    queryFn: () => fetchFees(apiParams as Parameters<typeof fetchFees>[0]),
  });

  const handleFilterChange = useCallback((raw: Record<string, string>) => {
    const next: Record<string, string> = {};
    if (raw.merchant) next.merchant_id = raw.merchant;
    if (raw.status) next.status = raw.status;
    setFilters(next);
    setPage(1);
  }, []);

  const columns: Column<Fee>[] = useMemo(
    () => [
      {
        key: 'txn_id',
        header: 'Mã GD',
        render: (f) => (
          <span title={f.txn_id}>
            {f.txn_id.length > 8 ? f.txn_id.slice(0, 8) + '...' : f.txn_id}
          </span>
        ),
      },
      {
        key: 'merchant_id',
        header: 'Merchant',
        render: (f) => {
          const m = merchants?.find((mer) => mer.id === f.merchant_id);
          if (m) return m.name;
          return f.merchant_id.length > 8
            ? f.merchant_id.slice(0, 8) + '...'
            : f.merchant_id;
        },
      },
      {
        key: 'fee_amount',
        header: 'Phí',
        render: (f) => <span className="text-right block">{formatVND(f.fee_amount)}</span>,
      },
      {
        key: 'status',
        header: 'Trạng thái',
        render: (f) => <FeeStatusPill status={f.status} />,
      },
      {
        key: 'remitted_at',
        header: 'Ngày nhận',
        render: (f) => (f.remitted_at ? formatDate(f.remitted_at) : '-'),
      },
      {
        key: 'created_at',
        header: 'Ngày tạo',
        render: (f) => formatDate(f.created_at),
      },
    ],
    [merchants],
  );

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-xl font-semibold">Phí dịch vụ</h2>

      <FilterBar
        merchants={merchantOptions}
        statuses={FEE_STATUS_OPTIONS}
        onFilterChange={handleFilterChange}
        showDateRange={false}
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
