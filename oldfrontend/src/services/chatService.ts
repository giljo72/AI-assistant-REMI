import api from './api';

export interface ChatMessage {
  id: string;
  content: string;
  is_user: boolean;
  chat_id: string;
  created_at: string;
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
  is_user: boolean;
  chat_id: string;
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
      // Generate a client-side chat object for fallback
      return {
        id: Date.now().toString(),
        name: chat.name,
        project_id: chat.project_id,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        messages: []
      };
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
    return api.get<ChatMessage[]>(`/chats/${chatId}/messages/`);
  }

  /**
   * Create a new message
   */
  async createMessage(message: ChatMessageCreate): Promise<ChatMessage> {
    return api.post<ChatMessage>('/chats/messages/', message);
  }

  /**
   * Send a user message and get the assistant's response
   * This is a convenience method that creates a user message and then gets the response
   */
  async sendMessage(chatId: string, content: string): Promise<ChatMessage[]> {
    // Create the user message
    await this.createMessage({
      chat_id: chatId,
      content,
      is_user: true
    });
    
    // TODO: In a real app, this would call the LLM backend to generate a response
    // For now, we'll just create a mock assistant message
    const assistantMessage = await this.createMessage({
      chat_id: chatId,
      content: `I received your message: "${content}". This is a mock response.`,
      is_user: false
    });
    
    // Return all messages for the chat
    return this.getChatMessages(chatId);
  }
}

export const chatService = new ChatService();