from functools import lru_cache
from .config import EMBED_MODEL
@lru_cache(maxsize=1)
def model():
    from fastembed import TextEmbedding
    return TextEmbedding(model_name=EMBED_MODEL)
def embed(text: str):
    vector=list(model().embed([text[:8000]]))[0].tolist()
    if len(vector)!=384: raise ValueError('Model must produce 384-dim embeddings')
    return vector
