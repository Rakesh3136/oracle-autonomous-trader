from oracle.runtime.release_readiness import ReadinessChecklist, ReleaseReadiness
from oracle.runtime.live_gate import DeploymentStage, GateChecklist, LiveGate
from oracle.exchange.bybit.auth import BybitCredentials
from oracle.exchange.bybit.private_rest import BybitPrivateRest, PrivateRestConfig


def test_live_readiness_is_denied_until_every_gate_passes():
    checks = ReadinessChecklist(*([True] * 11), operator_approval=False)
    report = ReleaseReadiness().evaluate(checks)
    assert report.ready_for_testnet
    assert not report.ready_for_live
    assert "operator_approval" in report.failures


def test_live_gate_requires_all_controls():
    checks = GateChecklist(True, True, True, True, True, False)
    assert not LiveGate().authorize(DeploymentStage.LIVE, checks)


def test_private_rest_cannot_submit_orders_by_default():
    adapter = BybitPrivateRest(BybitCredentials("key", "secret"), PrivateRestConfig(testnet=True))
    try:
        try:
            adapter.create_order({"category": "linear", "symbol": "BTCUSDT", "side": "Buy", "orderType": "Market", "qty": "1"})
            assert False, "order submission should be disabled"
        except PermissionError:
            pass
    finally:
        adapter.close()
