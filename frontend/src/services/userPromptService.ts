import api from './api';

export interface UserPrompt {
  id: string;
  name: string;
  content: string;
  project_id?: string;
  created_at: string;
  updated_at?: string;
  is_active: boolean;
}

export interface CreateUserPromptRequest {
  name: string;
  content: string;
  project_id?: string;
}

export interface UpdateUserPromptRequest {
  name?: string;
  content?: string;
  is_active?: boolean;
  project_id?: string;
}

const userPromptService = {
  // Get all user prompts
  getAllUserPrompts: async (): Promise<UserPrompt[]> => {
    const response = await api.get('/user-prompts');
    return response.data;
  },

  // Get user prompts for a project
  getUserPromptsForProject: async (projectId: string): Promise<UserPrompt[]> => {
    const response = await api.get(`/user-prompts?project_id=${projectId}`);
    return response.data;
  },

  // Get a user prompt by ID
  getUserPrompt: async (id: string): Promise<UserPrompt> => {
    const response = await api.get(`/user-prompts/${id}`);
    return response.data;
  },

  // Create a new user prompt
  createUserPrompt: async (userPrompt: CreateUserPromptRequest): Promise<UserPrompt> => {
    const response = await api.post('/user-prompts', userPrompt);
    return response.data;
  },

  // Update a user prompt
  updateUserPrompt: async (id: string, userPrompt: UpdateUserPromptRequest): Promise<UserPrompt> => {
    const response = await api.put(`/user-prompts/${id}`, userPrompt);
    return response.data;
  },

  // Delete a user prompt
  deleteUserPrompt: async (id: string): Promise<UserPrompt> => {
    const response = await api.delete(`/user-prompts/${id}`);
    return response.data;
  },

  // Activate a user prompt
  activateUserPrompt: async (id: string): Promise<UserPrompt> => {
    const response = await api.post(`/user-prompts/${id}/activate`);
    return response.data;
  },
};

export default userPromptService;