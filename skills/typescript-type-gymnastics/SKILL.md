---
name: typescript-type-gymnastics
description: High-precision engineering handbook for advanced TypeScript type gymnastics, conditional types, mapped types with key remapping, AST-level template literal parsing, nominal branding, exhaustive discriminated unions, recursive type-level algorithms, and zero-cost runtime validation schemas.
---

# TypeScript Type Gymnastics & Type-Level Engineering Handbook

High-precision, empirical architectural specifications, invariants, and production-grade design patterns for advanced TypeScript type system manipulation, compile-time theorem proving, and parse-don't-validate runtime boundaries.

---

## 1. Type Safety Invariants & Top/Bottom Types

### A. The Bottom-Up Hierarchy & Set-Theoretic Model
TypeScript's type system operates as a **set of possible runtime values**:
* **Top Type (`unknown`)**: Universal set ($\mathcal{U}$). Contains all possible JavaScript values. Cannot be operated on without explicit type narrowing.
* **Top/Bottom Hybrid (`any`)**: Unsound escape hatch that disables type checking. An assertion of `any` acts as both universal set and empty set, silently infecting downstream expressions and destroying inference.
* **Bottom Type (`never`)**: Empty set ($\emptyset$). Contains zero runtime values. Represents impossible execution branches, unhandled union variants, or functions that never return (throw / infinite loop).
* **Unit Types**: Single-element sets (`"GET"`, `42`, `true`, `null`, `undefined`, `unique symbol`).
* **Subtyping ($A \subseteq B$)**: $A$ is assignable to $B$ if every element in set $A$ belongs to set $B$.

```
          [ unknown ]           <-- Safe Top Type (Universal Set)
         /     |     \
      [any]    |    [any]       <-- Unsound Escape Hatch (Infects All)
     /         |         \
 [object]  [primitive]  [function]
     \         |         /
      \        |        /
        [ Unit Types ]
               |
           [ never ]            <-- Bottom Type (Empty Set: unreachable/exhaustive)
```

### B. Invariant: Zero `any` Policy
1. **No Implicit/Explicit `any`**: `any` bypasses the compiler's proof system. Any code containing `any` is an unverified assumption.
2. **Safe Ingress with `unknown`**: External data (HTTP request bodies, RPC payloads, `JSON.parse`, worker messages) MUST enter the codebase typed as `unknown` before undergoing validation.
3. **No Unsafe Assertions (`as T`)**: Direct casting `payload as TargetType` bypasses type checking without runtime verification. Use type guards (`x is T`), assertion functions (`asserts x is T`), or runtime schema parsers.

### C. Type Narrowing Mechanics
TypeScript narrows types based on control-flow analysis (CFA). Type narrowing predicates must account for JavaScript runtime edge cases.

#### 1. Built-in CFA Guards & Runtime Traps
* **`typeof null === "object"` Trap**:
  ```typescript
  // BAD: null passes through
  function isObjectBad(val: unknown): val is Record<string, unknown> {
    return typeof val === "object";
  }

  // GOOD: Empirical guard excluding null & arrays
  function isPlainObject(val: unknown): val is Record<PropertyKey, unknown> {
    return (
      typeof val === "object" &&
      val !== null &&
      !Array.isArray(val) &&
      Object.prototype.toString.call(val) === "[object Object]"
    );
  }
  ```
* **The `in` Operator Narrowing**:
  ```typescript
  type SuccessResponse = { status: "ok"; data: string[] };
  type ErrorResponse = { status: "error"; error: Error; code: number };
  type ApiResponse = SuccessResponse | ErrorResponse;

  function handleResponse(res: ApiResponse): string[] {
    if ("data" in res) {
      // CFA narrows res to SuccessResponse
      return res.data;
    }
    // CFA narrows res to ErrorResponse
    throw new Error(`API Failed [${res.code}]: ${res.error.message}`);
  }
  ```

#### 2. User-Defined Type Guards (`val is T`) vs Assertion Functions (`asserts val is T`)
* **Type Guard (`val is T`)**: Returns a boolean; branch-scoped narrowing.
* **Assertion Function (`asserts val is T`)**: Throws on invalid input; narrows the remainder of the current scope.

```typescript
// Type Guard
export function isNonNullable<T>(val: T): val is NonNullable<T> {
  return val !== null && val !== undefined;
}

// Array Filter Example (Preserves exact narrowed array type)
const mixed = ["alpha", null, "beta", undefined, "gamma"];
const strings: string[] = mixed.filter(isNonNullable);

// Assertion Function
export function assertNonNullable<T>(
  val: T,
  identifier = "Value"
): asserts val is NonNullable<T> {
  if (val === null || val === undefined) {
    throw new TypeError(`[Invariant Violation] ${identifier} cannot be null or undefined.`);
  }
}

// Scope-wide narrowing
function processHeader(header: string | undefined): string {
  assertNonNullable(header, "Authorization Header");
  // header is narrowed to string for all following lines
  return header.trim().toLowerCase();
}
```

---

## 2. Advanced Generics & Conditional Types

### A. Conditional Types & Distributive Law
Conditional types take the form `T extends U ? X : Y`.

#### 1. Distributive Conditional Types
When `T` is an unconstrained naked type parameter on the left of `extends`, conditional types **distribute** across unions:
$$(A \cup B) \text{ extends } U \implies (A \text{ extends } U) \cup (B \text{ extends } U)$$

```typescript
// Distributive: Filters out null and undefined from each union member
type NonNullableCustom<T> = T extends null | undefined ? never : T;

type Example = NonNullableCustom<string | number | null | undefined>;
// Result: string | number
```

#### 2. Preventing Distribution
To disable distribution (e.g. testing if an entire union satisfies a condition or checking for `never`), wrap both sides in tuple brackets `[T] extends [U]`:

```typescript
// Testing for exact 'never' type (never distributes to empty set if unbracketed)
type IsNever<T> = [T] extends [never] ? true : false;

type Test1 = IsNever<never>; // true
type Test2 = IsNever<string>; // false

// Testing for strict Tuple vs Array
type IsTuple<T> = T extends readonly [...infer _]
  ? number extends T["length"]
    ? false
    : true
  : false;

type T1 = IsTuple<[number, string]>; // true
type T2 = IsTuple<number[]>;          // false
```

### B. Type Inference with `infer`

`infer` introduces a pattern-matched type variable within the conditional clause.

```typescript
// 1. Unpacking Promise / Async Return Types
type AwaitDeep<T> = T extends PromiseLike<infer U> ? AwaitDeep<U> : T;

// 2. Unrolling Nested Arrays
type FlattenDeep<T> = T extends readonly (infer U)[] ? FlattenDeep<U> : T;

// 3. Extracting Parameter & Return Types of Overloaded / Variadic Functions
type AnyFunction = (...args: any[]) => any;

type ReturnTypeOf<T extends AnyFunction> = T extends (...args: any[]) => infer R
  ? R
  : never;

type ParametersOf<T extends AnyFunction> = T extends (...args: infer P) => any
  ? P
  : never;

type FirstArg<T extends AnyFunction> = T extends (first: infer F, ...rest: any[]) => any
  ? F
  : never;

// 4. Extracting Constructor Instance Types
type Constructor<T = unknown> = new (...args: any[]) => T;
type InstanceTypeOf<T extends Constructor> = T extends new (...args: any[]) => infer I
  ? I
  : never;
```

---

## 3. Mapped Types & Key Remapping

### A. Key Remapping via `as` Clauses
Transform, filter, or re-namespace object keys at compile time.

```typescript
// 1. Property filtering by Value Type
export type PickByValue<T, V> = {
  [K in keyof T as T[K] extends V ? K : never]: T[K];
};

export type OmitByValue<T, V> = {
  [K in keyof T as T[K] extends V ? never : K]: T[K];
};

interface ServiceInterface {
  id: string;
  name: string;
  count: number;
  init(): Promise<void>;
  shutdown(): Promise<void>;
}

type OnlyMethods = PickByValue<ServiceInterface, (...args: any[]) => any>;
// Result: { init: () => Promise<void>; shutdown: () => Promise<void> }

// 2. Getter/Setter Generation with Key Remapping
export type CreateGetters<T> = {
  [K in keyof T as K extends string ? `get${Capitalize<K>}` : never]: () => T[K];
};

export type CreateSetters<T> = {
  [K in keyof T as K extends string ? `set${Capitalize<K>}` : never]: (value: T[K]) => void;
};

type State = { volume: number; muted: boolean };
type StateAccessors = CreateGetters<State> & CreateSetters<State>;
/* Result: {
  getVolume: () => number;
  getMuted: () => boolean;
  setVolume: (value: number) => void;
  setMuted: (value: boolean) => void;
} */
```

### B. Deep Modifiers: Immutability & Deep Partial

```typescript
// Recursive Deep Readonly (Preserves primitives, functions, maps, sets)
export type DeepReadonly<T> = T extends ((...args: any[]) => any) | primitive
  ? T
  : T extends Map<infer K, infer V>
  ? ReadonlyMap<DeepReadonly<K>, DeepReadonly<V>>
  : T extends Set<infer U>
  ? ReadonlySet<DeepReadonly<U>>
  : T extends readonly [...infer Elements]
  ? { readonly [I in keyof Elements]: DeepReadonly<Elements[I]> }
  : T extends object
  ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
  : T;

type primitive = string | number | boolean | bigint | symbol | null | undefined;

// Recursive Deep Partial
export type DeepPartial<T> = T extends Function | primitive
  ? T
  : T extends Map<infer K, infer V>
  ? Map<DeepPartial<K>, DeepPartial<V>>
  : T extends Set<infer U>
  ? Set<DeepPartial<U>>
  : T extends readonly (infer U)[]
  ? DeepPartial<U>[]
  : T extends object
  ? { [K in keyof T]?: DeepPartial<T[K]> }
  : T;

// Mutable Inverse (Strip readonly modifier recursively)
export type DeepMutable<T> = {
  -readonly [K in keyof T]: T[K] extends object ? DeepMutable<T[K]> : T[K];
};
```

### C. Type-Safe Deep Path Navigation

Generate compile-time dot-notation paths for nested structures with value lookup.

```typescript
// Maximum recursion depth limiter to prevent infinite compiler recursion
type Prev = [never, 0, 1, 2, 3, 4, 5];

export type NestedPaths<T, Depth extends number = 4> = [Depth] extends [never]
  ? never
  : T extends object
  ? {
      [K in keyof T & string]: T[K] extends object
        ? `${K}` | `${K}.${NestedPaths<T[K], Prev[Depth]>}`
        : `${K}`;
    }[keyof T & string]
  : never;

export type PathValue<T, P extends string> = P extends `${infer Key}.${infer Rest}`
  ? Key extends keyof T
    ? PathValue<T[Key], Rest>
    : never
  : P extends keyof T
  ? T[P]
  : never;

// Type-Safe Deep Property Getter
export function get<T extends object, P extends NestedPaths<T>>(
  obj: T,
  path: P
): PathValue<T, P> {
  const keys = path.split(".");
  let current: any = obj;
  for (const key of keys) {
    if (current === null || current === undefined) return undefined as any;
    current = current[key];
  }
  return current;
}

// Example Schema
type AppConfig = {
  server: {
    host: string;
    port: number;
    ssl: { enabled: boolean; cert: string };
  };
  database: { primary: { url: string; poolSize: number } };
};

// Compile-Time Validated Paths
type AppPath = NestedPaths<AppConfig>;
// "server" | "server.host" | "server.port" | "server.ssl" | "server.ssl.enabled" | "server.ssl.cert" | "database" | "database.primary" | "database.primary.url" | "database.primary.poolSize"

type SslEnabled = PathValue<AppConfig, "server.ssl.enabled">; // boolean
type DbUrl = PathValue<AppConfig, "database.primary.url">;      // string
```

---

## 4. Template Literal Types & AST-Level Parsing

Compile-time string grammar parsing, route extracting, and casing transformations.

### A. Route Parameter Extraction Engine
Extracts path parameters from Express / Next.js URL schemas as a strongly-typed object.

```typescript
type ExtractRouteParamName<T extends string> =
  T extends `:${infer Param}` ? Param : never;

export type ExtractRouteParams<T extends string> = string extends T
  ? Record<string, string>
  : T extends `${infer _Start}:${infer Rest}`
  ? Rest extends `${infer Param}/${infer Subsequent}`
    ? { [K in Param | keyof ExtractRouteParams<`/${Subsequent}`>]: string }
    : { [K in Rest]: string }
  : Record<string, never>;

// Verification:
type UserPostRoute = "/orgs/:orgId/projects/:projectId/deployments/:deploymentId";
type ExtractedParams = ExtractRouteParams<UserPostRoute>;
// Result: { orgId: string; projectId: string; deploymentId: string }

export function defineRoute<T extends string>(
  path: T,
  handler: (params: ExtractRouteParams<T>) => void
) {
  return { path, handler };
}

// Fully type-checked handler arguments
defineRoute("/api/v1/pools/:poolAddress/tokens/:mint", (params) => {
  // params is inferred as { poolAddress: string; mint: string }
  console.log(params.poolAddress, params.mint);
});
```

### B. Typed Event Bus with Pattern Namespaces

```typescript
type Domain = "order" | "user" | "inventory";
type Action = "created" | "updated" | "deleted" | "failed";

export type DomainEventTopic = `${Domain}:${Action}` | `${Domain}:*` | "*";

export type EventPayloads = {
  "user:created": { userId: string; email: string; createdAt: number };
  "user:deleted": { userId: string; reason: string };
  "order:created": { orderId: string; totalLamports: bigint };
  "order:failed": { orderId: string; errorCode: string };
  "inventory:updated": { sku: string; quantity: number };
};

export interface StronglyTypedEventEmitter {
  emit<K extends keyof EventPayloads>(event: K, payload: EventPayloads[K]): void;
  on<K extends keyof EventPayloads>(
    event: K,
    handler: (payload: EventPayloads[K]) => void | Promise<void>
  ): void;
}
```

### C. String Manipulation: Casing Converters

```typescript
export type CamelToSnakeCase<S extends string> = S extends `${infer T}${infer U}`
  ? `${T extends Uppercase<T> ? `_${Lowercase<T>}` : T}${CamelToSnakeCase<U>}`
  : S;

export type SnakeToCamelCase<S extends string> = S extends `${infer Head}_${infer Tail}`
  ? `${Lowercase<Head>}${Capitalize<SnakeToCamelCase<Tail>>}`
  : Lowercase<S>;

export type DeepCamelKeys<T> = T extends readonly any[]
  ? { [K in keyof T]: DeepCamelKeys<T[K]> }
  : T extends object
  ? {
      [K in keyof T as SnakeToCamelCase<K & string>]: DeepCamelKeys<T[K]>;
    }
  : T;

// Example
type DatabaseRow = {
  user_id: string;
  first_name: string;
  total_liquidity_usd: number;
};

type AppModel = DeepCamelKeys<DatabaseRow>;
// Result: { userId: string; firstName: string; totalLiquidityUsd: number }
```

---

## 5. Nominal & Branded Types (Zero Primitive Obsession)

TypeScript uses a structural type system. By default, any two types with identical fields or primitive definitions are assignable to one another. **Branded types** inject compile-time nominal identity with **zero runtime overhead**.

### A. The Invariant & Brand Pattern
* A brand creates an uninhabitable intersection (`T & { readonly [BrandSymbol]: BrandName }`).
* Values can only be instantiated through explicit, validating constructor functions (smart constructors).

```typescript
// Global Brand Symbol
declare const __brand: unique symbol;

export type Brand<T, B extends string> = T & {
  readonly [__brand]: B;
};

// Domain Branded Identifiers
export type UserId = Brand<string, "UserId">;
export type OrganizationId = Brand<string, "OrganizationId">;
export type SolanaPublicKey = Brand<string, "SolanaPublicKey">;
export type PoolAddress = Brand<string, "PoolAddress">;
export type Lamports = Brand<bigint, "Lamports">;
export type MicroUSD = Brand<bigint, "MicroUSD">;
export type UnixTimestampMs = Brand<number, "UnixTimestampMs">;
```

### B. Smart Constructors & Validation Boundaries

```typescript
// 1. Solana Public Key Constructor (Base58 32-44 chars validation)
const BASE58_REGEX = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;

export function makeSolanaPublicKey(address: string): SolanaPublicKey {
  if (!BASE58_REGEX.test(address)) {
    throw new Error(`[InvalidSolanaPublicKey] Invalid Base58 address: "${address}"`);
  }
  return address as SolanaPublicKey;
}

// 2. UserId Smart Constructor (UUIDv4)
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function makeUserId(id: string): UserId {
  if (!UUID_REGEX.test(id)) {
    throw new Error(`[InvalidUserId] String is not a valid UUIDv4: "${id}"`);
  }
  return id as UserId;
}

// 3. Financial Unit Math with Invariant Preservation
export function toLamports(amountSol: number): Lamports {
  if (amountSol < 0) throw new RangeError("Lamports amount cannot be negative");
  return BigInt(Math.floor(amountSol * 1_000_000_000)) as Lamports;
}

export function addLamports(a: Lamports, b: Lamports): Lamports {
  return ((a as bigint) + (b as bigint)) as Lamports;
}

// Static Analysis Test: Prevents passing raw strings or wrong IDs
function transferSol(recipient: SolanaPublicKey, amount: Lamports, initiator: UserId) {
  // Safe execution with guaranteed invariants
}

declare const rawInput: string;
// @ts-expect-error Type 'string' is not assignable to type 'SolanaPublicKey'
transferSol(rawInput, 1000n, rawInput);

// Correct Usage:
const validRecipient = makeSolanaPublicKey("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v");
const validAmount = toLamports(1.5);
const validUser = makeUserId("f47ac10b-58cc-4372-a567-0e02b2c3d479");
transferSol(validRecipient, validAmount, validUser); // PASSES
```

---

## 6. Discriminated Unions & Exhaustiveness Proofs

State machines, protocol messages, and operational states must be modeled as **discriminated unions** to guarantee that illegal states are unrepresentable.

### A. State Machine Invariant Formulation

```typescript
// Explicit modeling of asynchronous data state
export type AsyncState<T, E = Error> =
  | { readonly status: "idle"; readonly data: null; readonly error: null }
  | { readonly status: "loading"; readonly data: T | null; readonly error: null }
  | { readonly status: "success"; readonly data: T; readonly error: null }
  | { readonly status: "error"; readonly data: T | null; readonly error: E };

export function isSuccessState<T, E>(
  state: AsyncState<T, E>
): state is { readonly status: "success"; readonly data: T; readonly error: null } {
  return state.status === "success";
}
```

### B. Exhaustiveness Verification with `never`

If a union is expanded with a new variant in the future, `assertNever` fails at compile time if the caller forgets to handle the new branch.

```typescript
export function assertNever(x: never, message?: string): never {
  throw new Error(
    message ?? `[Unreachable Branch Invariant Violated]: Received unexpected value ${JSON.stringify(x)}`
  );
}

// Complex Multi-Step Order Processing Machine
export type OrderAction =
  | { type: "INITIALIZE"; payload: { orderId: string; amount: bigint } }
  | { type: "ESCROW_LOCKED"; payload: { txSignature: string; vaultPda: string } }
  | { type: "EXECUTED"; payload: { executedPrice: number; filledAt: number } }
  | { type: "CANCELLED"; payload: { reason: string } };

export function handleOrderTransition(action: OrderAction): string {
  switch (action.type) {
    case "INITIALIZE":
      return `Order ${action.payload.orderId} initialized with ${action.payload.amount}`;
    case "ESCROW_LOCKED":
      return `Escrow locked in ${action.payload.vaultPda} (tx: ${action.payload.txSignature})`;
    case "EXECUTED":
      return `Order executed at ${action.payload.executedPrice}`;
    case "CANCELLED":
      return `Order cancelled: ${action.payload.reason}`;
    default:
      // If a 5th action type is added to OrderAction, TypeScript refuses to compile here
      return assertNever(action);
  }
}
```

### C. Pattern Matching Utility Function
An ergonomic functional pattern matcher supporting exhaustive checking.

```typescript
type PatternMatchMap<U extends { type: string }, R> = {
  [K in U["type"]]: (variant: Extract<U, { type: K }>) => R;
};

export function match<U extends { type: string }, R>(
  value: U,
  patterns: PatternMatchMap<U, R>
): R {
  const handler = patterns[value.type as keyof PatternMatchMap<U, R>];
  if (!handler) {
    return assertNever(value as never, `Unhandled pattern type: ${(value as any).type}`);
  }
  return handler(value as any);
}

// Usage
const result = match(action, {
  INITIALIZE: (a) => `Init ${a.payload.orderId}`,
  ESCROW_LOCKED: (a) => `Locked ${a.payload.txSignature}`,
  EXECUTED: (a) => `Executed ${a.payload.executedPrice}`,
  CANCELLED: (a) => `Cancelled ${a.payload.reason}`,
});
```

---

## 7. Zero-Cost Runtime Validation & Boundary Ingestion

### A. The "Parse, Don't Validate" Invariant
Validation functions returning booleans still leave the payload untyped or require manual unsafe casting. **Parsers** transform unverified raw ingress `unknown` into structured, strictly typed internal domain models.

```
External Data (unknown) ---> [ Parser / Schema Invariant ] ---> Verified Domain Model (T)
                                        |
                                        +---> [ Throws / Returns ParseError ]
```

### B. Production Integration: Zod vs TypeBox

#### 1. Zod: Developer Ergonomics & Rich Schema Refinement
```typescript
import { z } from "zod";

export const SwapOrderSchema = z.object({
  orderId: z.string().uuid(),
  poolAddress: z.string().min(32).max(44),
  inputAmount: z.string().regex(/^\d+$/).transform(BigInt),
  minOutputAmount: z.string().regex(/^\d+$/).transform(BigInt),
  recipient: z.string().min(32).max(44),
  slippageBps: z.number().int().min(0).max(10_000),
  deadline: z.number().int().positive(),
});

// Infer static TypeScript type directly from single source of truth
export type SwapOrder = z.infer<typeof SwapOrderSchema>;

export function parseSwapOrder(raw: unknown): SwapOrder {
  const result = SwapOrderSchema.safeParse(raw);
  if (!result.success) {
    throw new Error(`[SchemaValidationError] ${result.error.issues.map(i => `${i.path.join(".")}: ${i.message}`).join(", ")}`);
  }
  return result.data;
}
```

#### 2. TypeBox: Zero-Cost JSON-Schema JIT Compiler (High-Throughput Backends)
When processing 50k+ req/sec where validation overhead matters, `@sinclair/typebox` compiles schemas to V8 JIT validator functions.

```typescript
import { Type, Static } from "@sinclair/typebox";
import { TypeCompiler } from "@sinclair/typebox/compiler";

export const MicroserviceEventSchema = Type.Object({
  eventId: Type.String({ format: "uuid" }),
  sequenceNumber: Type.Integer({ minimum: 0 }),
  topic: Type.String({ minLength: 1 }),
  timestamp: Type.Integer(),
  payload: Type.Record(Type.String(), Type.Unknown()),
});

export type MicroserviceEvent = Static<typeof MicroserviceEventSchema>;

// JIT-compiled C-speed validator
const compiledCheck = TypeCompiler.Compile(MicroserviceEventSchema);

export function parseMicroserviceEvent(raw: unknown): MicroserviceEvent {
  if (compiledCheck.Check(raw)) {
    return raw; // Narrows directly to MicroserviceEvent
  }
  const firstError = compiledCheck.Errors(raw).First();
  throw new TypeError(
    `[TypeBoxError] Path ${firstError?.path}: ${firstError?.message}`
  );
}
```

---

## 8. Real-World Type-Level Engineering Recipes

### A. Tuple Manipulation Algorithms

```typescript
// 1. Head of Tuple
export type Head<T extends readonly any[]> = T extends readonly [infer H, ...any[]]
  ? H
  : never;

// 2. Tail of Tuple
export type Tail<T extends readonly any[]> = T extends readonly [any, ...infer Rest]
  ? Rest
  : [];

// 3. Prepend / Append
export type Prepend<T extends readonly any[], E> = [E, ...T];
export type Append<T extends readonly any[], E> = [...T, E];

// 4. Reverse a Tuple
export type Reverse<T extends readonly any[], Acc extends readonly any[] = []> =
  T extends readonly [infer First, ...infer Rest]
    ? Reverse<Rest, [First, ...Acc]>
    : Acc;

// 5. Tuple Length
export type Length<T extends readonly any[]> = T["length"];

// Verification
type TestTuple = [string, number, boolean];
type R1 = Head<TestTuple>;      // string
type R2 = Tail<TestTuple>;      // [number, boolean]
type R3 = Reverse<TestTuple>;   // [boolean, number, string]
```

### B. Strictly Typed Object Manipulation
Standard TypeScript widens `Object.keys(obj)` to `string[]` because objects may contain extra runtime properties. These utilities enforce strict typing when keys are known exhaustive records.

```typescript
export function strictKeys<T extends object>(obj: T): (keyof T & string)[] {
  return Object.keys(obj) as (keyof T & string)[];
}

export function strictEntries<K extends string | number | symbol, V>(
  obj: Record<K, V>
): [K, V][] {
  return Object.entries(obj) as [K, V][];
}

export function strictFromEntries<K extends PropertyKey, V>(
  entries: readonly (readonly [K, V])[]
): Record<K, V> {
  return Object.fromEntries(entries) as Record<K, V>;
}
```

### C. Type-Safe Fluent Builder with Phantom Type State Transition

Enforces that required fields MUST be set before calling `.build()` at compile time.

```typescript
type EmptyState = {
  hasUrl: false;
  hasMethod: false;
  hasHeaders: false;
};

export class RequestBuilder<State extends { hasUrl: boolean; hasMethod: boolean; hasHeaders: boolean } = EmptyState> {
  private url?: string;
  private method?: "GET" | "POST" | "PUT" | "DELETE";
  private headers: Record<string, string> = {};

  private constructor() {}

  static create(): RequestBuilder<EmptyState> {
    return new RequestBuilder<EmptyState>();
  }

  setUrl(url: string): RequestBuilder<Omit<State, "hasUrl"> & { hasUrl: true }> {
    this.url = url;
    return this as any;
  }

  setMethod(method: "GET" | "POST" | "PUT" | "DELETE"): RequestBuilder<Omit<State, "hasMethod"> & { hasMethod: true }> {
    this.method = method;
    return this as any;
  }

  setHeaders(headers: Record<string, string>): RequestBuilder<Omit<State, "hasHeaders"> & { hasHeaders: true }> {
    this.headers = headers;
    return this as any;
  }

  // .build() is ONLY available when hasUrl=true and hasMethod=true
  build(
    this: RequestBuilder<{ hasUrl: true; hasMethod: true; hasHeaders: boolean }>
  ): { url: string; method: string; headers: Record<string, string> } {
    return {
      url: this.url!,
      method: this.method!,
      headers: this.headers,
    };
  }
}

// Verification:
// Fails compilation: method not set yet
// RequestBuilder.create().setUrl("https://api.domain.com").build();

// Compiles cleanly:
const request = RequestBuilder.create()
  .setUrl("https://api.domain.com")
  .setMethod("POST")
  .setHeaders({ Authorization: "Bearer token" })
  .build();
```

---

## 9. Verification & Anti-Pattern Checklist

| Check | Anti-Pattern | Required Engineering Pattern |
| :--- | :--- | :--- |
| **Ingress Typing** | `function handle(data: any)` | `function handle(data: unknown)` + runtime parser |
| **Null Checks** | `typeof x === "object"` | `x !== null && typeof x === "object"` |
| **Array Filtering** | `.filter(x => Boolean(x))` | `.filter(isNonNullable)` with `x is NonNullable<T>` |
| **Primitive Obsession** | `transfer(to: string, amount: number)` | `transfer(to: SolanaPublicKey, amount: Lamports)` |
| **Union Switches** | `switch without default` | `default: return assertNever(variant)` |
| **Deep Access** | `obj.a?.b?.c` without type checking | `NestedPaths<T>` + `PathValue<T, P>` |
| **Casting** | `payload as UserProfile` | `UserProfileSchema.parse(payload)` |
