import api from './api';

export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at?: string;
  chat_count: number;
  document_count: number;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
}

const projectService = {
  // Get all projects
  getAllProjects: async (): Promise<Project[]> => {
    const response = await api.get('/projects');
    return response.data;
  },

  // Get a project by ID
  getProject: async (id: string): Promise<Project> => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },

  // Create a new project
  createProject: async (project: CreateProjectRequest): Promise<Project> => {
    const response = await api.post('/projects', project);
    return response.data;
  },

  // Update a project
  updateProject: async (id: string, project: UpdateProjectRequest): Promise<Project> => {
    const response = await api.put(`/projects/${id}`, project);
    return response.data;
  },

  // Delete a project
  deleteProject: async (id: string): Promise<Project> => {
    const response = await api.delete(`/projects/${id}`);
    return response.data;
  },
};

export default projectService;