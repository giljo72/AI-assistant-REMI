import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface ProjectSettingsState {
  projectPromptEnabled: boolean;
  globalDataEnabled: boolean;
  projectDocumentsEnabled: boolean;
  contextMode: string;
}

const initialState: ProjectSettingsState = {
  projectPromptEnabled: true,
  globalDataEnabled: false,
  projectDocumentsEnabled: true,
  contextMode: 'standard'
};

export const projectSettingsSlice = createSlice({
  name: 'projectSettings',
  initialState,
  reducers: {
    toggleProjectPrompt: (state) => {
      state.projectPromptEnabled = !state.projectPromptEnabled;
    },
    
    toggleGlobalData: (state) => {
      state.globalDataEnabled = !state.globalDataEnabled;
    },
    
    toggleProjectDocuments: (state) => {
      state.projectDocumentsEnabled = !state.projectDocumentsEnabled;
    },
    
    setProjectPromptEnabled: (state, action: PayloadAction<boolean>) => {
      state.projectPromptEnabled = action.payload;
    },
    
    setGlobalDataEnabled: (state, action: PayloadAction<boolean>) => {
      state.globalDataEnabled = action.payload;
    },
    
    setProjectDocumentsEnabled: (state, action: PayloadAction<boolean>) => {
      state.projectDocumentsEnabled = action.payload;
    },
    
    updateProjectSettings: (state, action: PayloadAction<Partial<ProjectSettingsState>>) => {
      return {
        ...state,
        ...action.payload
      };
    },
    
    setContextMode: (state, action: PayloadAction<string>) => {
      state.contextMode = action.payload;
    }
  }
});

export const {
  toggleProjectPrompt,
  toggleGlobalData,
  toggleProjectDocuments,
  setProjectPromptEnabled,
  setGlobalDataEnabled,
  setProjectDocumentsEnabled,
  updateProjectSettings,
  setContextMode
} = projectSettingsSlice.actions;

export default projectSettingsSlice.reducer;