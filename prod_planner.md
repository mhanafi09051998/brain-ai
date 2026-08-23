# Production Planning Specification: Zolu AI Web Production Engine

**Target Application**: `prod.zolu.my.id` (Port: 3012)  
**AI Inference Engine**: 9Router Gateway (`https://9router.zolu.my.id/v1`)  
**API Key**: `sk-b2a2f6c6f8228b4b-prod01-71d3127b`  
**Database**: SQLite (`better-sqlite3`) + WAL Mode  
**Architecture Invariant**: **Strict Maximum 300 Lines of Code per File** (Modular decomposition).

---

## 1. Arsitektur Sistem & Spesifikasi Inti

```
+-------------------------------------------------------------------------------+
|                       ZOLU AI WEB PRODUCTION ENGINE                           |
|                         (https://prod.zolu.my.id)                             |
+-------------------------------------------------------------------------------+
       |                                              |
       v                                              v
+-----------------------------+        +----------------------------------------+
|   Next.js 14 (App Router)   |        |           9Router AI Gateway           |
|  - TypeScript + Tailwind    | <----> |  - Endpoint: /v1/chat/completions      |
|  - Lucide Icons (Light Def) |        |  - Model: High-context Code Generator  |
|  - Max 300 lines/file       |        |  - Auth: sk-b2a2f6c6f8228b4b-...       |
+-----------------------------+        +----------------------------------------+
       |
       v
+-----------------------------+
|    SQLite Database (WAL)    |
|  - Projects & Templates     |
|  - Generated Files & Code   |
|  - Version History & Logs   |
+-----------------------------+
```

### 1.1 Tech Stack Standar
- **Framework**: Next.js 14 (App Router, Server Components & Route Handlers).
- **Language**: TypeScript (Strict Mode).
- **Styling**: Tailwind CSS (Default Light Mode, high contrast, mobile & desktop responsive).
- **Icons**: `lucide-react` (SVG native, zero bloat).
- **Database**: SQLite3 via `better-sqlite3` with WAL mode enabled (`PRAGMA journal_mode = WAL;`).
- **Server Port**: `3012` (PM2 name: `zolu-prod`).
- **Domain Edge**: `https://prod.zolu.my.id` via Cloudflare Tunnel.

---

## 2. Aturan Modularity & Maintenance (Max 300 Lines/File)

Setiap file dalam codebase wajib mematuhi batas **maksimal 300 baris kode**:

1. **Komponen UI**: Setiap kartu, toolbar, editor, dan viewer dipisah ke file tersendiri di `components/`.
2. **API Routes**: Logika parsing LLM, file streaming, dan database CRUD dipisahkan ke modul `lib/`.
3. **Database Repositories**: Kueri dipartisi per entitas (`projects_repo.ts`, `files_repo.ts`, `logs_repo.ts`).
4. **Code Sanitizer & Splitter**: Generator AI secara otomatis memecah output kode menjadi modular files jika komponen melebihi 300 baris.

---

## 3. Struktur Direktori Proyek (Modular Layout)

```
prod-zolu/
├── app/
│   ├── layout.tsx                     # Global layout, fonts, theme (<60 lines)
│   ├── page.tsx                       # Dashboard / project list (<150 lines)
│   ├── builder/[id]/
│   │   └── page.tsx                   # Main AI workspace & generator (<120 lines)
│   ├── api/
│   │   ├── generate/
│   │   │   └── route.ts               # SSE stream from 9Router (<180 lines)
│   │   ├── projects/
│   │   │   ├── route.ts               # CRUD project list (<90 lines)
│   │   │   └── [id]/route.ts          # Single project detail (<110 lines)
│   │   ├── preview/[id]/
│   │   │   └── route.ts               # In-memory virtual sandbox preview (<140 lines)
│   │   └── export/[id]/
│   │       └── route.ts               # ZIP packager & deploy handler (<130 lines)
├── components/
│   ├── common/
│   │   ├── Navbar.tsx                 # Header & brand (<80 lines)
│   │   ├── ThemeToggle.tsx            # Light/Dark switcher (<45 lines)
│   │   └── CustomDropdown.tsx         # Reusable popover dropdown (<120 lines)
│   ├── builder/
│   │   ├── PromptConsole.tsx          # Natural language prompt interface (<160 lines)
│   │   ├── FileExplorer.tsx           # Generated file tree view (<140 lines)
│   │   ├── CodeViewer.tsx             # Syntax highlighted code editor (<180 lines)
│   │   ├── LiveSandbox.tsx            # Real-time responsive iframe preview (<150 lines)
│   │   └── GenerationProgress.tsx     # Step-by-step pipeline status (<90 lines)
├── lib/
│   ├── ai/
│   │   ├── router_client.ts           # 9Router HTTP/SSE client wrapper (<120 lines)
│   │   ├── prompt_builder.ts          # System instructions & code scaffolds (<190 lines)
│   │   └── code_parser.ts             # Multi-file artifact extraction (<170 lines)
├── lib/
│   ├── db/
│   │   ├── client.ts                  # SQLite WAL initialization (<40 lines)
│   │   ├── schema.ts                  # Database DDL (<70 lines)
│   │   ├── projects_repo.ts           # Projects database operations (<130 lines)
│   │   └── files_repo.ts              # Code files database operations (<140 lines)
│   └── utils/
│       ├── zip_generator.ts           # Archive bundler (<95 lines)
│       └── line_validator.ts          # 300-line code guard rule (<50 lines)
├── public/
│   ├── favicon.svg                    # Brand icon
│   └── icon.svg
├── data/
│   └── prod_engine.db                 # SQLite database storage
├── package.json
└── tailwind.config.js
```

---

## 4. Skema Database SQLite (WAL Mode)

```sql
-- Inisialisasi Database
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;

-- 1. Tabel Proyek
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    prompt TEXT NOT NULL,
    stack TEXT DEFAULT 'nextjs-tailwind',
    status TEXT CHECK(status IN ('draft', 'generating', 'completed', 'error')) DEFAULT 'draft',
    preview_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabel File Kode Tergenerate
CREATE TABLE IF NOT EXISTS project_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    content TEXT NOT NULL,
    lines_count INTEGER NOT NULL,
    version INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    UNIQUE(project_id, file_path, version)
);

-- 3. Tabel Log Generasi AI 9Router
CREATE TABLE IF NOT EXISTS generation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    model_name TEXT NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    duration_ms INTEGER,
    status TEXT,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

---

## 5. Integrasi Mesin AI 9Router (`lib/ai/router_client.ts`)

```typescript
// Konfigurasi Klien 9Router
const ROUTER_BASE_URL = 'https://9router.zolu.my.id/v1';
const ROUTER_API_KEY = 'sk-b2a2f6c6f8228b4b-prod01-71d3127b';

export async function call9RouterStreaming(
  prompt: string,
  systemPrompt: string,
  onChunk: (text: string) => void
) {
  const response = await fetch(`${ROUTER_BASE_URL}/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${ROUTER_API_KEY}`
    },
    body: JSON.stringify({
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: prompt }
      ],
      stream: true,
      temperature: 0.2
    })
  });

  if (!response.ok) {
    throw new Error(`9Router Error: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (reader) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ') && line !== 'data: [DONE]') {
        try {
          const json = JSON.parse(line.slice(6));
          const content = json.choices[0]?.delta?.content || '';
          if (content) onChunk(content);
        } catch (e) {}
      }
    }
  }
}
```

---

## 6. Prompting Invariant: Modular Code Decomposition

Sistem AI diwajibkan menyertakan pembagian file yang ketat dalam System Prompt:

```text
ATURAN PRODUKSI KODE ZOLU ENGINE:
1. Hasilkan aplikasi web fullstack fungsional lengkap (Next.js App Router + Tailwind + SQLite).
2. Setiap file hasil generasi TIDAK BOLEH lebih dari 300 baris. Jika logika kompleks, pecah menjadi sub-komponen atau helper di direktori terpisah.
3. Format output wajib menggunakan penanda file:
   [FILE: path/to/file.tsx]
   ...kode file...
   [/FILE]
4. Utamakan Light Mode default, mobile-responsive, dan komponen interaktif popover in-page.
```

---

## 7. Tahapan Implementasi & Deployment

1. **Inisialisasi Proyek**:
   - `mkdir /home/ubuntu/apps/zolu-prod`
   - Setup Next.js 14 + Tailwind + Lucide + Better-SQLite3.
2. **Implementasi Database & Repositori**:
   - Pasang DDL SQLite WAL di `lib/db/`.
3. **Pembangunan UI & Workspace**:
   - Buat Dashboard, Prompt Console, Tree File, dan Live Sandbox Preview.
4. **Koneksi Engine 9Router**:
   - Sambungkan API key & streaming route handler.
5. **Konfigurasi Server & Cloudflare Tunnel**:
   - `pm2 start npm --name "zolu-prod" -- run start -- -p 3012`
   - Arahkan hostname `prod.zolu.my.id` ke `http://localhost:3012`.
