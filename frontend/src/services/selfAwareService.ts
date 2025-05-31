import { apiRequest } from './api';

export interface ActionRequest {
  id: string;
  type: 'command' | 'file_write';
  details: any;
  status: string;
  created_at: string;
}

export interface AuthResponse {
  success: boolean;
  token: string;
  expires_at: string;
}

class SelfAwareService {
  private ws: WebSocket | null = null;
  private actionCallbacks: Map<string, (action: ActionRequest) => void> = new Map();
  private token: string | null = null;

  // Authenticate for self-aware mode
  async authenticate(password: string): Promise<AuthResponse> {
    const response = await apiRequest<AuthResponse>('/self-aware/authenticate', {
      method: 'POST',
      body: JSON.stringify({ password }),
    });
    
    if (response.success) {
      this.token = response.token;
      localStorage.setItem('selfAwareToken', response.token);
      localStorage.setItem('selfAwareExpires', response.expires_at);
      // Connect WebSocket after a short delay to ensure auth is propagated
      setTimeout(() => this.connectWebSocket(), 100);
    }
    
    return response;
  }

  // Check if we have a valid token
  isAuthenticated(): boolean {
    const token = localStorage.getItem('selfAwareToken');
    const expires = localStorage.getItem('selfAwareExpires');
    
    if (!token || !expires) return false;
    
    const expiryDate = new Date(expires);
    const now = new Date();
    
    if (now >= expiryDate) {
      this.logout();
      return false;
    }
    
    this.token = token;
    return true;
  }

  // Get the authentication token
  getToken(): string | null {
    return this.token || localStorage.getItem('selfAwareToken');
  }

  // Logout and clear session
  logout() {
    if (this.token) {
      apiRequest('/self-aware/logout', {
        method: 'POST',
        body: JSON.stringify({ token: this.token }),
      });
    }
    
    this.token = null;
    localStorage.removeItem('selfAwareToken');
    localStorage.removeItem('selfAwareExpires');
    this.disconnectWebSocket();
  }

  // Connect to WebSocket for real-time approval notifications
  connectWebSocket() {
    if (this.ws) return;
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/approvals/ws`;
    
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onopen = () => {
      console.log('Connected to approval WebSocket');
    };
    
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'action_request' && data.action) {
          // Notify all registered callbacks
          this.actionCallbacks.forEach(callback => callback(data.action));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.ws.onclose = () => {
      console.log('Disconnected from approval WebSocket');
      this.ws = null;
      
      // Don't auto-reconnect - let the component manage connection lifecycle
    };
  }

  // Disconnect WebSocket
  private disconnectWebSocket() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  // Register a callback for action requests
  onActionRequest(callback: (action: ActionRequest) => void): () => void {
    const id = Math.random().toString(36).substr(2, 9);
    this.actionCallbacks.set(id, callback);
    
    // Return unsubscribe function
    return () => {
      this.actionCallbacks.delete(id);
    };
  }

  // Approve or deny an action
  async approveAction(actionId: string, approved: boolean): Promise<void> {
    await apiRequest(`/approvals/approve/${actionId}`, {
      method: 'POST',
      body: JSON.stringify({ action_id: actionId, approved }),
    });
  }

  // Get pending actions
  async getPendingActions(): Promise<ActionRequest[]> {
    return await apiRequest<ActionRequest[]>('/approvals/pending-actions');
  }

  // Get action history
  async getActionHistory(limit: number = 50): Promise<ActionRequest[]> {
    return await apiRequest<ActionRequest[]>(`/approvals/action-history?limit=${limit}`);
  }

  // Execute a file write operation (requires approval)
  async writeFile(filepath: string, content: string, reason: string): Promise<any> {
    const token = this.getToken();
    if (!token) throw new Error('Not authenticated');
    
    return await apiRequest('/self-aware-ops/write-file', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ filepath, content, reason }),
    });
  }

  // Execute a command (requires approval)
  async executeCommand(command: string[], workingDirectory: string | null, reason: string): Promise<any> {
    const token = this.getToken();
    if (!token) throw new Error('Not authenticated');
    
    return await apiRequest('/self-aware-ops/execute-command', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ 
        command, 
        working_directory: workingDirectory,
        reason 
      }),
    });
  }

  // Read a file (no approval needed)
  async readFile(filepath: string): Promise<{ content: string }> {
    const token = this.getToken();
    if (!token) throw new Error('Not authenticated');
    
    return await apiRequest('/self-aware-ops/read-file', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ filepath }),
    });
  }
}

// Export singleton instance
export const selfAwareService = new SelfAwareService();