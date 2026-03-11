# ORACLE - Autonomous AI Trading System

An advanced autonomous trading platform that generates consistent alpha through multi-modal analysis, predictive modeling, and intelligent execution.

## 🚀 System Architecture

ORACLE is built with a comprehensive multi-layer AI architecture designed for robust trading decisions:

### Core Modules

#### 1. Data Ingestion Engine
- **Market Data**: Real-time price, volume, and OHLCV data via yfinance
- **Sentiment Analysis**: AI-powered news and social media sentiment using GPT-5.2
- **Paper Trading Integration**: Alpaca paper trading API for risk-free testing

#### 2. AI Analysis Layers

**Layer A - Technical Analysis AI**
- 50+ technical indicators (RSI, MACD, Bollinger Bands, ATR, ADX, OBV)
- Multi-timeframe analysis (1m, 5m, 15m, 1h, 4h, 1D, 1W)
- Automated pattern detection
- Support/resistance mapping

**Layer B - Sentiment & NLP AI**
- GPT-5.2 powered sentiment analysis (-100 to +100 scale)
- Entity extraction and impact magnitude assessment
- Real-time news sentiment scoring
- Trading recommendation generation

**Layer C - Signal Fusion Engine**
- Bayesian ensemble combining all AI layers
- Minimum 72% confidence threshold for trades
- Signal strength scoring (1-10 scale)
- Automatic conflict resolution

#### 3. Risk Management System

**Non-Negotiable Safety Rules:**
- Position sizing via Kelly Criterion (0.25x fractional)
- Max single position: 5% of portfolio
- Daily loss limit: -2% of total equity (auto-pause)
- Weekly drawdown limit: -5% (requires review)
- Dynamic ATR-based trailing stops
- Correlation-aware portfolio construction

#### 4. Performance Tracking
- Real-time P&L monitoring (daily, weekly, monthly, all-time)
- Equity curve visualization
- Risk metrics (Sharpe ratio, max drawdown, win rate)
- Trade logging with AI reasoning

## 🎨 Professional Trading Terminal UI

**Design System:**
- **Theme**: Cyber-Professional Dark (Trading Terminal Style)
- **Colors**: 
  - Background: Deep Void (#050505)
  - Primary: Electric Blue (#00F0FF)
  - Buy Signal: Neon Green (#00E396)
  - Sell Signal: Red (#FF0055)
- **Typography**: 
  - JetBrains Mono for all numerical data
  - IBM Plex Sans for UI labels
- **Layout**: High-density Bento Grid for maximum information

## 🏗️ Tech Stack

**Backend:**
- FastAPI (Python)
- MongoDB (data storage)
- yfinance (market data)
- Alpaca Trading API (paper trading)
- scikit-learn, LightGBM (ML models)
- emergentintegrations (LLM integration)

**Frontend:**
- React 19
- Tailwind CSS
- Shadcn/UI components
- Recharts (data visualization)
- Lucide React (icons)

**AI/ML:**
- GPT-5.2 (sentiment analysis via Emergent LLM key)
- Technical analysis algorithms
- Signal fusion with Bayesian methods

## 📊 Key Features

### Dashboard
- Live P&L tracking with equity curve
- Active positions monitoring
- AI signal feed with confidence scores
- Risk metrics visualization
- AI Brain status visualization

### AI Signals Page
- Real-time multi-layer analysis for watchlist stocks
- Technical + Sentiment layer breakdown
- Trading recommendations with reasoning
- Position sizing suggestions

### Positions Page
- Active positions with real-time P&L
- Entry/exit price tracking
- Unrealized gains/losses

### Performance Analytics
- Comprehensive performance metrics
- Equity curve over time
- Win rate and trade statistics
- Risk-adjusted return metrics

### Kill Switch
- Emergency pause button (always visible)
- Confirmation dialog for safety
- Immediately stops all trading operations

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB
- Alpaca API keys (optional - runs in mock mode by default)

### Environment Variables

**Backend (.env):**
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=oracle_trading
EMERGENT_LLM_KEY=sk-emergent-xxxxx
```

**Frontend (.env):**
```env
REACT_APP_BACKEND_URL=https://your-app.preview.emergentagent.com
```

### Installation

1. **Install Backend Dependencies:**
```bash
cd /app/backend
pip install -r requirements.txt
```

2. **Install Frontend Dependencies:**
```bash
cd /app/frontend
yarn install
```

3. **Start the System:**
Backend and frontend are managed by supervisor and start automatically.

## 📡 API Endpoints

### Health & Account
- `GET /api/health` - System health check
- `GET /api/account` - Account information

### Market Data
- `GET /api/market-data/{symbol}` - Historical OHLCV data
- `GET /api/quotes?symbols=AAPL,MSFT` - Current quotes
- `GET /api/technical-analysis/{symbol}` - Technical indicators

### AI Signals
- `GET /api/signals/{symbol}` - Fused AI signals with recommendations
- `GET /api/sentiment-analysis/{symbol}` - Sentiment analysis

### Trading
- `GET /api/positions` - Active positions
- `GET /api/orders` - Order history
- `GET /api/performance` - Performance metrics

## 🔒 Security Features

1. **Kill Switch**: Emergency trading pause with confirmation
2. **Risk Limits**: Automated circuit breakers
3. **Position Sizing**: Kelly Criterion prevents over-leverage
4. **Mock Mode**: Safe testing without real money
5. **Environment Variables**: No hardcoded credentials

## 📈 Current Status

**Phase 1 Complete:**
✅ Data pipeline with yfinance integration
✅ Technical analysis layer (50+ indicators)
✅ Sentiment analysis layer (GPT-5.2)
✅ Signal fusion engine
✅ Risk management framework
✅ Alpaca paper trading integration (mock mode)
✅ Professional trading terminal UI
✅ Real-time dashboard with equity curve
✅ AI brain visualization
✅ Performance analytics

**Running in Mock Mode:**
- System operates with simulated $100,000 paper account
- All features functional without API keys
- Ready for real paper trading when Alpaca keys added

## 🎯 Next Steps (Future Phases)

### Phase 2: Enhanced AI Layers
- Quantitative/statistical analysis layer
- Macro & intermarket analysis layer
- Deep learning price prediction (Temporal Fusion Transformer)

### Phase 3: Advanced Features
- Backtesting engine with walk-forward optimization
- Monte Carlo simulation
- Options flow analysis
- Alternative data integration

### Phase 4: Live Trading
- Real money paper trading (30-day minimum)
- Smart order routing (VWAP/TWAP)
- Slippage modeling
- Tax-aware trading

### Phase 5: Optimization
- Self-improving AI from trade outcomes
- Strategy parameter optimization
- Portfolio rebalancing automation

## 🎨 Design Highlights

- **No Generic "AI Slop"**: Custom-designed professional trading terminal
- **High Information Density**: Maximum data per pixel without clutter
- **Cyber-Professional Theme**: Sharp edges, minimal borders, glowing active states
- **Monospace Data Display**: JetBrains Mono for perfect numerical alignment
- **Real-time Updates**: Auto-refresh every 10-30 seconds
- **Responsive Grid Layout**: Bento Grid system for optimal space usage

## ⚠️ Important Notes

1. **Never Trade Without Stop Loss**: System enforces this automatically
2. **Daily Loss Limits**: Cannot be overridden programmatically
3. **30-Day Paper Trading**: Minimum testing period before considering live
4. **Slippage Assumptions**: 0.1% per trade in calculations
5. **Human Override**: Always available via Kill Switch

## 🔧 Development

The system uses hot reload for both frontend and backend:
- Backend changes auto-reload (except .env or dependency changes)
- Frontend changes auto-reload via React Fast Refresh
- Supervisor restart required for .env changes: `sudo supervisorctl restart backend`

## 📊 Performance Expectations

Based on Phase 1 implementation:
- **Signal Generation**: Real-time analysis for multiple stocks
- **Confidence Threshold**: 72% minimum for trades
- **Signal Strength**: 7/10 minimum for execution
- **Risk Management**: Automated position sizing and stop losses

## 🌟 Why ORACLE?

1. **Multi-Modal Analysis**: Combines technical + sentiment + quantitative signals
2. **Risk-First Design**: Safety guardrails prevent catastrophic losses
3. **Transparent AI**: Every decision logged with reasoning
4. **Professional UX**: Trading terminal designed for serious traders
5. **Fully Autonomous**: Can operate 24/7 with human oversight

## 📝 License

Proprietary - ORACLE Autonomous Trading System

---

**Built with Emergent AI Platform**

*Disclaimer: This is a trading system for educational and research purposes. Past performance does not guarantee future results. Always understand the risks involved in trading.*
