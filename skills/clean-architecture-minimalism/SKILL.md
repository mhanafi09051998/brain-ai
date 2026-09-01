---
name: clean-architecture-minimalism
description: High-precision engineering handbook for minimalist Clean Architecture, Pragmatic Hexagonal (Ports & Adapters) without enterprise boilerplate, rich domain invariants, dependency inversion without over-engineering, zero-mock deterministic testing, and safe atomic refactoring.
---

# Clean Architecture Minimalism & Pragmatic Domain Engineering

High-precision architectural principles for building maintainable, testable, and deeply decoupled software systems without enterprise bloat or unnecessary indirection layers.

---

## 1. The 3-Tier Pragmatic Hexagonal Model

Collapse traditional 8-layer enterprise architectures into 3 concrete, non-negotiable boundaries:

```
+-----------------------------------------------------------------------------------+
| 1. ADAPTERS / INFRASTRUCTURE (Outer Ring)                                         |
|    - HTTP Handlers, Express/Fastify Routes, CLI Commands, Next.js Server Actions  |
|    - Postgres/SQLite Repository Implementations, External API Clients             |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 2. APPLICATION / USE CASES (Orchestration Layer)                                  |
|    - Workflow Orchestration, Transaction Boundaries, Port Interfaces              |
|    - Pure Application Logic (No direct DB or HTTP framework coupling)            |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
| 3. DOMAIN CORE (Pure Business Rules)                                              |
|    - Entities, Value Objects with self-contained invariant validation             |
|    - Zero external dependencies (pure language standard library only)             |
+-----------------------------------------------------------------------------------+
```

---

## 2. Rich Domain Models vs. Anemic Entities

### A. Value Objects (Self-Validating Invariants)
```typescript
export class Money {
  private constructor(public readonly amount: number, public readonly currency: string) {}

  public static create(amount: number, currency: string): Money {
    if (amount < 0) throw new Error("Amount cannot be negative");
    return new Money(amount, currency.toUpperCase());
  }

  public add(other: Money): Money {
    if (this.currency !== other.currency) throw new Error("Currency mismatch");
    return new Money(this.amount + other.amount, this.currency);
  }
}
```

---

## 3. Deterministic Testing Strategy (Zero Mock Hell)

1. **Domain Logic**: 100% pure unit tests with direct function inputs/outputs (zero mocks required).
2. **Use Cases**: Use lightweight in-memory fake repositories (`class InMemoryUserRepository implements UserRepository`) instead of fragile mock frameworks.
3. **Integration**: Test real database interactions against ephemeral SQLite/PostgreSQL test containers.
