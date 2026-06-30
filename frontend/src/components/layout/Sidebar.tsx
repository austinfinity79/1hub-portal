import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
  adminOnly?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  {
    to: '/',
    label: 'Tổng quan',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
        <rect x="1" y="1" width="7" height="7" rx="1" />
        <rect x="12" y="1" width="7" height="7" rx="1" />
        <rect x="1" y="12" width="7" height="7" rx="1" />
        <rect x="12" y="12" width="7" height="7" rx="1" />
      </svg>
    ),
  },
  {
    to: '/transactions',
    label: 'Giao dịch',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
        <rect x="2" y="3" width="16" height="2" rx="1" />
        <rect x="2" y="9" width="16" height="2" rx="1" />
        <rect x="2" y="15" width="16" height="2" rx="1" />
      </svg>
    ),
  },
  {
    to: '/fees',
    label: 'Phí dịch vụ',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5">
        <circle cx="10" cy="10" r="8" />
        <line x1="10" y1="5" x2="10" y2="15" />
        <line x1="7" y1="8" x2="13" y2="8" />
        <line x1="7" y1="12" x2="13" y2="12" />
      </svg>
    ),
  },
  {
    to: '/reconciliation',
    label: 'Đối soát',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="3,11 7,15 17,5" />
        <polyline points="3,6 6,9" />
        <polyline points="10,3 14,7" />
      </svg>
    ),
  },
  {
    to: '/merchants',
    label: 'Merchant',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
        <path d="M3 7V17H17V7L15 3H5L3 7Z" fill="none" stroke="currentColor" strokeWidth="1.5" />
        <rect x="7" y="11" width="6" height="6" rx="0.5" fill="none" stroke="currentColor" strokeWidth="1.5" />
        <path d="M3 7H17" stroke="currentColor" strokeWidth="1.5" />
      </svg>
    ),
  },
  {
    to: '/qr-test',
    label: 'Test QR',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="2" width="6" height="6" rx="1" />
        <rect x="12" y="2" width="6" height="6" rx="1" />
        <rect x="2" y="12" width="6" height="6" rx="1" />
        <rect x="13" y="13" width="2" height="2" />
        <rect x="16" y="13" width="2" height="2" />
        <rect x="13" y="16" width="2" height="2" />
        <rect x="16" y="16" width="2" height="2" />
      </svg>
    ),
  },
  {
    to: '/api-keys',
    label: 'API Keys',
    adminOnly: true,
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="7" cy="10" r="3" />
        <line x1="10" y1="10" x2="18" y2="10" />
        <line x1="15" y1="7" x2="15" y2="10" />
        <line x1="18" y1="7" x2="18" y2="10" />
      </svg>
    ),
  },
  {
    to: '/users',
    label: 'Người dùng',
    adminOnly: true,
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="10" cy="6" r="3" />
        <path d="M4 17c0-3.3 2.7-6 6-6s6 2.7 6 6" />
      </svg>
    ),
  },
  {
    to: '/audit-logs',
    label: 'Nhật ký',
    adminOnly: true,
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="2" width="14" height="16" rx="2" />
        <line x1="7" y1="6" x2="13" y2="6" />
        <line x1="7" y1="10" x2="13" y2="10" />
        <line x1="7" y1="14" x2="10" y2="14" />
      </svg>
    ),
  },
];

const linkBase =
  'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors';
const linkInactive = 'text-slate-300 hover:bg-slate-800 hover:text-white';
const linkActive = 'bg-slate-700 text-white';

export default function Sidebar() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const visibleItems = NAV_ITEMS.filter(
    (item) => !item.adminOnly || isAdmin,
  );

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-60 bg-slate-900 flex flex-col z-30">
      <div className="px-5 py-5 border-b border-slate-700">
        <h1 className="text-xl font-bold text-white tracking-wide">1Hub</h1>
        <p className="text-xs text-slate-400 mt-0.5">Napas Control Portal</p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {visibleItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `${linkBase} ${isActive ? linkActive : linkInactive}`
            }
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
