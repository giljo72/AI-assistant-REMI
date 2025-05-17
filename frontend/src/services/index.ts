import api from './api';
import projectService from './projectService';
import userPromptService from './userPromptService';
import fileService from './fileService';
import { chatService } from './chatService';

export {
  api,
  projectService,
  userPromptService,
  fileService,
  chatService,
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
export type { Chat, ChatMessage, ChatCreate, ChatUpdate, ChatMessageCreate } from './chatService';