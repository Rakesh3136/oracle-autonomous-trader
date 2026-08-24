"""Fail-closed reconciliation between local and authoritative exchange state."""
from oracle.reconciliation.models import DiscrepancyType, ReconciliationFinding

class ReconciliationEngine:
    def compare_orders(self, local: dict[str, str], exchange: dict[str, str], symbols: dict[str, str] | None = None) -> tuple[ReconciliationFinding, ...]:
        findings: list[ReconciliationFinding] = []
        for ref in sorted(set(local) | set(exchange)):
            if ref not in local:
                findings.append(ReconciliationFinding(DiscrepancyType.MISSING_LOCAL_ORDER, "", ref, "missing", exchange[ref]))
            elif ref not in exchange:
                findings.append(ReconciliationFinding(DiscrepancyType.MISSING_EXCHANGE_ORDER, "", ref, local[ref], "missing"))
            elif local[ref] != exchange[ref]:
                findings.append(ReconciliationFinding(DiscrepancyType.STATUS_MISMATCH, "", ref, local[ref], exchange[ref]))
        return tuple(findings)

    def compare_positions(self, local: dict[str, float], exchange: dict[str, float]) -> tuple[ReconciliationFinding, ...]:
        findings: list[ReconciliationFinding] = []
        for symbol in sorted(set(local) | set(exchange)):
            lq = local.get(symbol, 0.0)
            eq = exchange.get(symbol, 0.0)
            if lq != eq:
                kind = DiscrepancyType.UNEXPECTED_POSITION if symbol not in local else DiscrepancyType.POSITION_MISMATCH
                findings.append(ReconciliationFinding(kind, symbol, symbol, str(lq), str(eq)))
        return tuple(findings)

    @staticmethod
    def requires_halt(findings: tuple[ReconciliationFinding, ...]) -> bool:
        return any(f.severity in {"critical", "high"} for f in findings)
