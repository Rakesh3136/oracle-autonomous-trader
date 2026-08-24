# ORACLE Architecture

## Design principle

ORACLE is not an LLM that directly trades. It is a layered trading system in which AI performs perception, hypothesis generation, strategy analysis, research, and evaluation while deterministic controls govern capital, exposure, order validity, and emergency behavior.

## Decision loop

```text
Market Data
    ↓
Normalization / Feature Engine
    ↓
Market Regime Engine
    ↓
Independent Strategy Agents
    ↓
Trader Core
    ├── Current thesis
    ├── Alternative thesis
    ├── Evidence
    ├── Uncertainty
    └── Invalidation conditions
    ↓
Opportunity Ranking
    ↓
Deterministic Risk Gate
    ↓
Position Sizing
    ↓
Execution Engine
    ↓
Exchange
    ↓
Position / Order Reconciliation
    ↓
Trade Journal
    ↓
Evaluation & Research
    ↓
Champion / Challenger Validation
```

## Core boundaries

### AI layer

AI may propose actions such as LONG, SHORT, CLOSE, REDUCE, HOLD, or NO_TRADE. It must expose confidence, evidence, thesis, invalidation conditions, expected risk, and expected reward.

### Risk layer

The risk engine is authoritative. It can reject any proposed trade. It owns configured limits for exposure, leverage, loss, drawdown, liquidity, slippage, and emergency states.

### Execution layer

The execution engine is responsible for idempotency, order lifecycle handling, retries, partial fills, slippage measurement, and exchange-state reconciliation.

### Learning layer

Learning is controlled. New strategies/models are candidates until they pass backtesting, walk-forward validation, out-of-sample evaluation, stress testing, and paper/shadow evaluation.

## Initial operating modes

1. Research
2. Historical backtest
3. Paper trading
4. Shadow trading
5. Canary live trading
6. Production

Live trading is disabled by default.

## Repository structure

```text
oracle/
  core/          Trader state, thesis, memory
  market/        Market data and normalization
  intelligence/  Market perception and AI analysis
  strategies/   Independent strategy implementations
  regime/       Market-regime classification
  risk/         Deterministic risk controls
  execution/    Order lifecycle and execution
  portfolio/    Positions and exposure
  learning/     Trade evaluation and learning loops
  research/     Experiments and model evaluation
  backtest/     Event-driven simulation
  exchange/     Exchange adapters, including Bybit
```
