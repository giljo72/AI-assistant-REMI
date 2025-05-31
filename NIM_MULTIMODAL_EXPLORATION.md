# NIM Multimodal Document Processing Exploration Plan

## Executive Summary
Explore NVIDIA NIM's multimodal document processing capabilities to enhance our current text-only extraction with advanced features like table detection, chart extraction, and visual understanding.

## Current State vs. Vision

### Current Implementation (Working)
- **Text Extraction**: PyPDF2, python-docx, pandas
- **Embeddings**: NVIDIA NIM embeddings (1024-dim)
- **Limitations**: Text-only, no visual understanding
- **VRAM Usage**: ~1.2GB for embeddings only

### NIM Multimodal Vision
- **Visual Intelligence**: Extract charts, tables, images
- **Structured Data**: Preserve document layout and relationships
- **OCR Capabilities**: Extract text from images
- **Enhanced Context**: Better understanding of complex documents

## Technical Components

### 1. NVIDIA NV-Ingest Architecture
```yaml
Core Services:
  - nv-ingest-ms-runtime: Main orchestration service
  - nemo-retriever-embedding-ms: Document embeddings
  - nv-yolox-ms: Object detection (tables/charts)
  - paddleocr-ms: Optical character recognition
  - deplot-ms: Chart data extraction
  - cached-whisper-ms: Audio transcription (optional)

Resource Requirements:
  - Base overhead: 2-3GB VRAM
  - Per-model loading: 1-4GB each
  - Total for full suite: 10-15GB VRAM
```

### 2. Document Processing Models

| Model | Purpose | VRAM | Load Time |
|-------|---------|------|-----------|
| YOLOX | Table/chart detection | 1-2GB | 5-7s |
| PaddleOCR | Text from images | 2-3GB | 8-10s |
| DePlot | Chart data extraction | 2-4GB | 5-8s |
| C-RADIO | Visual features | 2-3GB | 6-8s |

## Exploration Phases

### Phase 1: Research & Feasibility (Week 1)
**Goal**: Understand NV-Ingest capabilities and requirements

1. **Documentation Review**
   - [ ] Study NV-Ingest architecture docs
   - [ ] Review API specifications
   - [ ] Understand model loading strategies
   - [ ] Check version compatibility

2. **Environment Setup**
   - [ ] Pull NV-Ingest Docker images
   - [ ] Configure docker-compose for services
   - [ ] Test basic connectivity
   - [ ] Verify GPU access from containers

3. **Simple Proof of Concept**
   - [ ] Process a PDF with tables
   - [ ] Extract structured data
   - [ ] Compare with PyPDF2 output
   - [ ] Measure performance metrics

### Phase 2: Integration Design (Week 2)
**Goal**: Design integration without breaking current system

1. **Hybrid Approach Design**
   - [ ] Keep PyPDF2 as fallback
   - [ ] Add NV-Ingest as optional enhancement
   - [ ] Design switching mechanism
   - [ ] Plan gradual rollout

2. **API Integration**
   - [ ] Create NVIngestService class
   - [ ] Implement document type detection
   - [ ] Add structured data models
   - [ ] Design caching strategy

3. **Resource Management**
   - [ ] Implement dynamic model loading
   - [ ] Add VRAM monitoring
   - [ ] Create model unloading logic
   - [ ] Set resource limits

### Phase 3: Prototype Implementation (Week 3)
**Goal**: Build working prototype with key features

1. **Core Features**
   - [ ] PDF table extraction
   - [ ] Chart data extraction
   - [ ] Image text extraction
   - [ ] Layout preservation

2. **Integration Points**
   - [ ] Modify document processor
   - [ ] Enhance chunk creation
   - [ ] Update vector storage
   - [ ] Extend metadata model

3. **Testing Suite**
   - [ ] Create test documents
   - [ ] Benchmark performance
   - [ ] Compare quality metrics
   - [ ] Stress test resources

### Phase 4: Evaluation & Decision (Week 4)
**Goal**: Decide on production implementation

1. **Performance Analysis**
   - [ ] Processing speed comparison
   - [ ] Resource usage patterns
   - [ ] Quality improvements
   - [ ] Cost-benefit analysis

2. **Production Planning**
   - [ ] Migration strategy
   - [ ] Rollback procedures
   - [ ] Monitoring setup
   - [ ] Documentation updates

## Key Technical Challenges

### 1. Docker Networking
- NV-Ingest uses multiple microservices
- Complex inter-service communication
- Need to integrate with existing services

### 2. Resource Management
- 24GB VRAM total (RTX 4090)
- Must share with LLM models
- Dynamic loading/unloading critical

### 3. Data Format Compatibility
- NV-Ingest outputs structured JSON
- Need to convert to our chunk format
- Preserve visual element relationships

### 4. Performance Optimization
- Batch processing for efficiency
- Caching extracted features
- Async processing pipeline

## Success Metrics

1. **Functional Success**
   - Extract 90%+ of tables correctly
   - Preserve document structure
   - Handle mixed content types
   - Maintain text extraction quality

2. **Performance Targets**
   - < 30s for average PDF processing
   - < 15GB peak VRAM usage
   - Graceful degradation without GPU
   - No impact on chat response time

3. **Quality Improvements**
   - Better context from visual elements
   - More accurate document chunking
   - Enhanced search relevance
   - Richer metadata extraction

## Implementation Code Structure

```python
# backend/app/services/nv_ingest_service.py
class NVIngestService:
    async def process_document(self, file_path: str, doc_type: str):
        # Detect required models
        models_needed = self._determine_models(doc_type)
        
        # Load models dynamically
        await self._ensure_models_loaded(models_needed)
        
        # Process document
        result = await self._call_nv_ingest(file_path)
        
        # Convert to our format
        return self._convert_to_chunks(result)

# backend/app/document_processing/multimodal_processor.py  
class MultimodalProcessor:
    def __init__(self):
        self.nv_ingest = NVIngestService()
        self.fallback = SimpleTextExtractor()
    
    async def process(self, doc_path: str):
        if self.should_use_multimodal(doc_path):
            try:
                return await self.nv_ingest.process_document(doc_path)
            except Exception as e:
                logger.warning(f"Multimodal failed, using fallback: {e}")
        
        return self.fallback.extract_text(doc_path)
```

## Next Immediate Steps

1. **Setup Test Environment**
   ```bash
   cd F:\assistant
   mkdir nim-exploration
   cd nim-exploration
   docker pull nvcr.io/nvidia/nemo/nv-ingest:24.08
   ```

2. **Create Test Script**
   ```python
   # test_nv_ingest_basic.py
   import requests
   import json
   
   def test_pdf_extraction():
       # Upload test PDF with tables
       # Call NV-Ingest API
       # Analyze output structure
       pass
   ```

3. **Document Findings**
   - Create `nim-exploration/findings.md`
   - Record VRAM usage
   - Note processing times
   - Capture output samples

## Decision Framework

### Go with NIM Multimodal if:
- Visual element extraction significantly improves search
- VRAM usage stays under 15GB with model switching
- Processing time acceptable (< 30s average)
- Clear ROI on implementation effort

### Stay with Current Approach if:
- Text extraction sufficient for use cases
- VRAM constraints too tight
- Complexity outweighs benefits
- Performance impact too high

## Resources & References

1. **NVIDIA Documentation**
   - [NV-Ingest Overview](https://docs.nvidia.com/nemo/nv-ingest/)
   - [API Reference](https://docs.nvidia.com/nemo/nv-ingest/api/)
   - [Model Specifications](https://docs.nvidia.com/nemo/nv-ingest/models/)

2. **Community Examples**
   - GitHub: NVIDIA/nv-ingest
   - Docker Hub: nvcr.io/nvidia/nemo/nv-ingest

3. **Our Test Documents**
   - `/tests/documents/sample_with_tables.pdf`
   - `/tests/documents/financial_charts.pdf`
   - `/tests/documents/mixed_content.pdf`