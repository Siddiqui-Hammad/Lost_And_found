import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Radio, Shield, User as UserIcon, ArrowRight, Sparkles } from 'lucide-react';

export const Login: React.FC<{ onSwitchToRegister: () => void }> = ({ onSwitchToRegister }) => {
  const { login } = useAuth();
  const [roleTab, setRoleTab] = useState<'STUDENT' | 'ADMIN'>('STUDENT');
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier || !password) {
      setError('Please enter your credentials');
      return;
    }
    setLoading(true);
    setError(null);
    const ok = await login(identifier, password);
    if (!ok) {
      setError('Invalid email / roll number or password.');
      setLoading(false);
    }
  };

  const handleQuickDemo = async (type: 'student' | 'admin') => {
    setLoading(true);
    setError(null);
    if (type === 'student') {
      await login('rahul.sharma@campus.edu', 'student123');
    } else {
      await login('admin@campus.edu', 'admin123');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex h-12 w-12 bg-sky-500/20 border border-sky-500/40 rounded-2xl items-center justify-center text-sky-400 mb-4 shadow-lg shadow-sky-950">
          <Radio className="w-6 h-6 animate-pulse" />
        </div>
        <h2 className="text-3xl font-black text-slate-100 tracking-tight">TRACE <span className="text-sky-400">AI</span></h2>
        <p className="text-xs text-slate-400 mt-1">Smart AI + IoT Lost & Found Management System</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-slate-900 border border-slate-800 py-8 px-6 sm:px-10 rounded-2xl shadow-2xl space-y-6">
          {/* Role Switcher */}
          <div className="grid grid-cols-2 p-1 bg-slate-950 rounded-xl border border-slate-800">
            <button
              type="button"
              onClick={() => {
                setRoleTab('STUDENT');
                setIdentifier('rahul.sharma@campus.edu');
                setPassword('student123');
              }}
              className={`py-2 text-xs font-bold rounded-lg transition flex items-center justify-center gap-1.5 ${
                roleTab === 'STUDENT' ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <UserIcon className="w-3.5 h-3.5" /> Student Login
            </button>
            <button
              type="button"
              onClick={() => {
                setRoleTab('ADMIN');
                setIdentifier('admin@campus.edu');
                setPassword('admin123');
              }}
              className={`py-2 text-xs font-bold rounded-lg transition flex items-center justify-center gap-1.5 ${
                roleTab === 'ADMIN' ? 'bg-rose-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Shield className="w-3.5 h-3.5" /> Admin Console
            </button>
          </div>

          {error && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl text-xs">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                {roleTab === 'STUDENT' ? 'College Email or Student Roll No' : 'Administrator Email'}
              </label>
              <input
                type="text"
                placeholder={roleTab === 'STUDENT' ? 'e.g. rahul.sharma@campus.edu' : 'admin@campus.edu'}
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-sky-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
              <input
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-slate-100 placeholder-slate-600 focus:outline-none focus:border-sky-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-sky-900/30 transition"
            >
              {loading ? 'Authenticating...' : 'Sign In'} <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Demo Logins */}
          <div className="pt-4 border-t border-slate-800 space-y-2">
            <span className="text-[11px] text-slate-500 block text-center">One-Click Demonstration Logins:</span>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => handleQuickDemo('student')}
                className="p-2 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg text-xs text-sky-400 font-semibold text-center transition"
              >
                👤 Student Demo
              </button>
              <button
                type="button"
                onClick={() => handleQuickDemo('admin')}
                className="p-2 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg text-xs text-rose-400 font-semibold text-center transition"
              >
                🛡️ Admin Demo
              </button>
            </div>
          </div>

          {roleTab === 'STUDENT' && (
            <div className="text-center">
              <button
                onClick={onSwitchToRegister}
                className="text-xs text-sky-400 hover:underline"
              >
                New student? Create an account
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
