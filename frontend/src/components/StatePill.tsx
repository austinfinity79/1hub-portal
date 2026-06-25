import { getStateInfo } from '../lib/states';

interface StatePillProps {
  state: string;
}

export default function StatePill({ state }: StatePillProps) {
  const info = getStateInfo(state);
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${info.color}`}
    >
      {info.label}
    </span>
  );
}
