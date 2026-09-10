"""Paket Self-Learning Agent Framework (Claudia Brain AI, Context7 Deep Mode)."""

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
from .engine import IterationLog, OptimizationResult, SelfLearningEngine
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
from .multi_task_flow import (
    BaseSpecializedTaskFlow,
    DocumentControllerTaskFlow,
    DomainRole,
    DomainStage,
    DynamicTaskFlow,
    FullStackTaskFlow,
    ResearchTaskFlow,
    SpatialXRTaskFlow,
    TaskFlowRouter,
)
from .reflection import (
    ReflectionAgent,
    ReflectionRecord,
    ReflectiveExecutor,
    ReflexionMemoryStore,
)
from .storage import KnowledgeEntry, KnowledgeStore
from .task_flow import (
    AgenticTaskFlow,
    FlowStep,
    StepStatus,
    TaskFlowContext,
    TaskPhase,
)

__version__ = "1.1.0"

__all__ = [
    # Self-Learning Engine
    "SelfLearningEngine",
    "OptimizationResult",
    "IterationLog",
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
    # Reflexion Engine
    "ReflectionRecord",
    "ReflexionMemoryStore",
    "ReflectionAgent",
    "ReflectiveExecutor",
    # Closed-Loop Task Flow
    "AgenticTaskFlow",
    "TaskFlowContext",
    "TaskPhase",
    "StepStatus",
    "FlowStep",
    # Multi-Task Flow
    "TaskFlowRouter",
    "DomainRole",
    "DomainStage",
    "BaseSpecializedTaskFlow",
    "FullStackTaskFlow",
    "ResearchTaskFlow",
    "SpatialXRTaskFlow",
    "DocumentControllerTaskFlow",
    "DynamicTaskFlow",
    # Identity Lock
    "ClaudiaIdentity",
    "IMMUTABLE_IDENTITY",
    "IdentityGuard",
    "IdentityTamperAttemptError",
    # Global Config
    "GlobalConfigManager",
    "ProjectEntry",
    "WorkspaceBridge",
]
