import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { StudentDashboard } from './pages/StudentDashboard';
import { AdminDashboard } from './pages/AdminDashboard';
import { ReportLost } from './pages/ReportLost';
import { ReportFound } from './pages/ReportFound';
import { MatchMatrix } from './pages/MatchMatrix';
import { ClaimDesk } from './pages/ClaimDesk';
import { IoTMonitor } from './pages/IoTMonitor';
import { Analytics } from './pages/Analytics';

const MainApp: React.FC = () => {
  const { user, isLoading, isAdmin } = useAuth();
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [isRegistering, setIsRegistering] = useState<boolean>(false);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center text-slate-400 font-mono text-xs">
        INITIALIZING TRACE AI ENGINE...
      </div>
    );
  }

  if (!user) {
    return isRegistering ? (
      <Register onSwitchToLogin={() => setIsRegistering(false)} />
    ) : (
      <Login onSwitchToRegister={() => setIsRegistering(true)} />
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-['Plus_Jakarta_Sans',sans-serif]">
      <Navbar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isAdmin ? (
          <>
            {currentTab === 'admin-dashboard' && <AdminDashboard />}
            {currentTab === 'admin-claims' && <AdminDashboard />}
            {currentTab === 'iot-fleet' && <IoTMonitor />}
            {currentTab === 'analytics' && <Analytics />}
            {currentTab === 'matches' && <MatchMatrix />}
          </>
        ) : (
          <>
            {currentTab === 'dashboard' && <StudentDashboard onNavigate={setCurrentTab} />}
            {currentTab === 'report-lost' && <ReportLost onComplete={() => setCurrentTab('matches')} onBack={() => setCurrentTab('dashboard')} />}
            {currentTab === 'report-found' && <ReportFound onComplete={() => setCurrentTab('dashboard')} onBack={() => setCurrentTab('dashboard')} />}
            {currentTab === 'matches' && <MatchMatrix />}
            {currentTab === 'claims' && <ClaimDesk />}
            {currentTab === 'iot-simulator' && <IoTMonitor />}
          </>
        )}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 text-center text-xs text-slate-500 font-mono">
        TRACE AI v2.0 • AI Semantic Matching Engine & ESP32 Smart Drop Box Fleet • Ready for Hardware Connection
      </footer>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
};

export default App;
