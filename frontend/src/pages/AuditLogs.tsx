import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchAuditLogs } from '../api/audit';
import DataTable, { type Column } from '../components/DataTable';
import { formatDateTime } from '../lib/format';
import type { AuditLog } from '../types';

const ACTION_OPTIONS = [
  { value: '', label: 'Tất cả' },
  { value: 'LOGIN', label: 'Đăng nhập' },
  { value: 'LOGIN_FAILED', label: 'Đăng nhập thất bại' },
  { value: 'USER_CREATED', label: 'Tạo user' },
  { value: 'KEY_CREATED', label: 'Tạo API key' },
  { value: 'KEY_REVOKED', label: 'Thu hồi API key' },
  { value: 'KEY_REVEALED', label: 'Hiện API key' },
];

export default function AuditLogs() {
  const [action, setAction] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const { data, isLoading } = useQuery({
    queryKey: ['audit-logs', action, page],
    queryFn: () =>
      fetchAuditLogs({
        action: action || undefined,
        page,
        page_size: pageSize,
      }),
  });

  const columns: Column<AuditLog>[] = [
    {
      key: 'created_at',
      header: 'Thời gian',
      render: (item) => formatDateTime(item.created_at),
    },
    {
      key: 'user_id',
      header: 'Người dùng',
      render: (item) => item.user_id ?? '-',
    },
    {
      key: 'action',
      header: 'Hành động',
      render: (item) => (
        <span className="inline-block px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700">
          {item.action}
        </span>
      ),
    },
    {
      key: 'resource_type',
      header: 'Tài nguyên',
      render: (item) =>
        item.resource_type
          ? `${item.resource_type}${item.resource_id ? ` #${item.resource_id}` : ''}`
          : '-',
    },
    {
      key: 'ip_address',
      header: 'IP',
      render: (item) => item.ip_address ?? '-',
    },
    {
      key: 'detail',
      header: 'Chi tiết',
      render: (item) => (
        <span className="max-w-xs truncate block" title={item.detail ?? ''}>
          {item.detail ?? '-'}
        </span>
      ),
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Nhật ký hệ thống</h1>

      {/* Filter */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Lọc theo hành động
        </label>
        <select
          value={action}
          onChange={(e) => {
            setAction(e.target.value);
            setPage(1);
          }}
          className="w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          {ACTION_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <DataTable
        columns={columns}
        data={data?.items ?? []}
        total={data?.total ?? 0}
        page={page}
        pageSize={pageSize}
        onPageChange={setPage}
        loading={isLoading}
      />
    </div>
  );
}
