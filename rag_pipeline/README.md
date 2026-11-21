# PgVector RAG Pipeline - Educational Content Retrieval & Generation

A production-ready RAG pipeline with PostgreSQL/pgvector for semantic search and OpenRouter LLM API for intelligent educational responses. Built-in anti-hallucination features with LangChain-inspired grounding verification.

## Quick Setup

### Installation
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac
pip install --upgrade pip
pip install psycopg[binary] pgvector sentence-transformers openai python-dotenv numpy
```

### .env Configuration
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/edu_rag
PGVECTOR_TABLE=curriculum_chunks
EMBEDDING_BACKEND=local
NOMIC_EMBEDDING_MODEL=nomic-ai/nomic-embed-text-v1.5
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=openai/gpt-4o-mini
```

## Basic Usage

```python
from pgvector_rag_pipeline import PgVectorPromptRAGPipeline, RetrievalFilters, create_embedding_provider, create_openrouter_client
import psycopg
from dotenv import load_dotenv
import os

load_dotenv()
llm = create_openrouter_client()
embedder = create_embedding_provider(openrouter_client=llm)

with psycopg.connect(os.getenv("DATABASE_URL")) as conn:
    pipeline = PgVectorPromptRAGPipeline(
        pg_conn=conn,
        embedding_provider=embedder,
        llm_client=llm,
        llm_model=os.getenv("OPENROUTER_MODEL"),
    )
    
    prompt = """
    Grade: 4
    Course: Fractions & Decimals
    Concept: fractions_like_denominators
    Goal: story_analogy
    Rules: Use pizza slice visuals, keep sentences short
    """
    
    # ⭐ RECOMMENDED: Grounded RAG with anti-hallucination
    result = pipeline.answer_grounded(prompt, filters=RetrievalFilters(grade_level=4))
    print(result.answer_text)
    print(f"Confidence: {result.confidence}")
    print(f"Has Hallucinations: {result.has_hallucinations}")
    
    # Alternative: Standard RAG
    # result = pipeline.run(prompt, top_k=4)
    # print(result.answer_text)
```

## Key Features

| Feature | Benefit |
|---------|---------|
| **Embedding Caching** | 2-5x faster repeated queries |
| **Lazy Model Loading** | Faster startup, serverless-friendly |
| **Batch Embedding** | 3-10x faster for multiple queries |
| **Vector HNSW Index** | 40-60% faster database queries |
| **Anti-Hallucination** | Confidence scoring + hallucination detection |
| **Query Extraction** | Regex-based curriculum field extraction |
| **Source Attribution** | Full traceability of answer sources |

## Pipeline Methods

### `answer_grounded()` ⭐ RECOMMENDED
```python
result = pipeline.answer_grounded(
    question="Your question here",
    filters=RetrievalFilters(grade_level=4, course_name="Math"),
    top_k=4
)
```
Returns: `GroundedRAGResult` with:
- `answer_text`: Final grounded response
- `confidence`: HIGH/MEDIUM/LOW
- `has_hallucinations`: Bool flag
- `unsupported_claims`: List of ungrounded claims
- `sources`: Source attribution data

### `run()` - Standard RAG
```python
result = pipeline.run(
    generated_prompt="Your prompt",
    top_k=4,
    filters=RetrievalFilters(...),
    temperature=0.4
)
```
Returns: `RAGGenerationResult` with answer, chunks, query, and full prompt

### Other Methods
- `retrieve_top_k()`: Retrieve chunks only
- `generate_text_prompt_response()`: LLM generation only
- `extract_retrieval_query()`: Extract curriculum fields
- `_detect_hallucinations()`: Check for unsupported claims

## Input Models

### RetrievalFilters (Optional)
```python
RetrievalFilters(
    grade_level=4,
    course_name="Fractions",
    concept_id="fractions_like_denominators",
    difficulty_tiers=["foundational", "standard"],
    chunk_roles=["explanation", "example"]
)
```

## Output Models

### GroundedRAGResult
```python
@dataclass
class GroundedRAGResult:
    answer_text: str                           # Answer with grounding
    confidence: str                            # HIGH/MEDIUM/LOW
    confidence_score: float                    # 0-1
    has_hallucinations: bool                   # Potential hallucinations detected
    unsupported_claims: List[str]              # Claims not in curriculum
    is_grounded: bool                          # Has curriculum context
    sources: List[Dict[str, Any]]              # Source attribution
    retrieved_chunks: List[RetrievedChunk]     # Actual chunks used
```

### RetrievedChunk
```python
@dataclass
class RetrievedChunk:
    chunk_id: str                    # Identifier
    content: str                     # Curriculum content
    similarity: float                # 0-1 score
    metadata: Dict[str, Any]         # grade_level, course_name, etc.
```

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Embedding (cached) | 1-5ms | LRU cache hit |
| Embedding (new) | 50-200ms | Local model or API |
| Vector Search | 50-150ms | With HNSW index |
| LLM Generation | 1-5s | Model dependent |
| **Total (typical)** | **1.1-5.2s** | Most queries cached |

Memory: LocalNomicEmbeddingProvider ~250MB (model + cache), OpenRouterEmbeddingProvider ~50MB cache.

## Database Schema

```sql
CREATE TABLE curriculum_chunks (
    chunk_id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(768),
    grade_level INTEGER,
    course_name VARCHAR(255),
    concept_id VARCHAR(255),
    difficulty_tier VARCHAR(50),
    chunk_role VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create HNSW index for fast search
CREATE INDEX ON curriculum_chunks USING hnsw (embedding vector_cosine_ops) 
WITH (m=16, ef_construction=200);
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No results | Check PGVECTOR_TABLE exists; verify filters aren't restrictive; set `use_extracted_query=False` |
| Slow embedding | First embedding slower (model loading), subsequent cached; check OpenRouter rate limits |
| Slow search | Verify HNSW index exists; adjust `ef_search`; run `ANALYZE table` |
| Poor answers | Check retrieved chunks relevance; adjust `top_k` (6-8); lower `temperature`; verify filter metadata |
| Hallucinations | Use `answer_grounded()` instead of `run()`; check `has_hallucinations` flag and `unsupported_claims` |

## API Reference

### PgVectorPromptRAGPipeline Methods

| Method | Purpose |
|--------|---------|
| `answer_grounded(question, filters, top_k)` | RAG with anti-hallucination ⭐ |
| `run(generated_prompt, top_k, filters, temperature)` | Standard RAG |
| `retrieve_top_k(query, filters, top_k)` | Retrieve chunks only |
| `generate_text_prompt_response(prompt, temperature)` | LLM only |
| `build_final_prompt(prompt, chunks)` | Assemble final prompt (static) |
| `extract_retrieval_query(prompt)` | Extract fields (static) |

### EmbeddingProvider Interface

```python
def embed(text: str, task_prefix: str = "search_query") -> List[float]
def embed_batch(texts: List[str], task_prefix: str = "search_query") -> List[List[float]]
```

Implementations:
- `LocalNomicEmbeddingProvider`: Lazy-loaded Nomic embeddings with LRU cache
- `OpenRouterEmbeddingProvider`: API-based embeddings with caching

## Optimizations Implemented

1. **Embedding Caching**: LRU cache (128-256 entries) with MD5 hash keys
2. **Lazy Loading**: Model loads only on first use (@property pattern)
3. **Batch Processing**: Vectorized embedding for multiple texts
4. **HNSW Tuning**: Configured m=16, ef_construction=200 for speed/quality tradeoff
5. **Query Extraction**: Regex-based extraction of curriculum-relevant fields
6. **Data Efficiency**: Single-pass metadata merging, direct tuple unpacking
7. **Anti-Hallucination**: Grounded prompting + confidence scoring + unsupported claim detection

## Best Practices

- **Always use `answer_grounded()`** for production (better accuracy, hallucination detection)
- **Monitor `has_hallucinations`** flag and filter low-confidence responses
- **Batch embeddings** when processing multiple queries
- **Tune `top_k`**: Start with 4, increase to 6-8 for harder questions
- **Keep `temperature`** at 0.3-0.4 for educational content (consistency over creativity)
- **Index embeddings** with HNSW for fast retrieval (scales to millions)
- **Cache frequently used queries** at application level for further speedup

## License

[Add your license here]
