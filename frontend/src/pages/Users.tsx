import { useState, type FormEvent } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchUsers, createUser } from '../api/auth';
import DataTable, { type Column } from '../components/DataTable';
import { formatDateTime } from '../lib/format';
import type { User } from '../types';

const ROLE_BADGE: Record<string, { bg: string; text: string }> = {
  admin: { bg: 'bg-purple-100', text: 'text-purple-800' },
  ops: { bg: 'bg-blue-100', text: 'text-blue-800' },
  viewer: { bg: 'bg-gray-100', text: 'text-gray-700' },
};

export default function Users() {
  const queryClient = useQueryClient();

  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    role: 'viewer',
  });

  const { data: users = [], isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers,
  });

  const createMut = useMutation({
    mutationFn: () => createUser(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setShowModal(false);
      setForm({ username: '', email: '', password: '', role: 'viewer' });
    },
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    createMut.mutate();
  }

  const columns: Column<User>[] = [
    { key: 'username', header: 'Tên đăng nhập' },
    { key: 'email', header: 'Email' },
    {
      key: 'role',
      header: 'Vai trò',
      render: (item) => {
        const badge = ROLE_BADGE[item.role] ?? ROLE_BADGE.viewer;
        return (
          <span
            className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}
          >
            {item.role}
          </span>
        );
      },
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
            Inactive
          </span>
        ),
    },
    {
      key: 'created_at',
      header: 'Ngày tạo',
      render: (item) => formatDateTime(item.created_at),
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Quản lý người dùng</h1>
        <button
          type="button"
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 transition-colors"
        >
          Tạo user
        </button>
      </div>

      <DataTable columns={columns} data={users} loading={isLoading} />

      {/* CREATE USER MODAL */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Tạo người dùng mới
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tên đăng nhập
                </label>
                <input
                  type="text"
                  required
                  value={form.username}
                  onChange={(e) => setForm({ ...form, username: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mật khẩu
                </label>
                <input
                  type="password"
                  required
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Vai trò
                </label>
                <select
                  value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="viewer">Viewer</option>
                  <option value="ops">Ops</option>
                  <option value="admin">Admin</option>
                </select>
              </div>

              {createMut.isError && (
                <p className="text-sm text-red-600">
                  Không thể tạo user. Vui lòng thử lại.
                </p>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm font-medium rounded-md bg-gray-100 text-gray-700 hover:bg-gray-200"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={createMut.isPending}
                  className="px-4 py-2 text-sm font-medium rounded-md bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {createMut.isPending ? 'Đang tạo...' : 'Tạo user'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
