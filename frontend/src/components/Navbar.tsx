import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Radio, Bell, LogOut, Shield, User as UserIcon } from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setCurrentTab }) => {
  const { user, logout, isAdmin } = useAuth();

  const studentTabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'report-lost', label: 'Report Lost' },
    { id: 'report-found', label: 'Report Found' },
    { id: 'matches', label: 'AI Matches' },
    { id: 'claims', label: 'My Claims' },
    { id: 'iot-simulator', label: 'IoT Simulator' },
  ];

  const adminTabs = [
    { id: 'admin-dashboard', label: 'Admin Console' },
    { id: 'admin-claims', label: 'Claims Review' },
    { id: 'iot-fleet', label: 'IoT Box Fleet' },
    { id: 'analytics', label: 'Analytics' },
    { id: 'matches', label: 'Global Match Matrix' },
  ];

  const tabs = isAdmin ? adminTabs : studentTabs;

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3 cursor-pointer" onClick={() => setCurrentTab(isAdmin ? 'admin-dashboard' : 'dashboard')}>
            <div className="h-9 w-9 bg-sky-500/20 border border-sky-500/40 rounded-xl flex items-center justify-center text-sky-400">
              <Radio className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <span className="text-lg font-black tracking-wider text-slate-100">TRACE <span className="text-sky-400">AI</span></span>
              <span className="hidden sm:inline-block ml-2 text-[10px] bg-slate-800 border border-slate-700 text-slate-400 px-2 py-0.5 rounded-full font-mono">
                AI + IoT CAMPUS
              </span>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="hidden md:flex space-x-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setCurrentTab(tab.id)}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition ${
                  currentTab === tab.id
                    ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>

          {/* User Badge & Actions */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex flex-col items-end">
              <span className="text-xs font-bold text-slate-200">{user?.name}</span>
              <span className="text-[10px] font-mono text-slate-500">
                {isAdmin ? 'CAMPUS ADMIN' : user?.student_id || 'STUDENT'}
              </span>
            </div>
            <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
              {isAdmin ? <Shield className="w-4 h-4 text-rose-400" /> : <UserIcon className="w-4 h-4 text-sky-400" />}
            </div>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-800 rounded-lg transition"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};
