"""Modul Runtime LLM nyata: panggil API provider eksternal untuk eksekusi tugas agen.

Mendukung dua protokol provider secara native:
1. OpenAI-compatible (`/v1/chat/completions`): OpenAI, Azure OpenAI, Ollama, vLLM,
   Groq, OpenRouter, dsb.
2. Google Gemini (`/v1beta/models/{model}:generateContent`).

Kelas `LLMExecutor` menggabungkan semantic search dari KnowledgeStore dengan
prompt builder, sehingga setiap panggilan LLM menerima konteks pengetahuan
yang paling relevan secara empiris (bukan seluruh store yang panjangnya tak terbatas).
"""

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .storage import KnowledgeStore, KnowledgeEntry


@dataclass
class LLMMessage:
    """Satu pesan dalam percakapan LLM."""

    role: str  # 'system', 'user', atau 'assistant'
    content: str


@dataclass
class LLMResponse:
    """Laporan hasil satu panggilan LLM."""

    text: str
    provider: str
    model: str
    latency_ms: float
    usage: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)


class LLMError(RuntimeError):
    """Galat runtime LLM: jaringan, autentikasi, atau respons tidak valid."""


class PromptOptimizer:
    """Optimasi prompt tahap terpisah (approach #2): tulis ulang prompt bahasa
    Indonesia menjadi instruksi bahasa Inggris yang lebih presisi sebelum
    diproses LLM utama. Optimizer ini tidak menjawab tugas; ia hanya
    menyempurnakan instruksi.
    """

    def __init__(self, provider: Any, timeout: Optional[float] = None):
        self.provider = provider
        if timeout is not None and hasattr(provider, "timeout"):
            provider.timeout = timeout

    def optimize(
        self,
        task_name: str,
        intended_goal: str,
        acceptance_criteria: List[str],
        reflection_feedback: Optional[str] = None,
    ) -> LLMResponse:
        """Minta LLM menulis ulang tugas menjadi prompt Inggris yang ringkas dan operatif."""
        criteria_block = "\n".join(f"- {c}" for c in acceptance_criteria)
        reflection_block = (
            f"\nKonteks kegagalan sebelumnya (jangan dijawab, hanya pertimbangkan):\n{reflection_feedback}"
            if reflection_feedback
            else ""
        )
        messages = [
            LLMMessage(
                role="system",
                content=(
                    "You are a prompt optimizer, not an answer generator. "
                    "Rewrite the user's task into one concise, unambiguous English instruction "
                    "that preserves every explicit requirement, constraint, and expected output. "
                    "Do not add requirements that were not requested. Do not solve the task. "
                    "Return only the optimized English prompt."
                ),
            ),
            LLMMessage(
                role="user",
                content=(
                    f"Task name: {task_name}\n"
                    f"Goal: {intended_goal}\n"
                    f"Acceptance criteria:\n{criteria_block}"
                    f"{reflection_block}"
                ),
            ),
        ]
        return self.provider.complete(messages)


def _http_post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: float) -> Dict[str, Any]:
    """Kirim POST JSON dan kembalikan respons JSON. Melempar LLMError dengan pesan jelas."""
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={**headers, "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", errors="replace")[:500]
        except OSError:
            pass
        raise LLMError(f"HTTP {e.code} dari LLM provider: {detail}") from e
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        raise LLMError(f"Gagal terhubung ke LLM provider: {e}") from e


class OpenAIChatProvider:
    """Provider untuk endpoint OpenAI-compatible chat completions."""

    provider_name = "openai_compatible"

    def __init__(
        self,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        timeout: float = 120.0,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = (
            api_key
            or os.environ.get("OPENAI_API_KEY", "")
            or os.environ.get("OPENROUTER_API_KEY", "")
        )
        self.temperature = temperature
        self.timeout = timeout

    def complete(self, messages: List[LLMMessage]) -> LLMResponse:
        """Kirim percakapan ke endpoint chat completions dan kembalikan respons terstruktur."""
        if not self.api_key:
            raise LLMError(
                "API key belum diset. Berikan lewat parameter api_key atau environment variable OPENAI_API_KEY."
            )
        url = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": self.temperature,
        }
        t0 = time.perf_counter()
        raw = _http_post_json(url, headers, payload, self.timeout)
        latency = (time.perf_counter() - t0) * 1000.0
        try:
            text = raw["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise LLMError(f"Struktur respons provider tidak dikenal: {raw}") from e
        return LLMResponse(
            text=text,
            provider=self.provider_name,
            model=self.model,
            latency_ms=latency,
            usage=raw.get("usage", {}),
            raw=raw,
        )


class GeminiProvider:
    """Provider untuk Google Gemini generateContent API."""

    provider_name = "gemini"

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        api_key: Optional[str] = None,
        temperature: float = 0.2,
        timeout: float = 120.0,
    ):
        self.model = model
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.temperature = temperature
        self.timeout = timeout

    def complete(self, messages: List[LLMMessage]) -> LLMResponse:
        """Kirim percakapan ke Gemini. Pesan system digabung ke user pertama (konvensi Gemini)."""
        if not self.api_key:
            raise LLMError(
                "API key belum diset. Berikan lewat parameter api_key atau environment variable GEMINI_API_KEY."
            )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        system_parts: List[str] = []
        contents: List[Dict[str, Any]] = []
        for m in messages:
            if m.role == "system":
                system_parts.append(m.content)
            else:
                contents.append({"role": "model" if m.role == "assistant" else "user", "parts": [{"text": m.content}]})
        if system_parts:
            sys_text = "\n\n".join(system_parts)
            if contents and contents[0]["role"] == "user":
                contents[0]["parts"][0]["text"] = f"{sys_text}\n\n{contents[0]['parts'][0]['text']}"
            else:
                contents.insert(0, {"role": "user", "parts": [{"text": sys_text}]})
        payload = {
            "contents": contents,
            "generationConfig": {"temperature": self.temperature},
        }
        t0 = time.perf_counter()
        raw = _http_post_json(url, {}, payload, self.timeout)
        latency = (time.perf_counter() - t0) * 1000.0
        try:
            text = raw["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as e:
            raise LLMError(f"Struktur respons Gemini tidak dikenal: {raw}") from e
        return LLMResponse(
            text=text,
            provider=self.provider_name,
            model=self.model,
            latency_ms=latency,
            usage=raw.get("usageMetadata", {}),
            raw=raw,
        )


def build_contextual_prompt(
    task_name: str,
    intended_goal: str,
    acceptance_criteria: List[str],
    relevant_knowledge: List[KnowledgeEntry],
    reflection_feedback: Optional[str] = None,
) -> List[LLMMessage]:
    """Rakit pesan LLM: system + user, dengan konteks knowledge base yang relevan."""
    knowledge_block = ""
    if relevant_knowledge:
        lines = []
        for idx, entry in enumerate(relevant_knowledge, 1):
            label = entry.category.replace("_", " ").upper()
            lines.append(f"{idx}. [{label}] (relevansi {entry.impact_score:+.1f}) {entry.pattern} — {entry.explanation}")
        knowledge_block = (
            "=== PENGETAHUAN TERKAIT DARI KNOWLEDGE BASE ===\n"
            + "\n".join(lines)
            + "\n=== SELESAI ===\n"
        )
    criteria_block = "\n".join(f"- {c}" for c in acceptance_criteria)
    system = (
        "Kamu adalah agen eksekutor tugas yang presisi, empiris, dan tidak berasumsi. "
        "Ikuti konteks pengetahuan yang diberikan bila relevan. "
        "Berikan jawaban akhir sebagai output langsung tanpa meta-komentar."
    )
    user_content = (
        f"=== TUGAS: {task_name} ===\n"
        f"Tujuan   : {intended_goal}\n"
        f"Kriteria :\n{criteria_block}\n"
        f"{knowledge_block}"
    )
    if reflection_feedback:
        user_content += f"\n=== REFLEKSI KEGAGALAN SEBELUMNYA ===\n{reflection_feedback}\n=== SELESAI ===\n"
    user_content += "\nBerikan hasil akhir sekarang."
    return [LLMMessage(role="system", content=system), LLMMessage(role="user", content=user_content)]


class LLMExecutor:
    """Eksekutor tugas nyata berbasis LLM: mengambil konteks semantik dari KnowledgeStore
    lalu memanggil provider LLM, dan menyimpan heuristik hasil ke store kembali.
    """

    def __init__(
        self,
        provider: Any,
        knowledge_store: Optional[KnowledgeStore] = None,
        prompt_optimizer: Optional[PromptOptimizer] = None,
        max_retrieval: int = 5,
        min_relevance: float = 0.05,
    ):
        self.provider = provider
        self.store = knowledge_store if knowledge_store is not None else KnowledgeStore()
        self.prompt_optimizer = prompt_optimizer
        self.max_retrieval = max_retrieval
        self.min_relevance = min_relevance

    def retrieve_relevant_knowledge(self, query: str) -> List[KnowledgeEntry]:
        """Ambil top-k pengetahuan paling relevan via semantic search TF-IDF."""
        scored = self.store.search_semantic(query, limit=self.max_retrieval, min_score=self.min_relevance)
        return [entry for entry, _score in scored]

    def execute(
        self,
        task_name: str,
        intended_goal: str,
        acceptance_criteria: List[str],
        reflection_feedback: Optional[str] = None,
        max_attempts: int = 3,
    ) -> Dict[str, Any]:
        """Jalankan siklus: retrieve konteks → panggil LLM → validasi → distil hasil.

        `acceptance_criteria` dapat berupa string kriteria teks, atau fungsi
        validator callable yang menerima `str` respons LLM dan mengembalikan bool.
        """
        text_validators = [c for c in acceptance_criteria if callable(c)]
        criteria_labels = [str(c) for c in acceptance_criteria if not callable(c)]
        last_error: Optional[str] = None
        history: List[Dict[str, Any]] = []

        for attempt in range(1, max_attempts + 1):
            optimized_goal = intended_goal
            optimizer_latency_ms = None
            if self.prompt_optimizer is not None:
                optimized = self.prompt_optimizer.optimize(
                    task_name=task_name,
                    intended_goal=intended_goal,
                    acceptance_criteria=criteria_labels,
                    reflection_feedback=reflection_feedback,
                )
                optimized_goal = optimized.text.strip()
                optimizer_latency_ms = optimized.latency_ms

            retrieval_query = f"{task_name} {optimized_goal}"
            retrieved = self.retrieve_relevant_knowledge(retrieval_query)
            messages = build_contextual_prompt(
                task_name=task_name,
                intended_goal=optimized_goal,
                acceptance_criteria=criteria_labels,
                relevant_knowledge=retrieved,
                reflection_feedback=reflection_feedback,
            )
            try:
                response = self.provider.complete(messages)
            except LLMError as err:
                last_error = str(err)
                history.append({
                    "attempt": attempt,
                    "error": last_error,
                    "retrieved": len(retrieved),
                    "optimizer_used": self.prompt_optimizer is not None,
                })
                continue

            all_valid = True
            for validator in text_validators:
                if not validator(response.text):
                    all_valid = False
                    break
            if all_valid:
                entry = KnowledgeEntry(
                    entry_id=f"llm-distill-{task_name}-{attempt}",
                    task_type=task_name,
                    category="heuristic",
                    pattern=f"Eksekusi LLM berhasil untuk '{intended_goal[:80]}'",
                    explanation=(f"Provider={response.provider}, model={response.model}, latensi={response.latency_ms:.1f}ms"),
                    impact_score=1.0,
                    metadata={
                        "provider": response.provider,
                        "model": response.model,
                        "latency_ms": round(response.latency_ms, 2),
                        "attempts": attempt,
                        "retrieved_count": len(retrieved),
                        "optimizer_used": self.prompt_optimizer is not None,
                        "optimizer_latency_ms": optimizer_latency_ms,
                        "optimized_goal": optimized_goal if self.prompt_optimizer else None,
                    },
                )
                self.store.add(entry)
                return {
                    "success": True,
                    "attempt": attempt,
                    "result": response.text,
                    "response": response,
                    "retrieved_count": len(retrieved),
                    "retrieved_entries": [e.entry_id for e in retrieved],
                    "optimized_goal": optimized_goal if self.prompt_optimizer else None,
                    "history": history,
                }
            last_error = "Validator menolak respons LLM."
            history.append({
                "attempt": attempt,
                "error": last_error,
                "retrieved": len(retrieved),
                "optimizer_used": self.prompt_optimizer is not None,
            })

        return {
            "success": False,
            "attempts": max_attempts,
            "last_error": last_error,
            "history": history,
        }
