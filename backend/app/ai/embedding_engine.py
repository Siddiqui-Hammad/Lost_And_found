import numpy as np
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TextEmbeddingEngine:
    """
    Pretrained Text Embedding & Semantic Similarity Engine.
    Uses Sentence Transformers (all-MiniLM-L6-v2) if available;
    otherwise employs optimized sub-word tokenized TF-IDF Cosine Similarity.
    """
    def __init__(self):
        self.model = None
        self._init_model()

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[AI Engine] Loaded pretrained SentenceTransformer (all-MiniLM-L6-v2).")
        except Exception:
            self.model = None
            print("[AI Engine] Running optimized TF-IDF Subword Cosine Similarity Engine.")

    def compute_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0
        
        t1 = text1.strip().lower()
        t2 = text2.strip().lower()
        
        if t1 == t2:
            return 100.0

        if self.model is not None:
            try:
                embeddings = self.model.encode([t1, t2])
                cos_sim = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
                score = float(np.clip(cos_sim, 0.0, 1.0)) * 100.0
                return round(score, 2)
            except Exception as e:
                print(f"[AI] SentenceTransformer error: {e}, falling back to TF-IDF")

        # High-precision n-gram TF-IDF Cosine Similarity
        try:
            vectorizer = TfidfVectorizer(ngram_range=(1, 3), analyzer="char_wb")
            tfidf_matrix = vectorizer.fit_transform([t1, t2])
            sim_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            score = float(sim_matrix[0][0]) * 100.0
            return round(score, 2)
        except Exception:
            # Word overlap fallback
            w1 = set(t1.split())
            w2 = set(t2.split())
            if not w1 or not w2:
                return 0.0
            overlap = len(w1.intersection(w2)) / max(len(w1), len(w2))
            return round(overlap * 100.0, 2)

embedding_engine = TextEmbeddingEngine()
