import React from 'react';
import { AlertOctagon, AlertTriangle, ShieldCheck, HelpCircle } from 'lucide-react';

interface RiskBadgeProps {
  score: number;
  riskType?: string;
  className?: string;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  score,
  riskType = 'none',
  className = '',
}) => {
  // Determine risk level based on score
  let level: 'low' | 'medium' | 'high' | 'none' = 'none';
  if (score > 0) {
    if (score < 30) level = 'low';
    else if (score < 70) level = 'medium';
    else level = 'high';
  } else if (riskType && riskType !== 'none') {
    // If score is 0 but we have a risk type, default to low or medium
    level = 'low';
  }

  const styles = {
    high: {
      bg: 'bg-red-50 text-red-700 border-red-200',
      icon: <AlertOctagon className="w-3.5 h-3.5 mr-1" aria-hidden="true" />,
      label: 'High Risk',
    },
    medium: {
      bg: 'bg-amber-50 text-amber-700 border-amber-200',
      icon: <AlertTriangle className="w-3.5 h-3.5 mr-1" aria-hidden="true" />,
      label: 'Medium Risk',
    },
    low: {
      bg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      icon: <ShieldCheck className="w-3.5 h-3.5 mr-1" aria-hidden="true" />,
      label: 'Low Risk',
    },
    none: {
      bg: 'bg-slate-50 text-slate-600 border-slate-200',
      icon: <HelpCircle className="w-3.5 h-3.5 mr-1 text-slate-400" aria-hidden="true" />,
      label: 'No Risk',
    },
  };

  const current = styles[level];

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded border text-xs font-semibold ${current.bg} ${className}`}
      title={`Risk score: ${score}/100, Type: ${riskType}`}
    >
      {current.icon}
      <span>{current.label} ({score})</span>
    </span>
  );
};
export default RiskBadge;
