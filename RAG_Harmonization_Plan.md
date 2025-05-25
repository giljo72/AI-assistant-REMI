# Knowledge/RAG/Vector/Memory Harmonization Plan

## Overview
This plan addresses the critical architectural gap where Knowledge retrieval, RAG, Vector search, and Memory systems are not properly integrated with the prompt hierarchy, preventing the system from achieving its full context-aware potential.

## Current State Analysis

### 1. Vector Store (pgvector)
- ✅ PostgreSQL with pgvector extension configured
- ✅ 768-dimensional embedding support
- ✅ Cosine similarity search implemented
- ❌ Using mock embeddings only
- ❌ No real embedding model integration

### 2. Document Processing
- ✅ Basic chunking implemented (1000 chars, 200 overlap)
- ✅ Text file processing works
- ❌ PDF, DOCX, etc. are placeholders
- ❌ No document structure preservation
- ❌ No real embedding generation

### 3. RAG Integration
- ✅ Context building from chat history
- ✅ System/user prompt integration
- ❌ Broken `search_chat_context` function
- ❌ No prompt-aware retrieval
- ❌ No context optimization

### 4. Model Orchestration
- ✅ LLM management implemented
- ❌ No embedding model management
- ❌ No unified model lifecycle

## Implementation Phases

### Phase 1: Embedding Service Foundation (Week 1)
1. **Create Embedding Service**
   - [ ] Implement `backend/app/services/embedding_service.py`
   - [ ] Integrate sentence-transformers or NV embedding models
   - [ ] Add embedding model to model orchestrator
   - [ ] Implement caching for embeddings

2. **Update Vector Store**
   - [ ] Replace mock embeddings with real service
   - [ ] Add batch embedding support
   - [ ] Implement embedding dimension validation

### Phase 2: Document Processing Enhancement (Week 2)
1. **Expand Document Parsers**
   - [ ] Implement PyPDF2/pdfplumber for PDFs
   - [ ] Implement python-docx for Word documents
   - [ ] Add markdown/code file special handling
   - [ ] Preserve document structure metadata

2. **Intelligent Chunking**
   - [ ] Implement semantic chunking based on paragraphs/sections
   - [ ] Add heading hierarchy preservation
   - [ ] Include metadata in chunks (title, section, page)

### Phase 3: RAG-Prompt Integration (Week 3)
1. **Fix Chat Context Retrieval**
   - [ ] Implement proper `search_chat_context` function
   - [ ] Connect to semantic search with project context
   - [ ] Add relevance scoring

2. **Context-Aware Retrieval**
   - [ ] Implement retrieval strategies per context mode:
     - Deep Research: More chunks, lower threshold
     - Quick Response: Fewer chunks, higher threshold
     - Creative: Balance relevance with diversity
     - Self-Aware: Prioritize technical docs
   - [ ] Add prompt-influenced query expansion

### Phase 4: Context Optimization (Week 4)
1. **Token-Aware Context Building**
   - [ ] Implement token counting for context
   - [ ] Add dynamic context pruning
   - [ ] Prioritize by relevance scores
   - [ ] Handle context overflow gracefully

2. **Memory Integration**
   - [ ] Add conversation memory to embeddings
   - [ ] Implement memory consolidation
   - [ ] Create memory retrieval patterns

## Technical Implementation Details

### 1. Embedding Service Architecture
```python
# backend/app/services/embedding_service.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Optional
import asyncio
from functools import lru_cache

class EmbeddingService:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model = None
        self.model_name = model_name
        self.dimension = 768
        
    async def initialize(self):
        """Load embedding model asynchronously"""
        self.model = await asyncio.to_thread(
            SentenceTransformer, self.model_name
        )
        
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        if not self.model:
            await self.initialize()
        embedding = await asyncio.to_thread(
            self.model.encode, text, normalize_embeddings=True
        )
        return embedding.tolist()
        
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self.model:
            await self.initialize()
        embeddings = await asyncio.to_thread(
            self.model.encode, texts, normalize_embeddings=True
        )
        return embeddings.tolist()
```

### 2. Enhanced Document Processor
```python
# backend/app/document_processing/enhanced_processor.py
from typing import List, Dict, Any
import pdfplumber
from docx import Document
import markdown
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    
class EnhancedDocumentProcessor:
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        
    async def process_pdf(self, filepath: str) -> List[DocumentChunk]:
        chunks = []
        with pdfplumber.open(filepath) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                sections = self._extract_sections(text)
                for section in sections:
                    chunk = DocumentChunk(
                        content=section['content'],
                        metadata={
                            'page': i + 1,
                            'section': section['title'],
                            'type': 'pdf'
                        }
                    )
                    chunk.embedding = await self.embedding_service.embed_text(
                        chunk.content
                    )
                    chunks.append(chunk)
        return chunks
```

### 3. Context-Aware Retrieval
```python
# backend/app/rag/context_aware_retrieval.py
class ContextAwareRetrieval:
    def __init__(self, vector_store, embedding_service):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        
    async def retrieve_for_context(
        self,
        query: str,
        project_id: str,
        context_mode: str,
        system_prompts: List[str],
        user_prompts: List[str]
    ) -> List[DocumentChunk]:
        # Expand query based on prompts
        expanded_query = await self._expand_query(
            query, system_prompts, user_prompts
        )
        
        # Adjust retrieval parameters based on context mode
        params = self._get_retrieval_params(context_mode)
        
        # Embed expanded query
        query_embedding = await self.embedding_service.embed_text(expanded_query)
        
        # Retrieve chunks with context-aware scoring
        chunks = await self.vector_store.search(
            query_embedding,
            project_id=project_id,
            limit=params['limit'],
            threshold=params['threshold']
        )
        
        return chunks
```

## Testing Strategy

### 1. Unit Tests
- [ ] Embedding service tests
- [ ] Document processor tests
- [ ] Retrieval strategy tests

### 2. Integration Tests
- [ ] End-to-end document processing
- [ ] Chat with RAG context
- [ ] Performance benchmarks

### 3. Quality Tests
- [ ] Retrieval relevance metrics
- [ ] Context coherence evaluation
- [ ] Response quality assessment

## Success Metrics

1. **Technical Metrics**
   - Embedding generation time < 100ms
   - Retrieval latency < 500ms
   - Context building < 1s
   - Memory usage stable under load

2. **Quality Metrics**
   - Retrieval precision > 0.8
   - Context relevance score > 0.7
   - User satisfaction improvement

3. **Functional Metrics**
   - All document types processed
   - Context modes properly influence retrieval
   - Prompts effectively guide search

## Risk Mitigation

1. **Performance Risks**
   - Implement caching for embeddings
   - Use batch processing where possible
   - Monitor memory usage

2. **Quality Risks**
   - A/B test retrieval strategies
   - Collect user feedback
   - Implement fallback mechanisms

3. **Integration Risks**
   - Maintain backward compatibility
   - Phase rollout with feature flags
   - Comprehensive testing

## Next Steps

1. Review and approve plan
2. Set up development branch
3. Begin Phase 1 implementation
4. Weekly progress reviews