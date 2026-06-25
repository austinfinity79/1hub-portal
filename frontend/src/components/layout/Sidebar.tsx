import { NavLink } from 'react-router-dom';

const NAV_ITEMS = [
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
];

const linkBase =
  'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors';
const linkInactive = 'text-slate-300 hover:bg-slate-800 hover:text-white';
const linkActive = 'bg-slate-700 text-white';

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 bottom-0 w-60 bg-slate-900 flex flex-col z-30">
      <div className="px-5 py-5 border-b border-slate-700">
        <h1 className="text-xl font-bold text-white tracking-wide">1Hub</h1>
        <p className="text-xs text-slate-400 mt-0.5">Napas Control Portal</p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => (
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
