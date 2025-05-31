import axios from 'axios';
import { API_BASE_URL } from './api';

export interface SystemPrompt {
  id: string;
  name: string;
  content: string;
  description?: string;
  category?: string;
  is_active: boolean;
  is_default: boolean;
  created_at: string;
  updated_at?: string;
}

export interface CreateSystemPromptData {
  name: string;
  content: string;
  description?: string;
  category?: string;
}

export interface UpdateSystemPromptData {
  name?: string;
  content?: string;
  description?: string;
  category?: string;
}

class SystemPromptService {
  private baseUrl = `${API_BASE_URL}/system-prompts`;

  async getAllSystemPrompts(category?: string): Promise<SystemPrompt[]> {
    try {
      const params = category ? { category } : {};
      const response = await axios.get(this.baseUrl, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching system prompts:', error);
      throw error;
    }
  }

  async getActiveSystemPrompt(): Promise<SystemPrompt | null> {
    try {
      const response = await axios.get(`${this.baseUrl}/active`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      console.error('Error fetching active system prompt:', error);
      throw error;
    }
  }

  async getSystemPrompt(id: string): Promise<SystemPrompt> {
    try {
      const response = await axios.get(`${this.baseUrl}/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching system prompt:', error);
      throw error;
    }
  }

  async createSystemPrompt(data: CreateSystemPromptData): Promise<SystemPrompt> {
    try {
      const response = await axios.post(this.baseUrl, data);
      return response.data;
    } catch (error) {
      console.error('Error creating system prompt:', error);
      throw error;
    }
  }

  async updateSystemPrompt(id: string, data: UpdateSystemPromptData): Promise<SystemPrompt> {
    try {
      const response = await axios.put(`${this.baseUrl}/${id}`, data);
      return response.data;
    } catch (error) {
      console.error('Error updating system prompt:', error);
      throw error;
    }
  }

  async deleteSystemPrompt(id: string): Promise<void> {
    try {
      await axios.delete(`${this.baseUrl}/${id}`);
    } catch (error) {
      console.error('Error deleting system prompt:', error);
      throw error;
    }
  }

  async activateSystemPrompt(id: string): Promise<SystemPrompt> {
    try {
      const response = await axios.post(`${this.baseUrl}/activate/${id}`);
      return response.data;
    } catch (error) {
      console.error('Error activating system prompt:', error);
      throw error;
    }
  }

  async deactivateAllSystemPrompts(): Promise<void> {
    try {
      await axios.post(`${this.baseUrl}/deactivate`);
    } catch (error) {
      console.error('Error deactivating system prompts:', error);
      throw error;
    }
  }

  async seedDefaultPrompts(): Promise<SystemPrompt[]> {
    try {
      const response = await axios.post(`${this.baseUrl}/seed-defaults`);
      return response.data;
    } catch (error) {
      console.error('Error seeding default prompts:', error);
      throw error;
    }
  }
}

export const systemPromptService = new SystemPromptService();