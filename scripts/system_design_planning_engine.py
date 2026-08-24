#!/usr/bin/env python3
"""
Claudia System Design, Capacity Estimation, Consistent Hashing & Architecture Planning Engine
Pure, zero-external-dependency production algorithms for:
1. System Capacity, IOPS, Storage & Bandwidth Estimator (80/20 Pareto, RAM Tiering)
2. Consistent Hashing Ring with Virtual Nodes & Minimal Rebalance Churn
3. Automated Architecture Decision Record (ADR) Generator (MADR & Nygard)
4. OpenAPI 3.1 Contract-First Specification & Request/Response Schema Validator
5. C4 Model Architecture-as-Code Mermaid Diagram Generator
"""

import math
import sys
import json
import hashlib
import bisect
import re
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass, asdict, field
import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# =====================================================================
# 1. SYSTEM CAPACITY, BANDWIDTH, RAM & STORAGE ESTIMATOR
# =====================================================================

@dataclass
class CapacityInput:
    dau: int                               # Daily Active Users
    reads_per_user_day: float              # Average read actions per user per day
    writes_per_user_day: float             # Average write actions per user per day
    read_payload_bytes: int                # Average payload size of a read response (bytes)
    write_payload_bytes: int               # Average payload size of a write request (bytes)
    peak_multiplier: float = 2.0           # Peak traffic multiplier (e.g., 2.0x avg)
    cache_hit_ratio: float = 0.80          # Cache hit ratio (80%)
    pareto_cache_pct: float = 0.20         # 80/20 rule: 20% of daily read data cached in RAM
    retention_days: int = 365 * 3          # Storage retention period (default: 3 years)
    replication_factor: int = 3            # Replication factor for high availability
    indexing_overhead_pct: float = 0.25    # Metadata & B-Tree index overhead (25%)


@dataclass
class CapacityOutput:
    # Throughput (QPS)
    daily_reads: int
    daily_writes: int
    avg_read_qps: float
    peak_read_qps: float
    avg_write_qps: float
    peak_write_qps: float
    total_avg_qps: float
    total_peak_qps: float

    # Network Bandwidth
    ingress_mb_per_sec: float
    ingress_gbps: float
    peak_ingress_gbps: float
    egress_mb_per_sec: float
    egress_gbps: float
    peak_egress_gbps: float
    total_bandwidth_gbps: float

    # Storage Tiering
    daily_raw_storage_gb: float
    daily_replicated_storage_gb: float
    yearly_replicated_storage_tb: float
    total_retention_storage_tb: float

    # Memory & Cache (Pareto 80/20)
    daily_read_volume_gb: float
    ram_cache_needed_gb: float
    ram_cache_needed_nodes: int            # Assuming standard 64GB RAM cache nodes

    # IOPS
    db_read_iops_cache_miss: float
    db_write_iops_replicated: float
    total_db_iops: float


class SystemCapacityEstimator:
    """
    High-precision Large-Scale Capacity and Infrastructure Resource Estimator.
    Implements standard mathematical modeling from 'donnemartin/system-design-primer'.
    """

    @staticmethod
    def estimate(inp: CapacityInput) -> CapacityOutput:
        seconds_in_day = 86400

        # 1. Throughput calculations
        daily_reads = int(inp.dau * inp.reads_per_user_day)
        daily_writes = int(inp.dau * inp.writes_per_user_day)

        avg_read_qps = daily_reads / seconds_in_day
        peak_read_qps = avg_read_qps * inp.peak_multiplier

        avg_write_qps = daily_writes / seconds_in_day
        peak_write_qps = avg_write_qps * inp.peak_multiplier

        total_avg_qps = avg_read_qps + avg_write_qps
        total_peak_qps = peak_read_qps + peak_write_qps

        # 2. Network Bandwidth (Ingress & Egress)
        ingress_bytes_sec = avg_write_qps * inp.write_payload_bytes
        ingress_mb_sec = ingress_bytes_sec / (1024 * 1024)
        ingress_gbps = (ingress_bytes_sec * 8) / 1e9
        peak_ingress_gbps = ingress_gbps * inp.peak_multiplier

        egress_bytes_sec = avg_read_qps * inp.read_payload_bytes
        egress_mb_sec = egress_bytes_sec / (1024 * 1024)
        egress_gbps = (egress_bytes_sec * 8) / 1e9
        peak_egress_gbps = egress_gbps * inp.peak_multiplier

        total_bandwidth_gbps = ingress_gbps + egress_gbps

        # 3. Storage Estimation (Daily, Yearly, Multi-Year Retention)
        daily_raw_write_bytes = daily_writes * inp.write_payload_bytes
        daily_raw_storage_gb = daily_raw_write_bytes / (1024 ** 3)
        
        # Factor in replication & index overhead: Storage = Raw * Replication * (1 + Index_Overhead)
        daily_replicated_storage_gb = daily_raw_storage_gb * inp.replication_factor * (1.0 + inp.indexing_overhead_pct)
        yearly_replicated_storage_tb = (daily_replicated_storage_gb * 365) / 1024
        total_retention_storage_tb = (daily_replicated_storage_gb * inp.retention_days) / 1024

        # 4. Memory Caching Tier (Pareto 80/20 Rule)
        daily_read_volume_bytes = daily_reads * inp.read_payload_bytes
        daily_read_volume_gb = daily_read_volume_bytes / (1024 ** 3)
        ram_cache_needed_gb = daily_read_volume_gb * inp.pareto_cache_pct
        
        # Standard Redis / Memcached 64GB RAM instance (48GB usable after OS/Redis overhead)
        usable_ram_per_node = 48.0
        ram_cache_needed_nodes = max(1, math.ceil(ram_cache_needed_gb / usable_ram_per_node))

        # 5. IOPS Estimation
        db_read_iops_cache_miss = avg_read_qps * (1.0 - inp.cache_hit_ratio)
        db_write_iops_replicated = avg_write_qps * inp.replication_factor
        total_db_iops = db_read_iops_cache_miss + db_write_iops_replicated

        return CapacityOutput(
            daily_reads=daily_reads,
            daily_writes=daily_writes,
            avg_read_qps=round(avg_read_qps, 2),
            peak_read_qps=round(peak_read_qps, 2),
            avg_write_qps=round(avg_write_qps, 2),
            peak_write_qps=round(peak_write_qps, 2),
            total_avg_qps=round(total_avg_qps, 2),
            total_peak_qps=round(total_peak_qps, 2),
            ingress_mb_per_sec=round(ingress_mb_sec, 2),
            ingress_gbps=round(ingress_gbps, 4),
            peak_ingress_gbps=round(peak_ingress_gbps, 4),
            egress_mb_per_sec=round(egress_mb_sec, 2),
            egress_gbps=round(egress_gbps, 4),
            peak_egress_gbps=round(peak_egress_gbps, 4),
            total_bandwidth_gbps=round(total_bandwidth_gbps, 4),
            daily_raw_storage_gb=round(daily_raw_storage_gb, 2),
            daily_replicated_storage_gb=round(daily_replicated_storage_gb, 2),
            yearly_replicated_storage_tb=round(yearly_replicated_storage_tb, 2),
            total_retention_storage_tb=round(total_retention_storage_tb, 2),
            daily_read_volume_gb=round(daily_read_volume_gb, 2),
            ram_cache_needed_gb=round(ram_cache_needed_gb, 2),
            ram_cache_needed_nodes=ram_cache_needed_nodes,
            db_read_iops_cache_miss=round(db_read_iops_cache_miss, 2),
            db_write_iops_replicated=round(db_write_iops_replicated, 2),
            total_db_iops=round(total_db_iops, 2),
        )


# =====================================================================
# 2. CONSISTENT HASHING RING WITH VIRTUAL NODES
# =====================================================================

class ConsistentHashRing:
    """
    Production Consistent Hashing Ring with Virtual Nodes (vnodes).
    Provides deterministic node placement, O(log N) binary search key lookup,
    and minimal K/N data redistribution during topology changes.
    """

    def __init__(self, vnodes_per_node: int = 150):
        self.vnodes_per_node = vnodes_per_node
        self.ring: List[int] = []                    # Sorted list of token hashes
        self.token_to_node: Dict[int, str] = {}     # Token -> Physical Node ID
        self.physical_nodes: Set[str] = set()

    @staticmethod
    def _hash(key: str) -> int:
        """MD5-based 128-bit hash modulo 2^32 for consistent ring distribution."""
        return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) & 0xFFFFFFFF

    def add_node(self, node_id: str, weight: int = 1) -> None:
        """Adds a physical node to the ring with corresponding virtual nodes."""
        if node_id in self.physical_nodes:
            return
        self.physical_nodes.add(node_id)
        num_vnodes = self.vnodes_per_node * max(1, weight)
        for i in range(num_vnodes):
            vnode_key = f"{node_id}#vnode-{i}"
            token = self._hash(vnode_key)
            self.token_to_node[token] = node_id
            bisect.insort(self.ring, token)

    def remove_node(self, node_id: str) -> None:
        """Removes a physical node and all its virtual tokens from the ring."""
        if node_id not in self.physical_nodes:
            return
        self.physical_nodes.remove(node_id)
        tokens_to_remove = [tok for tok, n in self.token_to_node.items() if n == node_id]
        for tok in tokens_to_remove:
            del self.token_to_node[tok]
        self.ring = [tok for tok in self.ring if tok not in tokens_to_remove]

    def get_node(self, key: str) -> Optional[str]:
        """Returns the primary physical node responsible for the given key."""
        if not self.ring:
            return None
        token = self._hash(key)
        idx = bisect.bisect_right(self.ring, token)
        if idx == len(self.ring):
            idx = 0  # Wrap around the ring
        return self.token_to_node[self.ring[idx]]

    def get_preference_list(self, key: str, n_replicas: int) -> List[str]:
        """
        Returns N distinct physical nodes responsible for replicating the key.
        Walks clockwise along the ring skipping duplicate physical nodes.
        """
        if not self.ring:
            return []
        token = self._hash(key)
        idx = bisect.bisect_right(self.ring, token)
        preference_list: List[str] = []
        seen_nodes: Set[str] = set()

        total_tokens = len(self.ring)
        for i in range(total_tokens):
            curr_idx = (idx + i) % total_tokens
            curr_node = self.token_to_node[self.ring[curr_idx]]
            if curr_node not in seen_nodes:
                seen_nodes.add(curr_node)
                preference_list.append(curr_node)
                if len(preference_list) >= min(n_replicas, len(self.physical_nodes)):
                    break
        return preference_list

    def calculate_distribution(self, sample_keys: List[str]) -> Dict[str, Any]:
        """Measures load balancing uniformity across physical nodes."""
        if not self.physical_nodes:
            return {"counts": {}, "standard_deviation": 0.0, "max_to_min_ratio": 1.0}

        counts = {node: 0 for node in self.physical_nodes}
        for k in sample_keys:
            node = self.get_node(k)
            if node:
                counts[node] += 1

        total_keys = len(sample_keys)
        n_nodes = len(self.physical_nodes)
        expected_per_node = total_keys / n_nodes if n_nodes > 0 else 0

        variance = sum((cnt - expected_per_node) ** 2 for cnt in counts.values()) / n_nodes if n_nodes > 0 else 0
        std_dev = math.sqrt(variance)
        
        min_cnt = min(counts.values()) if counts else 0
        max_cnt = max(counts.values()) if counts else 0
        ratio = (max_cnt / min_cnt) if min_cnt > 0 else float("inf")

        pct_dist = {node: round((cnt / total_keys) * 100, 2) if total_keys > 0 else 0.0 for node, cnt in counts.items()}

        return {
            "node_counts": counts,
            "percentage_distribution": pct_dist,
            "expected_percentage": round(100.0 / n_nodes, 2) if n_nodes > 0 else 0.0,
            "standard_deviation_keys": round(std_dev, 2),
            "max_to_min_ratio": round(ratio, 2),
        }

    def measure_rebalance_churn(
        self, sample_keys: List[str], target_node: str, is_add: bool
    ) -> Dict[str, Any]:
        """
        Measures the fraction of keys moved when a node is added or removed.
        Verifies theoretical minimal churn: ~ 1/(N+1) for add or 1/N for remove.
        """
        if is_add:
            # Current mapping without target_node
            before_map = {k: self.get_node(k) for k in sample_keys}
            self.add_node(target_node)
            after_map = {k: self.get_node(k) for k in sample_keys}
        else:
            # Current mapping with target_node
            before_map = {k: self.get_node(k) for k in sample_keys}
            self.remove_node(target_node)
            after_map = {k: self.get_node(k) for k in sample_keys}

        moved_keys = sum(1 for k in sample_keys if before_map[k] != after_map[k])
        total_keys = len(sample_keys)
        actual_churn_pct = (moved_keys / total_keys) * 100 if total_keys > 0 else 0.0

        n_nodes = len(self.physical_nodes)
        # Theoretical churn
        theoretical_churn_pct = (100.0 / n_nodes) if n_nodes > 0 else 0.0

        return {
            "total_keys": total_keys,
            "moved_keys": moved_keys,
            "actual_churn_pct": round(actual_churn_pct, 2),
            "theoretical_churn_pct": round(theoretical_churn_pct, 2),
            "churn_difference_pct": round(abs(actual_churn_pct - theoretical_churn_pct), 2),
        }


# =====================================================================
# 3. ARCHITECTURE DECISION RECORD (ADR) GENERATOR & LIFECYCLE
# =====================================================================

class ArchitectureDecisionRecordManager:
    """
    Standard Architecture Decision Record (ADR) Lifecycle Manager.
    Implements MADR (Markdown Architectural Decision Records) and Nygard standards.
    """

    VALID_STATUSES = ["Proposed", "Accepted", "Rejected", "Deprecated", "Superseded"]

    @classmethod
    def generate_madr(
        cls,
        adr_id: int,
        title: str,
        status: str,
        context_and_problem: str,
        decision_drivers: List[str],
        considered_options: List[Dict[str, Any]],
        chosen_option: str,
        consequences_positive: List[str],
        consequences_negative: List[str],
        deciders: List[str],
        date_str: Optional[str] = None,
    ) -> str:
        """Generates a structured MADR markdown document."""
        assert status in cls.VALID_STATUSES, f"Invalid ADR status: {status}"
        d_str = date_str or datetime.date.today().isoformat()
        
        drivers_md = "\n".join(f"* {d}" for d in decision_drivers)
        pos_md = "\n".join(f"* Good, because {c}" for c in consequences_positive)
        neg_md = "\n".join(f"* Bad, because {c}" for c in consequences_negative)
        
        options_md = ""
        for opt in considered_options:
            name = opt.get("name", "Option")
            desc = opt.get("description", "")
            pros = "\n".join(f"  * Good: {p}" for p in opt.get("pros", []))
            cons = "\n".join(f"  * Bad: {c}" for c in opt.get("cons", []))
            options_md += f"### {name}\n{desc}\n\n{pros}\n{cons}\n\n"

        content = f"""# ADR-{adr_id:04d}: {title}

* **Status:** {status}
* **Deciders:** {", ".join(deciders)}
* **Date:** {d_str}

## Context and Problem Statement
{context_and_problem.strip()}

## Decision Drivers
{drivers_md}

## Considered Options
{options_md.strip()}

## Decision Outcome
Chosen option: **"{chosen_option}"**, because it best satisfies the primary decision drivers while minimizing architectural debt.

### Positive Consequences
{pos_md}

### Negative Consequences & Mitigations
{neg_md}

## Validation & Verification
1. Automated unit & invariant test verification in continuous integration.
2. Architecture metric observability via OpenTelemetry.
"""
        return content

    @classmethod
    def generate_nygard(
        cls,
        adr_id: int,
        title: str,
        status: str,
        context: str,
        decision: str,
        consequences: List[str],
        date_str: Optional[str] = None,
    ) -> str:
        """Generates a classic Nygard-format ADR."""
        assert status in cls.VALID_STATUSES, f"Invalid ADR status: {status}"
        d_str = date_str or datetime.date.today().isoformat()
        cons_md = "\n".join(f"- {c}" for c in consequences)

        content = f"""# {adr_id}. {title}

Date: {d_str}

## Status
{status}

## Context
{context.strip()}

## Decision
{decision.strip()}

## Consequences
{cons_md}
"""
        return content

    @classmethod
    def supersede_adr(cls, existing_madr: str, new_adr_id: int, new_adr_title: str) -> str:
        """Transitions an existing ADR from Accepted -> Superseded by new ADR."""
        superseded_notice = f"Superseded by [ADR-{new_adr_id:04d}: {new_adr_title}](ADR-{new_adr_id:04d}.md)"
        updated = re.sub(
            r"\* \*\*Status:\*\* .*",
            f"* **Status:** {superseded_notice}",
            existing_madr,
            count=1
        )
        return updated

    @classmethod
    def parse_adr_metadata(cls, adr_content: str) -> Dict[str, Any]:
        """Extracts metadata from ADR markdown."""
        title_match = re.search(r"#\s+(?:ADR-)?(\d+)[:.]?\s+(.*)", adr_content)
        status_match = re.search(r"\*?\*?Status:?\*?\*?\s*(.*)", adr_content, re.IGNORECASE)
        date_match = re.search(r"\*?\*?Date:?\*?\*?\s*(\d{4}-\d{2}-\d{2})", adr_content, re.IGNORECASE)

        return {
            "adr_id": int(title_match.group(1)) if title_match else None,
            "title": title_match.group(2).strip() if title_match else None,
            "status": status_match.group(1).strip() if status_match else None,
            "date": date_match.group(1).strip() if date_match else None,
        }


# =====================================================================
# 4. OPENAPI 3.1 CONTRACT-FIRST SPECIFICATION & SCHEMA VALIDATOR
# =====================================================================

class OpenAPIContractValidator:
    """
    Pure Python Contract-First OpenAPI 3.0 / 3.1 Specification & JSON Schema Validator.
    Enforces rigorous API schema contracts, path parameter compliance, request body
    validation, and response status mapping without external dependencies.
    """

    @classmethod
    def validate_spec_structure(cls, spec: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validates the root structural integrity of an OpenAPI 3.x specification."""
        errors: List[str] = []

        if not isinstance(spec, dict):
            return False, ["Root OpenAPI specification must be a JSON/dict object."]

        # 1. Version check
        version = spec.get("openapi")
        if not version or not isinstance(version, str) or not version.startswith("3."):
            errors.append(f"Missing or invalid 'openapi' version string (must be 3.x.x, found '{version}').")

        # 2. Info check
        info = spec.get("info")
        if not isinstance(info, dict):
            errors.append("Missing 'info' dictionary in root specification.")
        else:
            if not info.get("title"):
                errors.append("Missing 'info.title' in specification.")
            if not info.get("version"):
                errors.append("Missing 'info.version' in specification.")

        # 3. Paths check
        paths = spec.get("paths")
        if not isinstance(paths, dict):
            errors.append("Missing 'paths' dictionary in root specification.")
        else:
            for path_pattern, path_item in paths.items():
                if not path_pattern.startswith("/"):
                    errors.append(f"Path '{path_pattern}' must start with a leading slash '/'.")
                
                # Check declared path parameters e.g. /users/{userId}
                expected_params = re.findall(r"\{([a-zA-Z0-9_-]+)\}", path_pattern)
                
                if isinstance(path_item, dict):
                    valid_methods = {"get", "post", "put", "delete", "patch", "options", "head"}
                    for method_name, op in path_item.items():
                        if method_name.lower() in valid_methods and isinstance(op, dict):
                            # Verify path parameters exist in operation or path parameters
                            declared_params = [
                                p.get("name") for p in op.get("parameters", []) if isinstance(p, dict) and p.get("in") == "path"
                            ]
                            for exp in expected_params:
                                if exp not in declared_params:
                                    errors.append(f"Operation {method_name.upper()} {path_pattern} misses required path parameter '{exp}'.")
                            
                            # Verify responses object
                            if "responses" not in op or not isinstance(op["responses"], dict):
                                errors.append(f"Operation {method_name.upper()} {path_pattern} must define a 'responses' dictionary.")

        return len(errors) == 0, errors

    @classmethod
    def validate_json_schema(cls, data: Any, schema: Dict[str, Any], path: str = "root") -> Tuple[bool, List[str]]:
        """
        Validates arbitrary JSON data against an OpenAPI / JSON Schema definition.
        Supports: type, required, properties, items, enum, minimum, maximum, minLength, maxLength, pattern.
        """
        errors: List[str] = []
        if not isinstance(schema, dict):
            return True, []

        schema_type = schema.get("type")

        # Null check
        if data is None:
            if schema.get("nullable") is True or schema_type == "null":
                return True, []
            return False, [f"{path}: Expected type '{schema_type}', found null."]

        # Type validation
        if schema_type:
            type_map = {
                "string": str,
                "integer": int,
                "number": (int, float),
                "boolean": bool,
                "array": list,
                "object": dict,
            }
            expected_py_type = type_map.get(schema_type)
            if expected_py_type:
                # Disallow bool acting as int (Python bool is subclass of int)
                if schema_type in ("integer", "number") and isinstance(data, bool):
                    errors.append(f"{path}: Expected numeric type '{schema_type}', found boolean.")
                    return False, errors
                if not isinstance(data, expected_py_type):
                    errors.append(f"{path}: Expected type '{schema_type}', found '{type(data).__name__}'.")
                    return False, errors

        # String constraints
        if isinstance(data, str):
            if "minLength" in schema and len(data) < schema["minLength"]:
                errors.append(f"{path}: String length {len(data)} < minLength {schema['minLength']}.")
            if "maxLength" in schema and len(data) > schema["maxLength"]:
                errors.append(f"{path}: String length {len(data)} > maxLength {schema['maxLength']}.")
            if "pattern" in schema:
                if not re.search(schema["pattern"], data):
                    errors.append(f"{path}: Value '{data}' does not match regex pattern '{schema['pattern']}'.")

        # Number constraints
        if isinstance(data, (int, float)) and not isinstance(data, bool):
            if "minimum" in schema and data < schema["minimum"]:
                errors.append(f"{path}: Value {data} < minimum {schema['minimum']}.")
            if "maximum" in schema and data > schema["maximum"]:
                errors.append(f"{path}: Value {data} > maximum {schema['maximum']}.")

        # Enum check
        if "enum" in schema and data not in schema["enum"]:
            errors.append(f"{path}: Value '{data}' is not in allowed enum {schema['enum']}.")

        # Array validation
        if isinstance(data, list):
            items_schema = schema.get("items")
            if items_schema and isinstance(items_schema, dict):
                for idx, item in enumerate(data):
                    valid, sub_errs = cls.validate_json_schema(item, items_schema, f"{path}[{idx}]")
                    if not valid:
                        errors.extend(sub_errs)

        # Object validation
        if isinstance(data, dict):
            # Required fields check
            required_fields = schema.get("required", [])
            for rf in required_fields:
                if rf not in data:
                    errors.append(f"{path}: Missing required field '{rf}'.")

            # Property schemas check
            properties = schema.get("properties", {})
            for key, val in data.items():
                if key in properties:
                    valid, sub_errs = cls.validate_json_schema(val, properties[key], f"{path}.{key}")
                    if not valid:
                        errors.extend(sub_errs)

        return len(errors) == 0, errors

    @classmethod
    def validate_request_payload(
        cls, spec: Dict[str, Any], path: str, method: str, payload: Any
    ) -> Tuple[bool, List[str]]:
        """Validates an incoming HTTP request body against the OpenAPI spec operation."""
        op = spec.get("paths", {}).get(path, {}).get(method.lower())
        if not op:
            return False, [f"Operation {method.upper()} {path} not defined in spec."]

        request_body_cfg = op.get("requestBody")
        if not request_body_cfg:
            if payload is not None:
                return False, [f"Operation {method.upper()} {path} does not expect a request body."]
            return True, []

        is_required = request_body_cfg.get("required", False)
        if is_required and payload is None:
            return False, [f"Operation {method.upper()} {path} requires a request body."]

        content_schema = (
            request_body_cfg.get("content", {})
            .get("application/json", {})
            .get("schema")
        )
        if not content_schema:
            return True, []

        return cls.validate_json_schema(payload, content_schema, path=f"requestBody({method.upper()} {path})")


# =====================================================================
# 5. C4 ARCHITECTURE MODEL & DIAGRAMS-AS-CODE MERMAID GENERATOR
# =====================================================================

@dataclass
class C4Element:
    id: str
    name: str
    description: str
    technology: Optional[str] = None
    element_type: str = "Container"   # Person, System, Container, Component, Database


@dataclass
class C4Relation:
    source_id: str
    target_id: str
    label: str
    protocol: Optional[str] = None


class C4ModelGenerator:
    """
    Structured C4 Architecture Model (Context & Container Levels)
    Generates Mermaid architecture diagrams natively without graphviz.
    """

    @classmethod
    def generate_context_diagram(
        cls,
        title: str,
        persons: List[C4Element],
        primary_system: C4Element,
        external_systems: List[C4Element],
        relations: List[C4Relation],
    ) -> str:
        """Generates C4 Level 1: System Context Diagram in Mermaid syntax."""
        lines = [
            "```mermaid",
            "flowchart TB",
            f"    %% Title: {title}",
            "    classDef personStyle fill:#08427b,stroke:#073b6e,color:#ffffff,stroke-width:2px;",
            "    classDef systemStyle fill:#1168bd,stroke:#0b4884,color:#ffffff,stroke-width:2px;",
            "    classDef extSystemStyle fill:#999999,stroke:#666666,color:#ffffff,stroke-width:2px;",
            "",
        ]

        # Persons
        for p in persons:
            lines.append(f'    {p.id}["👤 <b>{p.name}</b><br/><small>{p.description}</small>"]:::personStyle')

        # Primary System
        lines.append(
            f'    {primary_system.id}["🏢 <b>{primary_system.name}</b><br/><small>{primary_system.description}</small>"]:::systemStyle'
        )

        # External Systems
        for es in external_systems:
            lines.append(
                f'    {es.id}["☁️ <b>{es.name}</b><br/><small>[External System]</small><br/><small>{es.description}</small>"]:::extSystemStyle'
            )

        lines.append("")
        # Relations
        for r in relations:
            proto_str = f" [{r.protocol}]" if r.protocol else ""
            lines.append(f'    {r.source_id} -->|"{r.label}{proto_str}"| {r.target_id}')

        lines.append("```")
        return "\n".join(lines)

    @classmethod
    def generate_container_diagram(
        cls,
        title: str,
        system_name: str,
        containers: List[C4Element],
        external_systems: List[C4Element],
        relations: List[C4Relation],
    ) -> str:
        """Generates C4 Level 2: Container Diagram in Mermaid syntax."""
        lines = [
            "```mermaid",
            "flowchart TB",
            f"    %% Title: {title}",
            "    classDef containerStyle fill:#438dd5,stroke:#2e6295,color:#ffffff,stroke-width:2px;",
            "    classDef dbStyle fill:#2b78e4,stroke:#1b4f91,color:#ffffff,stroke-width:2px,shape:cylinder;",
            "    classDef extStyle fill:#888888,stroke:#555555,color:#ffffff,stroke-width:2px;",
            "",
            f'    subgraph Boundary_{cls._slug(system_name)} ["<b>{system_name} (System Boundary)</b>"]',
        ]

        for c in containers:
            tech = f"<br/><small>[{c.technology}]</small>" if c.technology else ""
            style = "dbStyle" if c.element_type == "Database" else "containerStyle"
            icon = "🗄️" if c.element_type == "Database" else "📦"
            lines.append(f'        {c.id}["{icon} <b>{c.name}</b>{tech}<br/><small>{c.description}</small>"]:::{style}')

        lines.append("    end")
        lines.append("")

        for es in external_systems:
            lines.append(
                f'    {es.id}["☁️ <b>{es.name}</b><br/><small>[External System]</small><br/><small>{es.description}</small>"]:::extStyle'
            )

        lines.append("")
        for r in relations:
            proto_str = f" [{r.protocol}]" if r.protocol else ""
            lines.append(f'    {r.source_id} -->|"{r.label}{proto_str}"| {r.target_id}')

        lines.append("```")
        return "\n".join(lines)

    @staticmethod
    def _slug(name: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_]", "_", name)


# =====================================================================
# 6. DETERMINISTIC TEST SUITE
# =====================================================================

def run_deterministic_tests() -> bool:
    print("======================================================================")
    print("🚀 Claudia System Design, Capacity & Planning Engine Test Suite")
    print("======================================================================")

    # -----------------------------------------------------------------
    # Test 1: Capacity & Resource Estimator
    # -----------------------------------------------------------------
    print("\n[Test 1] Testing System Capacity & Bandwidth Estimator...")
    cap_input = CapacityInput(
        dau=50_000_000,                # 50 Million DAU
        reads_per_user_day=20.0,       # 1 Billion Reads / day
        writes_per_user_day=2.0,       # 100 Million Writes / day
        read_payload_bytes=2048,       # 2 KB read payload
        write_payload_bytes=512,       # 512 B write payload
        peak_multiplier=2.0,
        cache_hit_ratio=0.85,          # 85% cache hit
        pareto_cache_pct=0.20,         # 20% daily read volume in RAM
        retention_days=365 * 3,        # 3 Years
        replication_factor=3,
        indexing_overhead_pct=0.25,
    )
    metrics = SystemCapacityEstimator.estimate(cap_input)

    assert metrics.daily_reads == 1_000_000_000, f"Expected 1B reads, got {metrics.daily_reads}"
    assert metrics.daily_writes == 100_000_000, f"Expected 100M writes, got {metrics.daily_writes}"
    assert abs(metrics.avg_read_qps - 11574.07) < 0.1, f"Avg read QPS mismatch: {metrics.avg_read_qps}"
    assert abs(metrics.avg_write_qps - 1157.41) < 0.1, f"Avg write QPS mismatch: {metrics.avg_write_qps}"
    assert abs(metrics.total_peak_qps - (metrics.total_avg_qps * 2.0)) < 0.1
    assert metrics.egress_gbps > metrics.ingress_gbps, "Egress bandwidth should exceed Ingress"
    assert metrics.ram_cache_needed_gb > 0, "RAM cache needed must be > 0"
    assert metrics.ram_cache_needed_nodes >= 1, "Cache nodes must be >= 1"

    print(f"  [✓] 50M DAU Capacity -> Avg QPS: {metrics.total_avg_qps:,.0f} | Peak QPS: {metrics.total_peak_qps:,.0f}")
    print(f"  [✓] Bandwidth -> Ingress: {metrics.ingress_gbps:.3f} Gbps | Egress: {metrics.egress_gbps:.3f} Gbps")
    print(f"  [✓] Storage -> 3-Year Replicated: {metrics.total_retention_storage_tb:.2f} TB | RAM Cache: {metrics.ram_cache_needed_gb:.1f} GB ({metrics.ram_cache_needed_nodes} nodes)")

    # -----------------------------------------------------------------
    # Test 2: Consistent Hashing Ring & Minimal Rebalance Churn
    # -----------------------------------------------------------------
    print("\n[Test 2] Testing Consistent Hashing Ring & Virtual Nodes...")
    ring = ConsistentHashRing(vnodes_per_node=150)
    initial_nodes = ["db-node-01", "db-node-02", "db-node-03", "db-node-04"]
    for n in initial_nodes:
        ring.add_node(n)

    sample_keys = [f"user_session_token_{i}" for i in range(10000)]
    dist = ring.calculate_distribution(sample_keys)

    # Validate distribution uniformity (each node should get approx 25% ± 5%)
    for node, pct in dist["percentage_distribution"].items():
        assert 20.0 <= pct <= 30.0, f"Node {node} distribution outlier: {pct}%"
    print(f"  [✓] Uniform Ring Distribution across 4 nodes (Expected ~25%): {dist['percentage_distribution']}")

    # Test Preference List (Replication)
    pref_list = ring.get_preference_list("order_id_987654", n_replicas=3)
    assert len(pref_list) == 3, f"Expected 3 replicas, got {len(pref_list)}"
    assert len(set(pref_list)) == 3, "Preference list must contain distinct physical nodes"
    print(f"  [✓] Replica Preference List: {pref_list}")

    # Test Minimal Churn (Adding 5th node should migrate ~ 1/(4+1) = 20% keys)
    churn = ring.measure_rebalance_churn(sample_keys, target_node="db-node-05", is_add=True)
    assert 15.0 <= churn["actual_churn_pct"] <= 25.0, f"Churn out of theoretical bound: {churn['actual_churn_pct']}%"
    print(f"  [✓] Node Addition Churn: {churn['actual_churn_pct']}% (Theoretical: {churn['theoretical_churn_pct']}%, Moved: {churn['moved_keys']}/{churn['total_keys']} keys)")

    # -----------------------------------------------------------------
    # Test 3: Architecture Decision Record (ADR) Generator
    # -----------------------------------------------------------------
    print("\n[Test 3] Testing ADR MADR/Nygard Generator & Lifecycle...")
    madr_text = ArchitectureDecisionRecordManager.generate_madr(
        adr_id=54,
        title="Adopt Consistent Hashing for Distributed Cache Tier",
        status="Accepted",
        context_and_problem="Rapid scaling to 50M DAU requires sharding Redis cache across 16 nodes with minimal rebalancing spikes.",
        decision_drivers=["Zero-downtime node addition", "Uniform key distribution", "Sub-millisecond routing"],
        considered_options=[
            {
                "name": "Modulo Hashing (hash(key) % N)",
                "description": "Simple modulo indexing.",
                "pros": ["Trivial implementation"],
                "cons": ["Complete cache invalidation when N changes (100% churn)"]
            },
            {
                "name": "Consistent Hashing Ring with 150 vnodes",
                "description": "MD5 ring with virtual nodes.",
                "pros": ["Minimal 1/N migration churn", "Uniform load balancing"],
                "cons": ["Slightly higher routing memory table in client"]
            }
        ],
        chosen_option="Consistent Hashing Ring with 150 vnodes",
        consequences_positive=["Reduces cache invalidation cascade during autoscaling to < 10%"],
        consequences_negative=["Client libraries must maintain virtual ring token lookup"],
        deciders=["Claudia", "Lead Architect", "Infrastructure SRE"],
        date_str="2026-08-24",
    )

    meta = ArchitectureDecisionRecordManager.parse_adr_metadata(madr_text)
    assert meta["adr_id"] == 54, f"Parsed ID mismatch: {meta['adr_id']}"
    assert meta["status"] == "Accepted", f"Parsed status mismatch: {meta['status']}"
    assert meta["title"] == "Adopt Consistent Hashing for Distributed Cache Tier"

    # Test Supersede transition
    superseded = ArchitectureDecisionRecordManager.supersede_adr(madr_text, 72, "Migrate to Dynamic Rendezvous Hashing")
    meta_super = ArchitectureDecisionRecordManager.parse_adr_metadata(superseded)
    assert "Superseded" in meta_super["status"], "ADR must reflect Superseded status"
    print("  [✓] MADR Generation, Metadata Parsing & Supersede Lifecycle validated.")

    # -----------------------------------------------------------------
    # Test 4: OpenAPI 3.1 Contract-First Spec & Schema Validator
    # -----------------------------------------------------------------
    print("\n[Test 4] Testing OpenAPI 3.1 Specification & Schema Validator...")
    sample_spec = {
        "openapi": "3.1.0",
        "info": {"title": "Claudia Distributed Payment API", "version": "1.0.0"},
        "paths": {
            "/v1/payments/{paymentId}": {
                "get": {
                    "operationId": "getPayment",
                    "parameters": [
                        {"name": "paymentId", "in": "path", "required": True, "schema": {"type": "string"}}
                    ],
                    "responses": {
                        "200": {"description": "Payment details retrieved"}
                    }
                }
            },
            "/v1/payments": {
                "post": {
                    "operationId": "createPayment",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["amount_cents", "currency", "recipient_id"],
                                    "properties": {
                                        "amount_cents": {"type": "integer", "minimum": 100},
                                        "currency": {"type": "string", "enum": ["USD", "IDR", "EUR"]},
                                        "recipient_id": {"type": "string", "pattern": "^usr_[a-zA-Z0-9]+$"},
                                        "metadata": {"type": "object"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {"description": "Payment initiated"}
                    }
                }
            }
        }
    }

    is_spec_valid, spec_errs = OpenAPIContractValidator.validate_spec_structure(sample_spec)
    assert is_spec_valid is True, f"Spec structure validation failed: {spec_errs}"

    # Test valid request payload
    valid_payload = {
        "amount_cents": 50000,
        "currency": "IDR",
        "recipient_id": "usr_alpha99"
    }
    is_valid_req, req_errs = OpenAPIContractValidator.validate_request_payload(
        sample_spec, "/v1/payments", "POST", valid_payload
    )
    assert is_valid_req is True, f"Valid payload rejected: {req_errs}"

    # Test invalid payloads (missing required, enum breach, regex mismatch, type mismatch)
    invalid_payload = {
        "amount_cents": 50,              # < minimum 100
        "currency": "SGD",               # not in enum [USD, IDR, EUR]
        "recipient_id": "invalid_id"     # pattern failure
    }
    is_invalid_res, invalid_errs = OpenAPIContractValidator.validate_request_payload(
        sample_spec, "/v1/payments", "POST", invalid_payload
    )
    assert is_invalid_res is False, "Invalid payload must be rejected"
    assert len(invalid_errs) >= 3, f"Expected >= 3 errors, found {len(invalid_errs)}: {invalid_errs}"
    print(f"  [✓] OpenAPI 3.1 Contract validation caught {len(invalid_errs)} schema contract breaches as expected.")

    # -----------------------------------------------------------------
    # Test 5: C4 Model Mermaid Architecture Generator
    # -----------------------------------------------------------------
    print("\n[Test 5] Testing C4 Model Architecture-as-Code Generator...")
    context_mermaid = C4ModelGenerator.generate_context_diagram(
        title="Claudia Global Scalable Engine Context",
        persons=[
            C4Element("User", "Mobile & Web User", "End-user interacting with payments and trading services"),
            C4Element("Admin", "SRE / System Operator", "Admin managing deployment and system parameters")
        ],
        primary_system=C4Element("CoreEngine", "Claudia Distributed System", "Autonomous AI & High-Throughput Core Platform"),
        external_systems=[
            C4Element("BankGateway", "Banking Clearing House", "External ISO-8583 payment settlement network"),
            C4Element("MarketData", "Intermarket Gold & FX Feeds", "Real-time institutional liquidity provider")
        ],
        relations=[
            C4Relation("User", "CoreEngine", "Initiates payments & queries", "HTTPS/JSON"),
            C4Relation("Admin", "CoreEngine", "Manages config & models", "gRPC/mTLS"),
            C4Relation("CoreEngine", "BankGateway", "Settles ledger transactions", "ISO-8583"),
            C4Relation("CoreEngine", "MarketData", "Streams tick prices", "WebSocket")
        ]
    )
    assert "```mermaid" in context_mermaid and "flowchart TB" in context_mermaid
    assert "CoreEngine" in context_mermaid and "BankGateway" in context_mermaid
    print("  [✓] C4 Model Mermaid Context Diagram generated successfully.")

    print("\n======================================================================")
    print("✅ All 5 System Design & Planning Nucleus Invariant Tests PASSED (100%)")
    print("======================================================================")
    return True


if __name__ == "__main__":
    success = run_deterministic_tests()
    sys.exit(0 if success else 1)
