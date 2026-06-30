/**
 * Design system tokens defining colors, spacing, typography and scales.
 * Unified theme structure used across all workspace modules.
 */
export const tokens = {
  colors: {
    brand: {
      light: '#f0f4ff',
      primary: '#3b82f6',
      primaryHover: '#2563eb',
      dark: '#1e3a8a',
      background: '#f8fafc',
      slateDark: '#0f172a'
    },
    risk: {
      low: '#10b981',     // Green
      lowBg: '#ecfdf5',
      lowText: '#065f46',
      medium: '#f59e0b',  // Yellow
      mediumBg: '#fffbeb',
      mediumText: '#92400e',
      high: '#ef4444',    // Red
      highBg: '#fef2f2',
      highText: '#991b1b',
      none: '#64748b',
      noneBg: '#f1f5f9',
      noneText: '#334155'
    }
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px'
  },
  radius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
    full: '9999px'
  },
  typography: {
    fontFamily: 'Inter, system-ui, sans-serif',
    sizes: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      xxl: '1.5rem'
    }
  }
}
