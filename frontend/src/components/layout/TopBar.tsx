export default function TopBar() {
  return (
    <header className="h-14 bg-white border-b border-gray-200 shadow-sm flex items-center justify-between px-6">
      <h1 className="text-lg font-semibold text-gray-800">1Hub Control Portal</h1>
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-slate-300 flex items-center justify-center text-sm font-medium text-slate-600">
          A
        </div>
        <span className="text-sm text-gray-600">Admin</span>
      </div>
    </header>
  );
}
