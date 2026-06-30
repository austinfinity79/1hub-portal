import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const ROLE_BADGE: Record<string, { bg: string; text: string }> = {
  admin: { bg: 'bg-purple-100', text: 'text-purple-800' },
  ops: { bg: 'bg-blue-100', text: 'text-blue-800' },
  viewer: { bg: 'bg-gray-100', text: 'text-gray-700' },
};

export default function TopBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate('/login', { replace: true });
  }

  const badge = ROLE_BADGE[user?.role ?? 'viewer'] ?? ROLE_BADGE.viewer;
  const initial = user?.username?.charAt(0).toUpperCase() ?? 'U';

  return (
    <header className="h-14 bg-white border-b border-gray-200 shadow-sm flex items-center justify-between px-6">
      <h1 className="text-lg font-semibold text-gray-800">1Hub Control Portal</h1>
      <div className="flex items-center gap-3">
        {user && (
          <>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-slate-300 flex items-center justify-center text-sm font-medium text-slate-600">
                {initial}
              </div>
              <span className="text-sm text-gray-700 font-medium">
                {user.username}
              </span>
              <span
                className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}
              >
                {user.role}
              </span>
            </div>
            <button
              type="button"
              onClick={handleLogout}
              className="ml-2 px-3 py-1.5 text-xs font-medium rounded-md border border-gray-300 text-gray-600 hover:bg-gray-100 transition-colors"
            >
              Đăng xuất
            </button>
          </>
        )}
      </div>
    </header>
  );
}
