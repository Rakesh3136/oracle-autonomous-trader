# ORACLE Autonomous Trader

A research-first autonomous trading platform for Bybit USDT perpetuals.

## Philosophy

ORACLE is designed to behave like a disciplined professional trader rather than a simple signal bot:

**Observe → Understand → Form Thesis → Challenge Thesis → Assess Risk → Wait or Act → Execute → Manage → Reassess → Exit → Review → Learn**

AI components propose and evaluate decisions, while deterministic risk controls remain authoritative.

## Safety

The initial implementation is research/backtest/paper-trading only. Live trading must be explicitly enabled after validation and must remain bounded by deterministic risk controls.

Never commit exchange credentials or secrets.

## Planned capabilities

- Bybit market-data and execution adapters
- Multi-timeframe market intelligence
- Market-regime detection
- Multi-strategy ensemble
- Trader Core with thesis and uncertainty state
- Deterministic risk engine
- Event-driven backtesting
- Paper trading
- Trade journal and memory
- Controlled research/self-improvement loop
- Champion/challenger model evaluation
- Monitoring and alerts
