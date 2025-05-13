import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { v4 as uuidv4 } from 'uuid';
import { UserPrompt } from '../components/UserPromptManager';

interface UserPromptsState {
  prompts: UserPrompt[];
  activePromptId: string | null;
}

const initialState: UserPromptsState = {
  prompts: [],
  activePromptId: null
};

export const userPromptsSlice = createSlice({
  name: 'userPrompts',
  initialState,
  reducers: {
    addPrompt: (state, action: PayloadAction<Omit<UserPrompt, 'id'>>) => {
      const id = uuidv4();
      const newPrompt = {
        id,
        ...action.payload
      };
      
      state.prompts.push(newPrompt);
      
      // If this prompt is set to active, update activePromptId
      if (newPrompt.active) {
        // Deactivate any currently active prompt
        state.prompts.forEach(prompt => {
          if (prompt.id !== id && prompt.active) {
            prompt.active = false;
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
        if (action.payload.active) {
          // Deactivate other prompts
          state.prompts.forEach(prompt => {
            if (prompt.id !== action.payload.id && prompt.active) {
              prompt.active = false;
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
        prompt.active = (prompt.id === id);
      });
      
      state.activePromptId = id;
    },
    
    deactivatePrompt: (state, action: PayloadAction<string>) => {
      const id = action.payload;
      
      const prompt = state.prompts.find(p => p.id === id);
      if (prompt) {
        prompt.active = false;
      }
      
      if (state.activePromptId === id) {
        state.activePromptId = null;
      }
    },
    
    deactivateAllPrompts: (state) => {
      state.prompts.forEach(prompt => {
        prompt.active = false;
      });
      
      state.activePromptId = null;
    }
  }
});

export const {
  addPrompt,
  updatePrompt,
  deletePrompt,
  activatePrompt,
  deactivatePrompt,
  deactivateAllPrompts
} = userPromptsSlice.actions;

export default userPromptsSlice.reducer;