import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from '@/pages/Dashboard';
import Signals from '@/pages/Signals';
import Positions from '@/pages/Positions';
import TradeHistory from '@/pages/TradeHistory';
import Performance from '@/pages/Performance';
import Layout from '@/components/Layout';
import { Toaster } from '@/components/ui/sonner';
import '@/App.css';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/signals" element={<Signals />} />
          <Route path="/positions" element={<Positions />} />
          <Route path="/history" element={<TradeHistory />} />
          <Route path="/performance" element={<Performance />} />
        </Routes>
      </Layout>
      <Toaster position="bottom-right" theme="dark" />
    </BrowserRouter>
  );
}

export default App;
