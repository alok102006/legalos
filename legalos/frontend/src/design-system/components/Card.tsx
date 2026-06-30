import React from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  className?: string;
  footer?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  className = '',
  footer,
}) => {
  return (
    <div className={`bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden flex flex-col ${className}`}>
      {(title || subtitle) && (
        <div className="px-5 py-4 border-b border-slate-100">
          {title && <h3 className="text-base font-semibold leading-6 text-slate-900">{title}</h3>}
          {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
        </div>
      )}
      <div className="px-5 py-5 flex-1">{children}</div>
      {footer && (
        <div className="bg-slate-50 px-5 py-3 border-t border-slate-100 flex items-center justify-end text-sm">
          {footer}
        </div>
      )}
    </div>
  );
};
export default Card;
