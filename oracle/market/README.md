# Market Intelligence

This package defines the canonical market representation used by every ORACLE component.

The exchange adapter must translate exchange-specific payloads into these models. Strategy and AI code must not depend directly on raw Bybit payloads.

Current foundation:

- OHLCV candles
- order-book levels and spread
- derivatives state
- immutable market snapshots
- returns
- realized volatility
- order-book imbalance
- exchange-independent market-data interface

The regime classifier currently contains an intentionally simple, explainable baseline. ML regime models will be introduced as challengers and evaluated against this baseline rather than replacing it blindly.
