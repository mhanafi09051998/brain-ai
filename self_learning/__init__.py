"""Paket Self-Learning Agent Framework."""

from .agents import (
    CriticAgent,
    CritiqueReport,
    DistillerAgent,
    ExecutionReport,
    ObserverAgent,
    OptimizerAgent,
)
from .agents.critic import TargetProfile
from .agents.observer import TestCase
from .engine import OptimizationResult, SelfLearningEngine
from .reflection import (
    ReflectionAgent,
    ReflectionRecord,
    ReflectiveExecutor,
    ReflexionMemoryStore,
)
from .global_config import (
    GlobalConfigManager,
    ProjectEntry,
    WorkspaceBridge,
)
from .identity_lock import (
    ClaudiaIdentity,
    IMMUTABLE_IDENTITY,
    IdentityGuard,
    IdentityTamperAttemptError,
)
from .storage import KnowledgeEntry, KnowledgeStore

__all__ = [
    "SelfLearningEngine",
    "OptimizationResult",
    "TargetProfile",
    "TestCase",
    "KnowledgeStore",
    "KnowledgeEntry",
    "ObserverAgent",
    "CriticAgent",
    "DistillerAgent",
    "OptimizerAgent",
    "ExecutionReport",
    "CritiqueReport",
    "ReflectionRecord",
    "ReflexionMemoryStore",
    "ReflectionAgent",
    "ReflectiveExecutor",
    "ClaudiaIdentity",
    "IMMUTABLE_IDENTITY",
    "IdentityGuard",
    "IdentityTamperAttemptError",
    "GlobalConfigManager",
    "ProjectEntry",
    "WorkspaceBridge",
]

