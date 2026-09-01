---
name: security-owasp-hardening
description: Production-grade OWASP security hardening guidelines, defensive coding patterns, and empirical security invariants for modern web applications.
---

# OWASP Security Hardening & Defensive Architecture

Defensive engineering guide for eliminating OWASP Top 10 vulnerabilities. Apply strict invariants at network, application, and persistence boundaries.

---

## 1. Authentication & Session Hardening

### A. Password Hashing (Argon2id / Bcrypt)
- **Primary Standard**: Argon2id (OWASP recommended for password hashing).
- **Secondary Standard**: Bcrypt with minimum cost factor >= 12.
- **Timing Attacks Defense**: Always use constant-time equality comparisons (`crypto.timingSafeEqual`) for tokens, signatures, and hashes.

```typescript
import argon2 from "argon2";
import crypto from "node:crypto";

// 1. Hash with Argon2id using OWASP minimum parameters
export async function hashPassword(password: string): Promise<string> {
  return await argon2.hash(password, {
    type: argon2.argon2id,
    memoryCost: 65536, // 64 MB
    timeCost: 3,       // 3 iterations
    parallelism: 4,    // 4 threads
  });
}

export async function verifyPassword(hash: string, plain: string): Promise<boolean> {
  try {
    return await argon2.verify(hash, plain);
  } catch {
    return false;
  }
}

// 2. Constant-time token verification (prevent timing side-channels)
export function timingSafeEqual(a: string, b: string): boolean {
  const bufA = Buffer.from(a);
  const bufB = Buffer.from(b);
  if (bufA.length !== bufB.length) return false;
  return crypto.timingSafeEqual(bufA, bufB);
}
```

### B. Secure Cookie Attributes & Prefixes
- Always enforce `HttpOnly`, `Secure`, and `SameSite` flags.
- Use `__Host-` cookie prefix for maximum origin-isolation (forces `Secure`, `Path=/`, and no subdomains).

```typescript
import { Response } from "express";

export function setAuthSessionCookie(res: Response, token: string, isProduction: boolean) {
  const cookieName = isProduction ? "__Host-session" : "session";
  
  res.cookie(cookieName, token, {
    httpOnly: true,                 // Block client-side JS document.cookie access (Mitigates XSS exfiltration)
    secure: isProduction,           // Enforce HTTPS transmission only
    sameSite: "lax",                // Mitigate CSRF on standard navigation (use "strict" for sensitive mutations)
    path: "/",                      // Match host root
    maxAge: 7 * 24 * 60 * 60 * 1000,// 7 days bounded TTL
  });
}
```

### C. Session Invariants
1. **Regenerate Session ID on Privilege Escalation**: Invalidate old session identifier upon login/logout to prevent Session Fixation.
2. **Absolute & Idle Timeout**: Enforce absolute expiration (e.g. 7 days) and idle inactivity timeout (e.g. 1 hour).
3. **Server-Side Invalidation**: Maintain active session records or a revocation list in Redis / database for instant token revocation.

---

## 2. Injection & Input Defense

### A. SQL / NoSQL Parameterization
- **Rule**: Never interpolate or concatenate user input into database queries. Always use parameterized queries or type-safe query builders (e.g., Prisma, Drizzle, `pg` parameterized values).

```typescript
import { Pool } from "pg";

const pool = new Pool();

// VULNERABLE:
// const query = `SELECT * FROM users WHERE email = '${req.body.email}'`;

// SECURE (Parameterized query):
export async function findUserByEmail(email: string) {
  const result = await pool.query(
    "SELECT id, email, password_hash, role FROM users WHERE email = $1 LIMIT 1",
    [email]
  );
  return result.rows[0] ?? null;
}
```

- **NoSQL Operator Injection**: Ensure user inputs are coerced to primitive types (string/number) to prevent object injection like `{ "$ne": null }`.

```typescript
// SECURE: Coerce inputs explicitly or validate with Zod
const email = String(req.body.email);
const user = await db.collection("users").findOne({ email: { $eq: email } });
```

### B. Strict Schema Validation with Zod
- Enforce schema validation at all network ingress points before executing business logic.
- Use `.strict()` or safe parsing to strip/reject unexpected payload properties.

```typescript
import { z } from "zod";

export const RegisterUserSchema = z.object({
  email: z.string().trim().email().max(255),
  password: z.string().min(12).max(128),
  fullName: z.string().trim().min(2).max(100),
}).strict();

export type RegisterUserInput = z.infer<typeof RegisterUserSchema>;

export function validatePayload<T>(schema: z.ZodSchema<T>, data: unknown): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    throw new Error(`Validation Failed: ${result.error.issues.map(i => i.message).join(", ")}`);
  }
  return result.data;
}
```

### C. XSS & Content-Security-Policy (CSP) Defense
1. **Context-Aware Encoding**: Modern frameworks (React/Vue/Svelte) automatically escape string interpolations. Never use `dangerouslySetInnerHTML` or `v-html` with untrusted inputs.
2. **HTML Sanitization**: If rich text rendering is required, sanitize using `DOMPurify` (with `jsdom` on server or client).
3. **HTTP Security Headers**: Use Helmet to apply strict security headers and CSP.

```typescript
import helmet from "helmet";
import express from "express";

const app = express();

app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", "data:", "https:"],
        objectSrc: ["'none'"],
        frameAncestors: ["'none'"], // Prevent clickjacking (alternative to X-Frame-Options: DENY)
        upgradeInsecureRequests: [],
      },
    },
    referrerPolicy: { policy: "strict-origin-when-cross-origin" },
    hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
  })
);
```

---

## 3. API Protection & Abuse Prevention

### A. Rate Limiting (Token Bucket / Sliding Window)
- Limit abuse on sensitive endpoints (e.g. login, registration, password reset, payment endpoints).

```typescript
import rateLimit from "express-rate-limit";

export const authRateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10,                  // Max 10 failed/success attempts per IP per window
  standardHeaders: true,    // Return standard RateLimit-* headers
  legacyHeaders: false,     // Disable X-RateLimit-* headers
  message: { error: "Too many requests. Please try again later." },
});

export const apiRateLimiter = rateLimit({
  windowMs: 60 * 1000,      // 1 minute
  max: 100,                 // 100 requests/minute
  standardHeaders: true,
  legacyHeaders: false,
});
```

### B. CORS Whitelist Policies
- **Rule**: Never use wildcard `Access-Control-Allow-Origin: *` when credentials/cookies are enabled.
- Explicitly validate origin against an approved whitelist.

```typescript
import cors from "cors";

const ALLOWED_ORIGINS = new Set([
  "https://app.example.com",
  "https://admin.example.com",
]);

export const corsMiddleware = cors({
  origin: (origin, callback) => {
    // Allow non-browser agents or same-origin requests (undefined origin)
    if (!origin || ALLOWED_ORIGINS.has(origin)) {
      callback(null, true);
    } else {
      callback(new Error("CORS policy violation: Disallowed origin"));
    }
  },
  credentials: true,
  methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization", "X-CSRF-Token"],
  maxAge: 86400, // Preflight cache 24h
});
```

### C. CSRF Protection
- For cookie-based authentication, enforce anti-CSRF defenses using Double Submit Cookies or SameSite=Lax/Strict plus custom headers (`X-Requested-With` or `X-CSRF-Token`).
- For mutation requests (`POST`, `PUT`, `PATCH`, `DELETE`), verify the `Origin` / `Referer` matches the host domain.

```typescript
import { Request, Response, NextFunction } from "express";

export function verifyCsrfOrigin(req: Request, res: Response, next: NextFunction) {
  if (["GET", "HEAD", "OPTIONS"].includes(req.method)) {
    return next();
  }

  const origin = req.headers.origin || req.headers.referer;
  const host = req.headers.host;

  if (!origin || !host || !origin.includes(host)) {
    return res.status(403).json({ error: "CSRF check failed: Invalid origin" });
  }

  next();
}
```

---

## 4. Secret & Credential Isolation

### A. Zero Secret Leakage in Source Code & Git
1. **Never Commit Secrets**: Ensure `.env*` files are strictly added to `.gitignore`.
2. **Client-Side Secret Shield**: Prefix client-facing env vars explicitly (e.g. `NEXT_PUBLIC_` or `VITE_`). Never expose private database URLs, private API keys, or secret tokens to client bundles.
3. **Automated Secret Scanning**: Enforce local and CI pre-commit git secret scanners (`gitleaks`, `trufflehog`).

```gitignore
# .gitignore rules for credentials
.env
.env.local
.env.*.local
*.pem
*.key
credentials.json
service-account*.json
```

### B. Fail-Fast Environment Variable Validation at Startup
- Never allow an application to boot if required secrets or configurations are missing or invalid.

```typescript
import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  SESSION_SECRET: z.string().min(32, "SESSION_SECRET must be at least 32 characters"),
  REDIS_URL: z.string().url().optional(),
});

export type Env = z.infer<typeof EnvSchema>;

export function validateEnv(): Env {
  const result = EnvSchema.safeParse(process.env);
  if (!result.success) {
    console.error("Invalid environment variables:", result.error.format());
    process.exit(1); // Fail-fast: Stop execution immediately
  }
  return result.data;
}

export const env = validateEnv();
```

---

## 5. OWASP Hardening Invariants Checklist

| Category | Invariant Rule | Verification Test |
| :--- | :--- | :--- |
| **Passwords** | Argon2id (m=64MB, t=3, p=4) or Bcrypt (cost >= 12). | Unit test password verify + hash output length. |
| **Cookies** | `HttpOnly; Secure; SameSite=Lax` with `__Host-` prefix in prod. | Check `Set-Cookie` response header flags. |
| **Database** | Parameterized queries only. Zero string interpolation in SQL. | Static analysis / linter rule forbidding template literals in SQL. |
| **Inputs** | Strict Zod schema parsing on all request bodies and query params. | Automated integration tests rejecting extra/invalid fields. |
| **Headers** | CSP enabled, `X-Frame-Options: DENY`, `Strict-Transport-Security`. | SecurityHeaders / Mozilla Observatory scan. |
| **Rate Limit** | Active rate limits on `/api/auth/*` and public endpoints. | Burst HTTP tests expecting HTTP 429. |
| **Environment** | Fail-fast validation at boot; no unvalidated `process.env`. | Boot test without required env var expecting process exit 1. |
