import React from 'react';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyle = 'inline-flex items-center justify-center font-medium rounded transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2';
  
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white disabled:bg-blue-300 focus-visible:outline-blue-600',
    secondary: 'bg-slate-100 hover:bg-slate-200 text-slate-800 disabled:bg-slate-50 focus-visible:outline-slate-600',
    outline: 'border border-slate-300 bg-white hover:bg-slate-50 text-slate-700 disabled:bg-slate-50 focus-visible:outline-slate-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white disabled:bg-red-300 focus-visible:outline-red-600',
    ghost: 'hover:bg-slate-100 text-slate-600 disabled:bg-transparent',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-5 py-2.5 text-base',
  };

  return (
    <button
      className={`${baseStyle} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
      {children}
    </button>
  );
};
export default Button;
