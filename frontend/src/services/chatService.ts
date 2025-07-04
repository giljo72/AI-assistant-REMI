import api from './api';
import { personalProfileService } from './personalProfileService';

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  chat_id: string;
  created_at: string;
  model_info?: {
    model_name: string;
    device: string;
    is_initialized: boolean;
    nemo_available: boolean;
    model_type: string;
  };
}

export interface ChatGenerateRequest {
  message: string;
  max_length?: number;
  temperature?: number;
  include_context?: boolean;
  model_name?: string;
  model_type?: string;
  context_mode?: string;
  personal_context?: string;
  // Document context settings
  is_project_documents_enabled?: boolean;
  is_global_data_enabled?: boolean;
  is_user_prompt_enabled?: boolean;
  active_user_prompt_id?: string;
}

export interface ChatGenerateResponse {
  response: string;
  user_message_id: string;
  assistant_message_id: string;
  model_info: {
    model_name: string;
    device: string;
    is_initialized: boolean;
    nemo_available: boolean;
    model_type: string;
  };
}

export interface Chat {
  id: string;
  name: string;
  project_id: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface ChatCreate {
  name: string;
  project_id: string;
}

export interface ChatUpdate {
  name?: string;
}

export interface ChatMessageCreate {
  content: string;
  role: 'user' | 'assistant' | 'system';
  chat_id: string;
}

interface ChatGenerateRequest {
  message: string;
  max_length?: number;
  temperature?: number;
  include_context?: boolean;
  model_name?: string;
  model_type?: string;
  context_mode?: string;
  personal_context?: string;
}

/**
 * Chat service for managing chats and messages
 */
class ChatService {
  /**
   * Get all chats, optionally filtered by project
   */
  async getChats(projectId?: string): Promise<Chat[]> {
    const url = projectId ? `/chats/?project_id=${projectId}` : '/chats/';
    try {
      const response = await api.get(url);
      // Ensure we always return an array, even if the API returns something else
      return Array.isArray(response.data) ? response.data : [];
    } catch (error) {
      console.error("Error fetching chats:", error);
      return [];
    }
  }

  /**
   * Get a single chat by ID
   */
  async getChat(chatId: string): Promise<Chat> {
    try {
      const response = await api.get(`/chats/${chatId}`);
      // Ensure the chat has a messages array
      if (!response.data.messages || !Array.isArray(response.data.messages)) {
        response.data.messages = [];
      }
      
      // Transform is_user to role for each message
      response.data.messages = response.data.messages.map((msg: any) => ({
        ...msg,
        role: msg.is_user ? 'user' : 'assistant'
      }));
      
      return response.data;
    } catch (error) {
      console.error("Error fetching chat:", error);
      // Return an empty chat object if there's an error
      return {
        id: chatId,
        name: "Unknown Chat",
        project_id: "",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        messages: []
      };
    }
  }

  /**
   * Create a new chat
   */
  async createChat(chat: ChatCreate): Promise<Chat> {
    try {
      const response = await api.post('/chats/', chat);
      return {
        ...response.data,
        messages: [] // Ensure messages array exists
      };
    } catch (error) {
      console.error("Error creating chat:", error);
      // Don't create a fallback chat - throw the error instead
      throw error;
    }
  }

  /**
   * Update a chat
   */
  async updateChat(chatId: string, chat: ChatUpdate): Promise<Chat> {
    return api.put<Chat>(`/chats/${chatId}`, chat);
  }

  /**
   * Delete a chat
   */
  async deleteChat(chatId: string): Promise<Chat> {
    return api.delete<Chat>(`/chats/${chatId}`);
  }

  /**
   * Get messages for a chat
   */
  async getChatMessages(chatId: string): Promise<ChatMessage[]> {
    const response = await api.get(`/chats/${chatId}/messages/`);
    // Transform is_user to role for each message
    return response.data.map((msg: any) => ({
      ...msg,
      role: msg.is_user ? 'user' : 'assistant'
    }));
  }

  /**
   * Create a new message
   */
  async createMessage(message: ChatMessageCreate): Promise<ChatMessage> {
    return api.post<ChatMessage>('/chats/messages/', message);
  }

  /**
   * Generate AI response using NeMo LLM
   */
  async generateResponse(chatId: string, request: ChatGenerateRequest): Promise<ChatGenerateResponse> {
    try {
      // Add self-aware token if in self-aware mode
      const headers: any = {};
      if (request.context_mode === 'self-aware') {
        const token = localStorage.getItem('selfAwareToken');
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
      }
      
      const response = await api.post(`/chats/${chatId}/generate`, request, { headers });
      return response.data;
    } catch (error) {
      console.error("Error generating response:", error);
      throw error;
    }
  }

  /**
   * Send a user message and get the assistant's response using unified LLM service
   */
  async sendMessage(chatId: string, content: string, options?: {
    max_length?: number;
    temperature?: number;
    include_context?: boolean;
    model_name?: string;
    model_type?: string;
    context_mode?: string;
  }): Promise<ChatGenerateResponse> {
    try {
      console.log('🚀 ChatService: Sending message with options:', options);
      
      const request: ChatGenerateRequest = {
        message: content,
        max_length: options?.max_length || 4096,  // Increased from 150 to allow full responses
        temperature: options?.temperature || 0.7,
        include_context: options?.include_context !== false, // Default to true
        model_name: options?.model_name,
        model_type: options?.model_type,
        context_mode: options?.context_mode,
        personal_context: await this.getPersonalContext()
      };
      
      console.log('📤 ChatService: Request payload:', request);
      return await this.generateResponse(chatId, request);
    } catch (error) {
      console.error("❌ ChatService: Error sending message:", error);
      // Fallback response for error cases
      return {
        response: "I apologize, but I'm having trouble generating a response right now. Please check the backend connection and try again.",
        user_message_id: "",
        assistant_message_id: "",
        model_info: {
          model_name: "Connection Error",
          device: "unknown",
          is_initialized: false,
          nemo_available: false,
          model_type: "Fallback"
        }
      };
    }
  }

  /**
   * Send a simple message and get response (for backward compatibility)
   */
  async sendSimpleMessage(chatId: string, content: string): Promise<ChatMessage> {
    try {
      const response = await api.post(`/chats/${chatId}/messages/generate?message_content=${encodeURIComponent(content)}`);
      return response.data;
    } catch (error) {
      console.error("Error sending simple message:", error);
      throw error;
    }
  }

  /**
   * Send a message with streaming response
   */
  async sendMessageStream(
    chatId: string, 
    content: string, 
    options?: {
      max_length?: number;
      temperature?: number;
      include_context?: boolean;
      model_name?: string;
      model_type?: string;
      context_mode?: string;
      // Document context settings
      is_project_documents_enabled?: boolean;
      is_global_data_enabled?: boolean;
      is_user_prompt_enabled?: boolean;
      active_user_prompt_id?: string;
      onChunk?: (chunk: string) => void;
      onStart?: (modelInfo: { model: string }) => void;
      onComplete?: (messageIds: { user_message_id: string; assistant_message_id: string }) => void;
      onError?: (error: string) => void;
    }
  ): Promise<void> {
    const request: ChatGenerateRequest = {
      message: content,
      max_length: options?.max_length || 4096,
      temperature: options?.temperature || 0.7,
      include_context: options?.include_context !== false,
      model_name: options?.model_name,
      model_type: options?.model_type,
      context_mode: options?.context_mode,
      personal_context: await this.getPersonalContext(),
      // Document context settings
      is_project_documents_enabled: options?.is_project_documents_enabled ?? true,
      is_global_data_enabled: options?.is_global_data_enabled ?? false,
      is_user_prompt_enabled: options?.is_user_prompt_enabled ?? false,
      active_user_prompt_id: options?.active_user_prompt_id
    };

    // Add self-aware token if in self-aware mode
    const headers: any = {
      'Content-Type': 'application/json',
    };
    if (options?.context_mode === 'self-aware') {
      const token = localStorage.getItem('selfAwareToken');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    
    const response = await fetch(`${api.defaults.baseURL}/chats/${chatId}/generate-stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data.trim()) {
            try {
              const event = JSON.parse(data);
              
              switch (event.type) {
                case 'start':
                  console.log('🚀 Streaming started with model:', event.model);
                  options?.onStart?.(event);
                  break;
                case 'chunk':
                  options?.onChunk?.(event.content);
                  break;
                case 'complete':
                  options?.onComplete?.({
                    user_message_id: event.user_message_id,
                    assistant_message_id: event.assistant_message_id
                  });
                  break;
                case 'error':
                  options?.onError?.(event.message);
                  break;
              }
            } catch (e) {
              console.error('Error parsing SSE event:', e);
            }
          }
        }
      }
    }
  }

  /**
   * Get personal context from the default profile
   */
  private async getPersonalContext(): Promise<string | undefined> {
    try {
      const defaultProfile = await personalProfileService.getDefaultProfile();
      if (defaultProfile) {
        // Use formatProfilesForPrompt with an array containing the single profile
        return personalProfileService.formatProfilesForPrompt([defaultProfile]);
      }
    } catch (error) {
      console.error('Error fetching personal profile:', error);
    }
    return undefined;
  }
}

export const chatService = new ChatService();