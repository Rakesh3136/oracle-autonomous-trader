"""Runtime configuration with safe defaults for research/paper operation."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "research"
    bybit_testnet: bool = True
    bybit_api_key: str | None = Field(default=None, repr=False)
    bybit_api_secret: str | None = Field(default=None, repr=False)
    live_trading_enabled: bool = False
    max_symbols: int = 20

    def assert_live_safety(self) -> None:
        if self.live_trading_enabled and self.bybit_testnet:
            raise ValueError("live trading cannot be enabled while Bybit testnet is selected")
        if self.live_trading_enabled and (not self.bybit_api_key or not self.bybit_api_secret):
            raise ValueError("live trading requires exchange credentials")
