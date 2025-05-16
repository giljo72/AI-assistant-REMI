import api from './api';
import projectService from './projectService';
import userPromptService from './userPromptService';
import fileService from './fileService';

export {
  api,
  projectService,
  userPromptService,
  fileService,
};

export type { Project, CreateProjectRequest, UpdateProjectRequest } from './projectService';
export type { UserPrompt, CreateUserPromptRequest, UpdateUserPromptRequest } from './userPromptService';
export type { 
  File, 
  FileWithMetadata,
  FileUploadRequest, 
  FileProcessRequest, 
  FileSearchRequest,
  FileSearchResult,
  FileFilterOptions,
  FileSortOptions,
  FileLinkRequest,
  FileUpdateRequest,
  FileBulkOperationResult,
  ProcessingStats
} from './fileService';