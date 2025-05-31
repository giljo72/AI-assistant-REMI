import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { systemPromptService, SystemPrompt } from '../services/systemPromptService';

interface SystemPromptsState {
  prompts: SystemPrompt[];
  activePrompt: SystemPrompt | null;
  loading: boolean;
  error: string | null;
}

const initialState: SystemPromptsState = {
  prompts: [],
  activePrompt: null,
  loading: false,
  error: null,
};

// Async thunks
export const fetchSystemPrompts = createAsyncThunk(
  'systemPrompts/fetchAll',
  async (category?: string) => {
    const prompts = await systemPromptService.getAllSystemPrompts(category);
    return prompts;
  }
);

export const fetchActiveSystemPrompt = createAsyncThunk(
  'systemPrompts/fetchActive',
  async () => {
    const prompt = await systemPromptService.getActiveSystemPrompt();
    return prompt;
  }
);

export const activateSystemPrompt = createAsyncThunk(
  'systemPrompts/activate',
  async (promptId: string) => {
    const prompt = await systemPromptService.activateSystemPrompt(promptId);
    return prompt;
  }
);

export const createSystemPrompt = createAsyncThunk(
  'systemPrompts/create',
  async (data: { name: string; content: string; description?: string; category?: string }) => {
    const prompt = await systemPromptService.createSystemPrompt(data);
    return prompt;
  }
);

export const updateSystemPrompt = createAsyncThunk(
  'systemPrompts/update',
  async ({ id, data }: { id: string; data: { name?: string; content?: string; description?: string; category?: string } }) => {
    const prompt = await systemPromptService.updateSystemPrompt(id, data);
    return prompt;
  }
);

export const deleteSystemPrompt = createAsyncThunk(
  'systemPrompts/delete',
  async (id: string) => {
    await systemPromptService.deleteSystemPrompt(id);
    return id;
  }
);

export const seedDefaultSystemPrompts = createAsyncThunk(
  'systemPrompts/seedDefaults',
  async () => {
    const prompts = await systemPromptService.seedDefaultPrompts();
    return prompts;
  }
);

const systemPromptsSlice = createSlice({
  name: 'systemPrompts',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setActiveSystemPrompt: (state, action: PayloadAction<string | null>) => {
      if (action.payload === null) {
        // Disable system prompt
        state.activePrompt = null;
        state.prompts = state.prompts.map(p => ({ ...p, is_active: false }));
      } else {
        // Find and activate the selected prompt
        const prompt = state.prompts.find(p => p.id === action.payload);
        if (prompt) {
          state.prompts = state.prompts.map(p => ({ 
            ...p, 
            is_active: p.id === action.payload 
          }));
          state.activePrompt = { ...prompt, is_active: true };
        }
      }
    },
  },
  extraReducers: (builder) => {
    // Fetch all prompts
    builder
      .addCase(fetchSystemPrompts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSystemPrompts.fulfilled, (state, action) => {
        state.loading = false;
        state.prompts = action.payload;
        // Update active prompt if it's in the list
        const activePrompt = action.payload.find(p => p.is_active);
        if (activePrompt) {
          state.activePrompt = activePrompt;
        }
      })
      .addCase(fetchSystemPrompts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch system prompts';
      });

    // Fetch active prompt
    builder
      .addCase(fetchActiveSystemPrompt.fulfilled, (state, action) => {
        state.activePrompt = action.payload;
      });

    // Activate prompt
    builder
      .addCase(activateSystemPrompt.fulfilled, (state, action) => {
        // Deactivate all prompts
        state.prompts = state.prompts.map(p => ({ ...p, is_active: false }));
        // Activate the selected prompt
        const index = state.prompts.findIndex(p => p.id === action.payload.id);
        if (index !== -1) {
          state.prompts[index] = action.payload;
        }
        state.activePrompt = action.payload;
      });

    // Create prompt
    builder
      .addCase(createSystemPrompt.fulfilled, (state, action) => {
        state.prompts.push(action.payload);
      });

    // Update prompt
    builder
      .addCase(updateSystemPrompt.fulfilled, (state, action) => {
        const index = state.prompts.findIndex(p => p.id === action.payload.id);
        if (index !== -1) {
          state.prompts[index] = action.payload;
        }
        if (state.activePrompt?.id === action.payload.id) {
          state.activePrompt = action.payload;
        }
      });

    // Delete prompt
    builder
      .addCase(deleteSystemPrompt.fulfilled, (state, action) => {
        state.prompts = state.prompts.filter(p => p.id !== action.payload);
      });

    // Seed defaults
    builder
      .addCase(seedDefaultSystemPrompts.fulfilled, (state, action) => {
        // Add new prompts that don't exist
        const existingIds = new Set(state.prompts.map(p => p.id));
        const newPrompts = action.payload.filter(p => !existingIds.has(p.id));
        state.prompts.push(...newPrompts);
        
        // Update active prompt if one was activated
        const activePrompt = action.payload.find(p => p.is_active);
        if (activePrompt) {
          state.activePrompt = activePrompt;
        }
      });
  },
});

export const { clearError, setActiveSystemPrompt } = systemPromptsSlice.actions;
export default systemPromptsSlice.reducer;