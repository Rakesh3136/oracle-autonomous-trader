"""Local account state projection from normalized private events."""
from dataclasses import dataclass

@dataclass(frozen=True)
class AccountPosition:
    symbol: str
    side: str
    quantity: float
    entry_price: float
    mark_price: float | None = None
    unrealized_pnl: float = 0.0

@dataclass(frozen=True)
class AccountState:
    wallet_balance: float = 0.0
    available_balance: float = 0.0
    positions: tuple[AccountPosition, ...] = ()

class AccountStateStore:
    def __init__(self) -> None:
        self.state = AccountState()

    def set_wallet(self, wallet_balance: float, available_balance: float) -> None:
        self.state = AccountState(wallet_balance, available_balance, self.state.positions)

    def set_positions(self, positions: list[AccountPosition]) -> None:
        self.state = AccountState(self.state.wallet_balance, self.state.available_balance, tuple(positions))
