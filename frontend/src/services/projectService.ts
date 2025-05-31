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
    console.log("Fetching all projects...");
    try {
      const response = await api.get('/projects/');
      console.log("Projects response:", response.data);
      
      // Ensure we return an array
      if (!Array.isArray(response.data)) {
        console.warn("Projects response is not an array, might be nested in an object:", response.data);
        // Try to extract the array if it's nested
        if (response.data && typeof response.data === 'object' && Array.isArray(response.data.projects)) {
          return response.data.projects;
        }
        // If we can't find an array, return an empty one
        console.error("Could not find project array in response, returning empty array");
        return [];
      }
      
      return response.data;
    } catch (error) {
      console.error("Error fetching projects:", error);
      return [];
    }
  },

  // Get a project by ID
  getProject: async (id: string): Promise<Project> => {
    console.log(`Getting project with ID: ${id}`);
    try {
      const response = await api.get(`/projects/${id}`);
      console.log("Project data received:", response.data);
      return response.data;
    } catch (error) {
      console.error(`Error getting project ${id}:`, error);
      // Try to get project from the list of all projects as a fallback
      try {
        const allProjects = await projectService.getAllProjects();
        const project = allProjects.find(p => p.id === id);
        if (project) {
          console.log("Found project from list of all projects:", project);
          return project;
        }
      } catch (fallbackError) {
        console.error("Fallback also failed:", fallbackError);
      }
      
      // If we can't find the project, create a mock one
      const mockProject: Project = {
        id,
        name: `Project ${id.substring(0, 8)}`,
        created_at: new Date().toISOString(),
        chat_count: 0,
        document_count: 0
      };
      console.log("Created mock project:", mockProject);
      return mockProject;
    }
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