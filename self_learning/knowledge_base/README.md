# Knowledge Base (Runtime Store)

Direktori ini adalah lokasi default memori persisten Claudia Brain:

| Berkas | Ditulis oleh | Isi |
| :--- | :--- | :--- |
| `learned_patterns.json` | `KnowledgeStore` (`storage.py`) | Heuristik sukses & anti-pola hasil siklus self-learning / task flow |
| `reflections.json` | `ReflexionMemoryStore` (`reflection.py`) | Memori episodik refleksi 4-kuadran |

Kedua berkas **tidak dilacak git** (lihat `.gitignore`): isinya spesifik per mesin dan berubah
setiap kali benchmark atau task flow dijalankan. Unit test tidak pernah menulis ke sini —
seluruh test memakai direktori sementara.

Untuk memakai lokasi lain, berikan `storage_path` saat membuat store:

```python
from pathlib import Path
from self_learning import KnowledgeStore, ReflexionMemoryStore

store = KnowledgeStore(Path("~/.claudia/learned_patterns.json").expanduser())
memory = ReflexionMemoryStore(Path("~/.claudia/reflections.json").expanduser())
```
