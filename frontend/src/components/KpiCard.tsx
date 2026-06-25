interface KpiCardProps {
  title: string;
  value: string;
  subtitle?: string;
  variant?: 'default' | 'warning' | 'success' | 'danger';
}

const BORDER_COLORS: Record<NonNullable<KpiCardProps['variant']>, string> = {
  default: '#94a3b8',
  warning: '#f59e0b',
  success: '#10b981',
  danger: '#ef4444',
};

export default function KpiCard({
  title,
  value,
  subtitle,
  variant = 'default',
}: KpiCardProps) {
  return (
    <div
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
      style={{ borderLeftWidth: '4px', borderLeftColor: BORDER_COLORS[variant] }}
    >
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
        {title}
      </p>
      <p className="mt-1 text-2xl font-bold text-gray-900">{value}</p>
      {subtitle && (
        <p className="mt-1 text-xs text-gray-400">{subtitle}</p>
      )}
    </div>
  );
}
