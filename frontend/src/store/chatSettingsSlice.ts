import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ChatSettings {
  contextMode: string;
  isSystemPromptEnabled: boolean;
  isUserPromptEnabled: boolean;
  activeUserPromptId: string | null;
  activeUserPromptName: string | null;
  isProjectPromptEnabled: boolean;
  isGlobalDataEnabled: boolean;
  isProjectDocumentsEnabled: boolean;
}

interface ChatSettingsState {
  // Store settings per chat ID
  settingsByChat: Record<string, ChatSettings>;
  // Current chat ID
  currentChatId: string | null;
}

// Default settings for a new chat
const defaultChatSettings: ChatSettings = {
  contextMode: 'standard',
  isSystemPromptEnabled: true,
  isUserPromptEnabled: false,
  activeUserPromptId: null,
  activeUserPromptName: null,
  isProjectPromptEnabled: true,
  isGlobalDataEnabled: true,
  isProjectDocumentsEnabled: true,
};

const initialState: ChatSettingsState = {
  settingsByChat: {},
  currentChatId: null,
};

const chatSettingsSlice = createSlice({
  name: 'chatSettings',
  initialState,
  reducers: {
    // Set current chat
    setCurrentChat: (state, action: PayloadAction<string | null>) => {
      state.currentChatId = action.payload;
      // Initialize settings if chat doesn't exist
      if (action.payload && !state.settingsByChat[action.payload]) {
        state.settingsByChat[action.payload] = { ...defaultChatSettings };
      }
    },
    
    // Update context mode for current chat
    updateContextMode: (state, action: PayloadAction<string>) => {
      if (state.currentChatId) {
        if (!state.settingsByChat[state.currentChatId]) {
          state.settingsByChat[state.currentChatId] = { ...defaultChatSettings };
        }
        state.settingsByChat[state.currentChatId].contextMode = action.payload;
      }
    },
    
    // Toggle system prompt
    toggleSystemPrompt: (state) => {
      if (state.currentChatId) {
        if (!state.settingsByChat[state.currentChatId]) {
          state.settingsByChat[state.currentChatId] = { ...defaultChatSettings };
        }
        state.settingsByChat[state.currentChatId].isSystemPromptEnabled = 
          !state.settingsByChat[state.currentChatId].isSystemPromptEnabled;
      }
    },
    
    // Toggle user prompt
    toggleUserPrompt: (state) => {
      if (state.currentChatId) {
        if (!state.settingsByChat[state.currentChatId]) {
          state.settingsByChat[state.currentChatId] = { ...defaultChatSettings };
        }
        state.settingsByChat[state.currentChatId].isUserPromptEnabled = 
          !state.settingsByChat[state.currentChatId].isUserPromptEnabled;
      }
    },
    
    // Set active user prompt
    setActiveUserPrompt: (state, action: PayloadAction<{ id: string | null; name: string | null }>) => {
      if (state.currentChatId) {
        if (!state.settingsByChat[state.currentChatId]) {
          state.settingsByChat[state.currentChatId] = { ...defaultChatSettings };
        }
        state.settingsByChat[state.currentChatId].activeUserPromptId = action.payload.id;
        state.settingsByChat[state.currentChatId].activeUserPromptName = action.payload.name;
        // Enable user prompt when one is selected
        if (action.payload.id) {
          state.settingsByChat[state.currentChatId].isUserPromptEnabled = true;
        }
      }
    },
    
    // Toggle project prompt
    toggleProjectPrompt: (state) => {
      if (state.currentChatId) {
        if (!state.settingsByChat[state.currentChatId]) {
          state.settingsByChat[state.currentChatId] = { ...defaultChatSettings };
        }
        state.settingsByChat[state.currentChatId].isProjectPromptEnabled = 
          !state.settingsByChat[state.currentChatId].isProjectPromptEnabled;
      }
    },
    
    // Toggle global data
    toggleGlobalData: (state) => {
      if (state.currentChatId) {
        if (!state.settingsByChat[state.currentChatId]) {
          state.settingsByChat[state.currentChatId] = { ...defaultChatSettings };
        }
        state.settingsByChat[state.currentChatId].isGlobalDataEnabled = 
          !state.settingsByChat[state.currentChatId].isGlobalDataEnabled;
      }
    },
    
    // Toggle project documents
    toggleProjectDocuments: (state) => {
      if (state.currentChatId) {
        if (!state.settingsByChat[state.currentChatId]) {
          state.settingsByChat[state.currentChatId] = { ...defaultChatSettings };
        }
        state.settingsByChat[state.currentChatId].isProjectDocumentsEnabled = 
          !state.settingsByChat[state.currentChatId].isProjectDocumentsEnabled;
      }
    },
    
    // Load settings from backend (when chat is loaded)
    loadChatSettings: (state, action: PayloadAction<{ chatId: string; settings: ChatSettings }>) => {
      state.settingsByChat[action.payload.chatId] = action.payload.settings;
    },
    
    // Clear settings for a chat (when deleted)
    clearChatSettings: (state, action: PayloadAction<string>) => {
      delete state.settingsByChat[action.payload];
    },
  },
});

export const {
  setCurrentChat,
  updateContextMode,
  toggleSystemPrompt,
  toggleUserPrompt,
  setActiveUserPrompt,
  toggleProjectPrompt,
  toggleGlobalData,
  toggleProjectDocuments,
  loadChatSettings,
  clearChatSettings,
} = chatSettingsSlice.actions;

// Selectors
export const selectCurrentChatSettings = (state: { chatSettings: ChatSettingsState }) => {
  if (!state.chatSettings.currentChatId) return defaultChatSettings;
  return state.chatSettings.settingsByChat[state.chatSettings.currentChatId] || defaultChatSettings;
};

export const selectChatSettings = (chatId: string) => (state: { chatSettings: ChatSettingsState }) => {
  return state.chatSettings.settingsByChat[chatId] || defaultChatSettings;
};

export default chatSettingsSlice.reducer;