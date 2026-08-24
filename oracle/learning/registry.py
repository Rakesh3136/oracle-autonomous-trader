"""Versioned model registry with explicit promotion and rollback."""
from dataclasses import dataclass
from datetime import datetime, timezone
from oracle.learning.evaluation import ModelReport

@dataclass(frozen=True)
class ModelVersion:
    version: str
    created_at: datetime
    report: ModelReport

class ModelRegistry:
    def __init__(self) -> None:
        self._versions: dict[str, ModelVersion] = {}
        self._champion: str | None = None
        self._history: list[str] = []

    @property
    def champion(self) -> ModelVersion | None:
        return self._versions.get(self._champion) if self._champion else None

    def register(self, version: str, report: ModelReport) -> ModelVersion:
        if not version or version in self._versions:
            raise ValueError("model version must be unique and non-empty")
        model = ModelVersion(version, datetime.now(timezone.utc), report)
        self._versions[version] = model
        return model

    def promote(self, version: str) -> ModelVersion:
        if version not in self._versions:
            raise KeyError(version)
        if self._champion and version == self._champion:
            return self._versions[version]
        self._champion = version
        self._history.append(version)
        return self._versions[version]

    def rollback(self) -> ModelVersion:
        if len(self._history) < 2:
            raise RuntimeError("no previous champion available")
        self._history.pop()
        self._champion = self._history[-1]
        return self._versions[self._champion]
