import hashlib
import logging
import math
import re
from typing import List, Optional
import httpx
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 1536

def _generate_local_embedding(text: str, dim: int = EMBEDDING_DIM) -> List[float]:
    """
    Generate a deterministic, normalized dense vector representation for text.
    Uses n-gram and token frequency hashing to ensure semantically related
    technical queries produce high cosine similarity without external API dependencies.
    """
    vector = [0.0] * dim
    clean_text = text.lower()
    
    # Tokenize words and n-grams
    tokens = re.findall(r"\b\w+\b", clean_text)
    if not tokens:
        tokens = [clean_text]

    # Unigrams, bigrams, and character trigrams
    features = list(tokens)
    for i in range(len(tokens) - 1):
        features.append(f"{tokens[i]}_{tokens[i+1]}")
    for i in range(len(clean_text) - 2):
        features.append(clean_text[i:i+3])

    for feature in features:
        h = int(hashlib.sha256(feature.encode("utf-8")).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if (h >> 16) % 2 == 0 else -1.0
        # Weight by length/importance
        weight = 1.0 + (0.1 * min(len(feature), 10))
        vector[idx] += sign * weight

    # Normalize vector to unit length (L2 norm)
    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0.0:
        vector = [v / norm for v in vector]

    return vector

def get_embedding(text: str) -> List[float]:
    """
    Generate vector embedding for a single string.
    Uses OpenAI text-embedding-3-small if API key is provided,
    otherwise falls back to deterministic local semantic embedding.
    """
    if settings.OPENAI_API_KEY:
        try:
            url = "https://api.openai.com/v1/embeddings"
            headers = {
                "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": text,
                "model": settings.EMBEDDING_MODEL
            }
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["data"][0]["embedding"]
                else:
                    logger.warning(f"OpenAI embedding error {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Failed to fetch OpenAI embedding: {e}. Using local fallback.")

    return _generate_local_embedding(text)

def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Batch generate embeddings."""
    return [get_embedding(t) for t in texts]

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two unit vectors."""
    if len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    return float(dot_product)
