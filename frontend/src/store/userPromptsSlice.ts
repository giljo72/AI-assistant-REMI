import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { v4 as uuidv4 } from 'uuid';

interface UserPrompt {
  id: string;
  name: string;
  content: string;
  description?: string;
  is_active: boolean;
  project_id?: string | null;
  created_at?: string;
  updated_at?: string;
}

interface UserPromptsState {
  prompts: UserPrompt[];
  activePromptId: string | null;
  loading: boolean;
  error: string | null;
}

const initialState: UserPromptsState = {
  prompts: [],
  activePromptId: null,
  loading: false,
  error: null
};

export const userPromptsSlice = createSlice({
  name: 'userPrompts',
  initialState,
  reducers: {
    setPrompts: (state, action: PayloadAction<UserPrompt[]>) => {
      state.prompts = action.payload;
      // Find the active prompt
      const activePrompt = action.payload.find(p => p.is_active);
      state.activePromptId = activePrompt?.id || null;
    },
    
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    addPrompt: (state, action: PayloadAction<Omit<UserPrompt, 'id'>>) => {
      const id = uuidv4();
      const newPrompt = {
        id,
        ...action.payload
      };
      
      state.prompts.push(newPrompt);
      
      // If this prompt is set to active, update activePromptId
      if (newPrompt.is_active) {
        // Deactivate any currently active prompt
        state.prompts.forEach(prompt => {
          if (prompt.id !== id && prompt.is_active) {
            prompt.is_active = false;
          }
        });
        
        state.activePromptId = id;
      }
    },
    
    updatePrompt: (state, action: PayloadAction<UserPrompt>) => {
      const index = state.prompts.findIndex(p => p.id === action.payload.id);
      if (index !== -1) {
        state.prompts[index] = action.payload;
        
        // Update active prompt status
        if (action.payload.is_active) {
          // Deactivate other prompts
          state.prompts.forEach(prompt => {
            if (prompt.id !== action.payload.id && prompt.is_active) {
              prompt.is_active = false;
            }
          });
          
          state.activePromptId = action.payload.id;
        } else if (state.activePromptId === action.payload.id) {
          // This prompt was active but is no longer active
          state.activePromptId = null;
        }
      }
    },
    
    deletePrompt: (state, action: PayloadAction<string>) => {
      const id = action.payload;
      
      // Check if we're deleting the active prompt
      if (state.activePromptId === id) {
        state.activePromptId = null;
      }
      
      state.prompts = state.prompts.filter(prompt => prompt.id !== id);
    },
    
    activatePrompt: (state, action: PayloadAction<string>) => {
      const id = action.payload;
      
      // Deactivate all prompts first
      state.prompts.forEach(prompt => {
        prompt.is_active = (prompt.id === id);
      });
      
      state.activePromptId = id;
    },
    
    deactivatePrompt: (state, action: PayloadAction<string>) => {
      const id = action.payload;
      
      const prompt = state.prompts.find(p => p.id === id);
      if (prompt) {
        prompt.is_active = false;
      }
      
      if (state.activePromptId === id) {
        state.activePromptId = null;
      }
    },
    
    deactivateAllPrompts: (state) => {
      state.prompts.forEach(prompt => {
        prompt.is_active = false;
      });
      
      state.activePromptId = null;
    }
  }
});

export const {
  setPrompts,
  setLoading,
  setError,
  addPrompt,
  updatePrompt,
  deletePrompt,
  activatePrompt,
  deactivatePrompt,
  deactivateAllPrompts
} = userPromptsSlice.actions;

export default userPromptsSlice.reducer;