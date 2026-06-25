interface StateInfo {
  label: string;
  color: string; // Tailwind bg + text classes
}

const STATE_MAP: Record<string, StateInfo> = {
  INITIATED: { label: 'Khởi tạo', color: 'bg-gray-100 text-gray-700' },
  AUTHORIZED: { label: 'Chưa về tiền', color: 'bg-amber-100 text-amber-800' },
  SETTLED: { label: 'Đã về', color: 'bg-green-100 text-green-800' },
  QUEUED: { label: 'Chờ batch', color: 'bg-blue-100 text-blue-700' },
  NOTIFIED: { label: 'Đã thông báo', color: 'bg-emerald-100 text-emerald-800' },
  RECONCILED: { label: 'Đã đối soát', color: 'bg-teal-100 text-teal-800' },
  DISPUTE: { label: 'Lệch', color: 'bg-red-100 text-red-800' },
  REJECTED: { label: 'Từ chối', color: 'bg-red-50 text-red-600' },
};

export function getStateInfo(state: string): StateInfo {
  return STATE_MAP[state] || { label: state, color: 'bg-gray-100 text-gray-600' };
}
