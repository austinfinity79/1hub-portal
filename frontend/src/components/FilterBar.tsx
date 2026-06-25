import { useState, useCallback } from 'react';

export interface FilterOption {
  value: string;
  label: string;
}

interface FilterBarProps {
  merchants?: FilterOption[];
  statuses?: FilterOption[];
  onFilterChange: (filters: Record<string, string>) => void;
  showDateRange?: boolean;
}

export default function FilterBar({
  merchants,
  statuses,
  onFilterChange,
  showDateRange = true,
}: FilterBarProps) {
  const [filters, setFilters] = useState<Record<string, string>>({});

  const updateFilter = useCallback(
    (key: string, value: string) => {
      setFilters((prev) => ({ ...prev, [key]: value }));
    },
    [],
  );

  const handleSubmit = useCallback(() => {
    onFilterChange(filters);
  }, [filters, onFilterChange]);

  const selectClass =
    'border border-gray-300 rounded px-3 py-1.5 text-sm bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:border-transparent';
  const inputClass =
    'border border-gray-300 rounded px-3 py-1.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-slate-400 focus:border-transparent';

  return (
    <div className="flex flex-wrap items-center gap-3">
      {merchants && merchants.length > 0 && (
        <select
          className={selectClass}
          value={filters.merchant ?? ''}
          onChange={(e) => updateFilter('merchant', e.target.value)}
        >
          <option value="">Tất cả merchant</option>
          {merchants.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
      )}

      {statuses && statuses.length > 0 && (
        <select
          className={selectClass}
          value={filters.status ?? ''}
          onChange={(e) => updateFilter('status', e.target.value)}
        >
          <option value="">Tất cả trạng thái</option>
          {statuses.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      )}

      {showDateRange && (
        <>
          <input
            type="date"
            className={inputClass}
            value={filters.dateFrom ?? ''}
            onChange={(e) => updateFilter('dateFrom', e.target.value)}
          />
          <span className="text-sm text-gray-400">-</span>
          <input
            type="date"
            className={inputClass}
            value={filters.dateTo ?? ''}
            onChange={(e) => updateFilter('dateTo', e.target.value)}
          />
        </>
      )}

      <button
        type="button"
        onClick={handleSubmit}
        className="px-4 py-1.5 rounded bg-slate-800 text-white text-sm font-medium hover:bg-slate-700 transition-colors"
      >
        Lọc
      </button>
    </div>
  );
}
