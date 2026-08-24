"""Normalized order API contract for paper, testnet and live adapters."""
from dataclasses import dataclass
from enum import Enum

class OrderType(str, Enum):
    MARKET = "Market"
    LIMIT = "Limit"

@dataclass(frozen=True)
class CreateOrderRequest:
    category: str
    symbol: str
    side: str
    order_type: OrderType
    qty: str
    price: str | None = None
    client_order_id: str | None = None
    reduce_only: bool = False

@dataclass(frozen=True)
class ExchangeOrderResponse:
    success: bool
    order_id: str | None
    client_order_id: str | None
    status_code: int
    ret_code: int | None = None
    ret_msg: str = ""

class OrderApi:
    def __init__(self, client) -> None:
        self.client = client

    def create(self, request: CreateOrderRequest) -> ExchangeOrderResponse:
        body = {
            "category": request.category,
            "symbol": request.symbol,
            "side": request.side,
            "orderType": request.order_type.value,
            "qty": request.qty,
            "reduceOnly": request.reduce_only,
        }
        if request.price is not None:
            body["price"] = request.price
        if request.client_order_id is not None:
            body["orderLinkId"] = request.client_order_id
        result = self.client.request("POST", "/v5/order/create", {}, str(body))
        return ExchangeOrderResponse(
            success=result.get("retCode") == 0,
            order_id=(result.get("result") or {}).get("orderId") if isinstance(result.get("result"), dict) else None,
            client_order_id=(result.get("result") or {}).get("orderLinkId") if isinstance(result.get("result"), dict) else request.client_order_id,
            status_code=200,
            ret_code=result.get("retCode"),
            ret_msg=str(result.get("retMsg", "")),
        )
