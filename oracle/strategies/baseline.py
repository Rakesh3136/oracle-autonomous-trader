from oracle.core.trader import Action
from oracle.market.features import returns
from oracle.market.models import MarketSnapshot
from oracle.strategies.base import Signal, Strategy

class MomentumStrategy(Strategy):
    name = "momentum_baseline"
    def evaluate(self, snapshot: MarketSnapshot) -> Signal:
        r = returns(snapshot.candles)
        if r is None:
            return Signal(self.name, Action.NO_TRADE, 0.0, ("insufficient data",), ())
        if r > 0.005:
            return Signal(self.name, Action.LONG, min(1.0, r / 0.02), ("positive short-term momentum",), ("momentum reversal",), 2.0)
        if r < -0.005:
            return Signal(self.name, Action.SHORT, min(1.0, abs(r) / 0.02), ("negative short-term momentum",), ("momentum reversal",), 2.0)
        return Signal(self.name, Action.NO_TRADE, 0.5, ("momentum not decisive",), ())
