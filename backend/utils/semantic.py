"""
Semantic similarity with a sentence-embedding model (all-MiniLM-L6-v2),
loaded directly through `transformers` and falling back to TF-IDF when the
model is unavailable (no internet / low-memory hosts).

Set ATS_SEMANTIC_MODEL=off to force the TF-IDF fallback.
"""

import os
import threading
from typing import List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

MODEL_NAME = os.getenv("ATS_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


class SemanticEncoder:
    def __init__(self):
        self._lock = threading.Lock()
        self._tokenizer = None
        self._model = None
        self._torch = None
        self._done = threading.Event()
        self._cache: dict = {}
        self._cache_lock = threading.Lock()
        self._cache_max = 6000
        self.backend = "tfidf"

    def _load(self):
        if self._done.is_set():
            return
        with self._lock:  # concurrent callers block here until loading finishes
            if self._done.is_set():
                return
            try:
                self._load_model()
            finally:
                self._done.set()

    def _load_model(self):
        if os.getenv("ATS_SEMANTIC_MODEL", "on").lower() in {"off", "0", "false", "no"}:
            return
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer
            try:
                tok = AutoTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
                model = AutoModel.from_pretrained(MODEL_NAME, local_files_only=True)
            except Exception:
                tok = AutoTokenizer.from_pretrained(MODEL_NAME)
                model = AutoModel.from_pretrained(MODEL_NAME)
            model.eval()
            self._torch, self._tokenizer, self._model = torch, tok, model
            self.backend = "embeddings"
            print(f"[OK] Semantic model loaded: {MODEL_NAME}")
        except Exception as e:
            print(f"[INFO] Semantic model unavailable ({e.__class__.__name__}); using TF-IDF similarity")

    def warmup_async(self):
        threading.Thread(target=self._load, daemon=True).start()

    @property
    def available(self) -> bool:
        self._load()
        return self._model is not None

    def encode(self, texts: List[str]) -> Optional[np.ndarray]:
        if not texts or not self.available:
            return None
        # Job postings and resume lines repeat across requests: cache their vectors
        missing = list(dict.fromkeys(t for t in texts if t not in self._cache))
        if missing:
            torch = self._torch
            with torch.no_grad():
                for i in range(0, len(missing), 32):
                    chunk = missing[i:i + 32]
                    batch = self._tokenizer(chunk, padding=True, truncation=True,
                                            max_length=256, return_tensors="pt")
                    out = self._model(**batch).last_hidden_state
                    mask = batch["attention_mask"].unsqueeze(-1).float()
                    pooled = (out * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
                    for text, vec in zip(chunk, torch.nn.functional.normalize(pooled, dim=1).numpy()):
                        self._cache_put(text, vec)
        return np.vstack([self._cache[t] for t in texts])

    def _cache_put(self, text: str, vec: np.ndarray):
        with self._cache_lock:
            if len(self._cache) >= self._cache_max:
                # Drop the oldest quarter (dicts keep insertion order)
                for key in list(self._cache)[: self._cache_max // 4]:
                    self._cache.pop(key, None)
            self._cache[text] = vec


encoder = SemanticEncoder()


def tfidf_similarity_matrix(a: List[str], b: List[str]) -> np.ndarray:
    """Cosine similarity between two lists of texts using word + char n-gram TF-IDF."""
    try:
        vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, min_df=1)
        m = vec.fit_transform(a + b)
        return cosine_similarity(m[: len(a)], m[len(a):])
    except ValueError:
        return np.zeros((len(a), len(b)))


def similarity_matrix(a: List[str], b: List[str]) -> np.ndarray:
    """Pairwise similarity (rows: a, cols: b)."""
    if not a or not b:
        return np.zeros((len(a), len(b)))
    ea = encoder.encode(a)
    if ea is not None:
        eb = encoder.encode(b)
        return ea @ eb.T
    return tfidf_similarity_matrix(a, b)


def calibrate(sim: float) -> float:
    """
    Map raw similarity to 0..1 "how well is this covered".
    MiniLM: unrelated ~0.0-0.25, same field but different work ~0.3-0.4, strong match >= 0.65.
    Char TF-IDF has a different range, so it's mapped separately.
    """
    if encoder.backend == "embeddings":
        lo, hi = 0.25, 0.65
    else:
        lo, hi = 0.08, 0.45
    return float(np.clip((sim - lo) / (hi - lo), 0.0, 1.0))
