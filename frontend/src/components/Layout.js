import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, TrendingUp, FileText, BarChart3, Settings, Power, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';

export const Layout = ({ children }) => {
  const location = useLocation();
  const [tradingPaused, setTradingPaused] = useState(false);

  const navItems = [
    { path: '/', icon: Activity, label: 'Dashboard' },
    { path: '/signals', icon: TrendingUp, label: 'Signals' },
    { path: '/positions', icon: FileText, label: 'Positions' },
    { path: '/history', icon: FileText, label: 'History' },
    { path: '/performance', icon: BarChart3, label: 'Performance' },
  ];

  const handleKillSwitch = () => {
    setTradingPaused(!tradingPaused);
  };

  return (
    <div className="min-h-screen bg-[#050505]">
      {/* Header */}
      <header className="border-b border-[#1F1F23] bg-[#050505] sticky top-0 z-50">
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold font-mono tracking-tight text-[#00F0FF]" data-testid="app-title">ORACLE</h1>
            <span className="text-xs text-[#52525B] uppercase tracking-wider">Autonomous Trading System</span>
          </div>
          
          <div className="flex items-center gap-3">
            {tradingPaused && (
              <div className="flex items-center gap-2 px-3 py-1.5 bg-[#FF0055]/10 border border-[#FF0055]/20 rounded-sm">
                <AlertTriangle className="w-4 h-4 text-[#FF0055]" />
                <span className="text-xs font-medium text-[#FF0055]">TRADING PAUSED</span>
              </div>
            )}
            
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button
                  size="sm"
                  className={`rounded-sm font-medium ${
                    tradingPaused 
                      ? 'bg-[#00E396]/10 border border-[#00E396]/20 text-[#00E396] hover:bg-[#00E396]/20'
                      : 'bg-[#FF0055]/10 border border-[#FF0055]/20 text-[#FF0055] hover:bg-[#FF0055]/20 kill-switch-button'
                  }`}
                  data-testid="kill-switch-button"
                >
                  <Power className="w-4 h-4 mr-2" />
                  {tradingPaused ? 'Resume Trading' : 'Kill Switch'}
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent className="bg-[#0A0A0B] border-[#1F1F23]">
                <AlertDialogHeader>
                  <AlertDialogTitle className="text-[#E4E4E7]">
                    {tradingPaused ? 'Resume Trading?' : 'Pause All Trading?'}
                  </AlertDialogTitle>
                  <AlertDialogDescription className="text-[#A1A1AA]">
                    {tradingPaused 
                      ? 'This will resume automated trading operations. Make sure market conditions are suitable.'
                      : 'This will immediately pause all trading operations and cancel pending orders. This action is reversible.'}
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel className="bg-transparent border-[#3F3F46] text-[#E4E4E7] hover:bg-[#1F1F23]">Cancel</AlertDialogCancel>
                  <AlertDialogAction 
                    onClick={handleKillSwitch}
                    className={tradingPaused ? 'bg-[#00E396] text-black hover:bg-[#00E396]/90' : 'bg-[#FF0055] text-white hover:bg-[#FF0055]/90'}
                  >
                    Confirm
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-16 border-r border-[#1F1F23] bg-[#050505] min-h-[calc(100vh-57px)] sticky top-[57px]">
          <nav className="flex flex-col items-center py-4 gap-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`w-12 h-12 flex items-center justify-center rounded-sm transition-colors ${
                    isActive
                      ? 'bg-[#00F0FF]/10 text-[#00F0FF] border border-[#00F0FF]/20'
                      : 'text-[#A1A1AA] hover:text-[#E4E4E7] hover:bg-[#1F1F23]'
                  }`}
                  title={item.label}
                  data-testid={`nav-${item.label.toLowerCase()}`}
                >
                  <Icon className="w-5 h-5" />
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 min-h-[calc(100vh-57px)]">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
