# Technical Debt TODO List

## Priority Matrix
- 🔴 **Critical**: Blocking issues or security concerns
- 🟡 **High**: Impacts user experience or developer productivity  
- 🟢 **Medium**: Nice to have, improves quality
- ⚪ **Low**: Cosmetic or minor improvements

## 1. Code Cleanup Tasks

### 🔴 Critical - Immediate Action Required
- [ ] Delete all .bak files (use git for version control)
  - `backend/app/db/init_db.py.bak`
  - `frontend/src/components/file/MainFileManager.tsx.bak`
- [ ] Delete empty/unknown files
  - `frontend/src/components/chat/nul`
- [ ] Investigate and resolve "cleaned" files mystery
  - `backend/app/api/cleaned_api.py`
  - `backend/app/cleaned_main.py`
  - `backend/app/api/endpoints/cleaned_files.py`
  - WHY do these exist? Are they duplicates?

### 🟡 High Priority - This Week
- [ ] Archive one-time setup scripts to `/scripts/archive/`
  - `setup_nim.py`
  - `install_pdf_libs.py`
  - `install_all_models.bat`
  - `install_models.bat`
  - `install_required_models.bat`
  - `setup_llama_70b_nim.bat`
- [ ] Consolidate test scripts to `/tests/` directory
  - Move `test_*.py` from root
  - Create proper test structure
- [ ] Remove or properly integrate mock services
  - Review `frontend/src/services/fileService.mock.ts`
  - Decide on `backend/app/core/mock_nemo/` usage
- [ ] Clean up duplicate LLM implementations
  - Verify which are active: nemo_llm.py vs transformers_llm.py
  - Remove unused implementations

### 🟢 Medium Priority - This Month
- [ ] Review and remove unused endpoints
  - Check if `test_endpoints.py` is needed
  - Remove development-only routes
- [ ] Consolidate model configuration
  - Too many model config files
  - Create single source of truth
- [ ] Clean up logging
  - Standardize log formats
  - Remove debug prints
- [ ] Remove commented code blocks
  - Search for large commented sections
  - Delete or document why they exist

### ⚪ Low Priority - When Time Permits
- [ ] Standardize file naming conventions
- [ ] Add file headers with purpose/author
- [ ] Remove unused imports
- [ ] Format all code with black/prettier

## 2. Missing Functionality

### 🔴 Critical - Core Features Incomplete
- [ ] **Context Controls Backend**
  - Frontend shows controls but backend ignores them
  - Need to implement context filtering in LLM service
  - Pass context settings through API calls
  - Estimated: 2-3 days

### 🟡 High Priority - User Experience
- [ ] **Personal Profiles Integration**
  - Database tables exist but not used in chat
  - Need to inject profile data into context
  - Estimated: 1 day
- [ ] **Error Handling**
  - Many try/except blocks just print errors
  - Need proper error propagation to UI
  - Add user-friendly error messages
- [ ] **Loading States**
  - Missing loading indicators for long operations
  - Document processing needs progress bar
  - Model switching needs feedback

### 🟢 Medium Priority - Quality of Life
- [ ] **Batch Document Upload**
  - Currently one at a time
  - Need multi-file selection
- [ ] **Document Preview**
  - Can only download, not preview
  - Add in-app document viewer
- [ ] **Chat Export**
  - No way to export conversations
  - Add markdown/PDF export
- [ ] **Keyboard Shortcuts**
  - No shortcuts for common actions
  - Add customizable keybindings

## 3. Performance Optimizations

### 🟡 High Priority - Noticeable Impact
- [ ] **Database Query Optimization**
  - Missing indexes on foreign keys
  - N+1 queries in chat history
  - No query result caching
- [ ] **Frontend Bundle Size**
  - 5MB+ JavaScript bundle
  - Need code splitting
  - Lazy load heavy components
- [ ] **Embedding Generation**
  - Sequential processing is slow
  - Implement batch embeddings
  - Add progress tracking

### 🟢 Medium Priority - Future Scaling
- [ ] **Redis Caching Layer**
  - Cache embeddings
  - Cache model responses
  - Session management
- [ ] **WebSocket for Real-time**
  - Currently polling for updates
  - Switch to WebSocket for chat
  - Reduce server load
- [ ] **Background Job Queue**
  - Document processing blocks API
  - Need Celery or similar
  - Async processing pipeline

## 4. Testing & Quality

### 🔴 Critical - No Test Coverage
- [ ] **Unit Tests - Backend**
  - 0% coverage currently
  - Critical paths need tests
  - Database operations
  - LLM service logic
- [ ] **Unit Tests - Frontend**
  - No component tests
  - No Redux tests
  - No service tests

### 🟡 High Priority - Reliability
- [ ] **Integration Tests**
  - API endpoint testing
  - Database transaction tests
  - Model switching tests
- [ ] **E2E Tests**
  - Critical user journeys
  - Document upload flow
  - Chat conversation flow
- [ ] **Performance Tests**
  - Load testing with Locust
  - Memory leak detection
  - VRAM usage monitoring

## 5. Security Improvements

### 🟡 High Priority - Data Protection
- [ ] **Input Validation**
  - Missing validation on many endpoints
  - SQL injection possibilities
  - Path traversal in file operations
- [ ] **Authentication System**
  - Currently no auth at all
  - Need at least basic auth
  - API key management
- [ ] **Secrets Management**
  - API keys in plain text
  - Need proper secret storage
  - Environment variable validation

### 🟢 Medium Priority - Defense in Depth
- [ ] **Rate Limiting**
  - No limits on API calls
  - Could exhaust resources
- [ ] **Audit Logging**
  - No record of actions
  - Need compliance trail
- [ ] **Encrypted Storage**
  - Documents stored plain
  - Consider encryption at rest

## 6. Documentation Gaps

### 🟡 High Priority - Developer Experience
- [ ] **API Documentation**
  - Many endpoints undocumented
  - Missing request/response examples
  - No Swagger/OpenAPI spec
- [ ] **Setup Guide**
  - Windows-specific issues
  - Troubleshooting guide
  - Common problems FAQ
- [ ] **Architecture Diagrams**
  - Data flow diagrams
  - Component interactions
  - Deployment architecture

### 🟢 Medium Priority - Maintenance
- [ ] **Code Comments**
  - Complex logic undocumented
  - Missing docstrings
  - Unclear variable names
- [ ] **Configuration Guide**
  - All config options
  - Performance tuning
  - Model selection criteria

## 7. Infrastructure & DevOps

### 🟡 High Priority - Production Readiness
- [ ] **Production Build Pipeline**
  - No CI/CD setup
  - Manual deployment only
  - No automated builds
- [ ] **Monitoring & Alerting**
  - No production monitoring
  - No error tracking (Sentry)
  - No performance monitoring
- [ ] **Backup & Recovery**
  - No automated backups
  - No disaster recovery plan
  - No data migration tools

### 🟢 Medium Priority - Scalability
- [ ] **Container Orchestration**
  - Better Docker Compose setup
  - Consider Kubernetes
  - Health checks needed
- [ ] **Configuration Management**
  - Hardcoded values everywhere
  - Need central config
  - Environment-specific settings

## 8. NIM Multimodal Integration

### 🟡 High Priority - Advanced Features
- [ ] **NV-Ingest Evaluation**
  - Test multimodal extraction
  - Benchmark performance
  - Document VRAM requirements
  - Create integration POC
- [ ] **Fallback Strategy**
  - Graceful degradation
  - Feature detection
  - User notifications
- [ ] **Performance Impact**
  - Measure processing time
  - Monitor VRAM usage
  - Optimize model loading

## Completed Tasks ✅

### May 27, 2025
- [x] **Enhanced Backend Console Logging**
  - Added timestamps to all requests
  - Human-readable action names
  - Color-coded status indicators
  - Integrated into run_server.py
  - Resource endpoint filtering

### May 26, 2025
- [x] **Document Text Extraction**
  - Implemented PyPDF2 for PDFs
  - Added python-docx for Word docs
  - Integrated pandas for spreadsheets
  - Removed placeholder text

## Execution Plan

### Week 1 (Immediate)
1. Clean up .bak files and empty files
2. Fix context controls backend
3. Start backend unit tests
4. Investigate "cleaned" files

### Week 2-3 (High Priority)
1. Archive old scripts
2. Implement personal profiles
3. Add error handling
4. Begin NIM multimodal evaluation

### Month 2 (Medium Priority)
1. Performance optimizations
2. Security improvements
3. Testing infrastructure
4. Documentation updates

### Month 3 (Lower Priority)
1. Infrastructure improvements
2. Advanced features
3. Polish and refinement
4. Production preparation

## Success Metrics
- [ ] 50%+ test coverage
- [ ] All critical bugs fixed
- [ ] < 3s page load time
- [ ] Zero security vulnerabilities
- [ ] Complete API documentation
- [ ] Automated deployment pipeline

This TODO list should be reviewed weekly and updated as items are completed or priorities change.