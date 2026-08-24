# ORACLE Master Build — 39 Requirements

This file tracks the original 39 engineering requirements. A requirement is **implemented** only when the corresponding production-quality code, tests, and documentation exist.

## Status

### Foundation
- [x] 1. Project architecture
- [x] 2. Configuration foundation (project configuration exists; runtime config still expanding)
- [ ] 3. Database
- [ ] 4. Bybit market-data adapter
- [ ] 5. Historical data ingestion
- [x] 6. Feature engine foundation
- [ ] 7. Full indicator library
- [ ] 8. Strategy framework
- [ ] 9. Event-driven backtesting engine
- [x] 10. Deterministic risk engine foundation

### Trading intelligence
- [ ] 11. Paper execution
- [ ] 12. AI regime engine
- [ ] 13. AI strategy ensemble
- [ ] 14. Learning/research engine
- [ ] 15. Live execution adapter (disabled until validation)
- [ ] 16. Monitoring
- [ ] 17. Dashboard
- [ ] 18. Alerting
- [ ] 19. Full integration test suite
- [ ] 20. Deployment

### Advanced capabilities
- [ ] 21. Multi-timeframe market intelligence
- [ ] 22. Order-flow intelligence
- [ ] 23. Derivatives intelligence: funding/OI/liquidations
- [ ] 24. Market-regime adaptation
- [ ] 25. Multi-agent trader ensemble
- [ ] 26. Thesis/debate engine
- [ ] 27. Opportunity ranking
- [ ] 28. Professional position sizing
- [ ] 29. Execution optimization
- [ ] 30. Position/order reconciliation
- [ ] 31. Complete trade journal
- [ ] 32. Strategy/model leaderboard
- [ ] 33. Champion/challenger model lifecycle
- [ ] 34. Walk-forward and out-of-sample validation
- [ ] 35. Monte Carlo and stress testing
- [ ] 36. Controlled self-improvement
- [ ] 37. Research ingestion and hypothesis generation
- [ ] 38. Anomaly/emergency protection
- [ ] 39. Production hardening, observability, security, and staged deployment

## Non-negotiable design rules

1. AI never bypasses deterministic risk controls.
2. Live trading is disabled by default.
3. No secret/API key may be committed.
4. Every trade decision must be auditable.
5. New models are challengers until validated out-of-sample.
6. NO_TRADE is a first-class decision.
7. Exchange-specific payloads stay behind adapters.
8. Backtests must model fees, funding, slippage, latency and fills.
9. The system must be able to stop trading when data, execution, reconciliation or risk integrity fails.
10. Performance is judged by risk-adjusted, cost-adjusted, out-of-sample results rather than raw backtest profit.
