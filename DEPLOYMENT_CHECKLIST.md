# ORACLE Deployment Checklist

## Research / paper
- [ ] Historical data loaded and validated
- [ ] No look-ahead leakage
- [ ] Walk-forward validation passed
- [ ] Fee/slippage/funding stress passed
- [ ] Paper trading stable

## Bybit Testnet
- [ ] Testnet API key/secret stored outside git
- [ ] Instrument rules synchronized from exchange
- [ ] Server clock synchronized
- [ ] Public market stream healthy
- [ ] Private order/position stream healthy
- [ ] Wallet, orders and positions reconcile
- [ ] Duplicate-order protection verified
- [ ] Unknown-order outcome forces halt/reconciliation
- [ ] Kill switch verified
- [ ] Full order lifecycle verified

## Live deployment
- [ ] All CI checks green
- [ ] Walk-forward and stress validation independently reviewed
- [ ] Sufficient paper/Testnet history collected
- [ ] Monitoring and alerts verified
- [ ] Secret management verified
- [ ] Rollback/flatten procedure tested
- [ ] Live API key has only the minimum required permissions
- [ ] Live order cap and rate limits configured
- [ ] Independent operator approval recorded

**Important:** Live trading must never be enabled merely because the software compiles. It requires evidence from the gates above and explicit operator approval. Bybit's current V5 API provides REST/WebSocket trading and account interfaces, and Bybit recommends testing API trading on Testnet first. See the official API documentation linked from Bybit's Help Center. 
