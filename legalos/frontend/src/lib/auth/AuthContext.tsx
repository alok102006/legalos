import React, { createContext, useContext, useState, useEffect } from 'react';

export type UserRole = 'owner' | 'ca' | 'reviewer';

interface AuthContextType {
  role: UserRole;
  setRole: (role: UserRole) => void;
  roleName: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [role, setRoleState] = useState<UserRole>(() => {
    const saved = localStorage.getItem('legalos_fake_role');
    return (saved as UserRole) || 'owner';
  });

  const setRole = (newRole: UserRole) => {
    setRoleState(newRole);
    localStorage.setItem('legalos_fake_role', newRole);
  };

  const roleNames = {
    owner: 'Business Owner',
    ca: 'Chartered Accountant (CA)',
    reviewer: 'Legal Reviewer',
  };

  return (
    <AuthContext.Provider value={{ role, setRole, roleName: roleNames[role] }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};


// Role Switcher Dropdown Component
export const RoleSwitcher: React.FC = () => {
  const { role, setRole } = useAuth();

  return (
    <div className="flex items-center gap-2 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
      <label htmlFor="role-selector" className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
        Actor Profile:
      </label>
      <select
        id="role-selector"
        value={role}
        onChange={(e) => setRole(e.target.value as UserRole)}
        className="bg-transparent text-xs font-medium text-slate-800 border-none outline-none cursor-pointer focus:ring-0"
      >
        <option value="owner">Business Owner</option>
        <option value="ca">Chartered Accountant (CA)</option>
        <option value="reviewer">Legal Reviewer</option>
      </select>
    </div>
  );
};
