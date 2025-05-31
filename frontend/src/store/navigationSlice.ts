import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Define the possible view types
export type View = 'project' | 'chat' | 'document' | 'projectFiles' | 'mainFiles' | 'searchResults';

interface NavigationState {
  activeView: View;
  activeProjectId: string | null;
  activeChatId: string | null;
  activeDocumentId: string | null;
  isSearchActive: boolean;
  searchQuery: string;
}

const initialState: NavigationState = {
  activeView: 'project',
  activeProjectId: null,
  activeChatId: null,
  activeDocumentId: null,
  isSearchActive: false,
  searchQuery: '',
};

export const navigationSlice = createSlice({
  name: 'navigation',
  initialState,
  reducers: {
    // Project navigation
    setActiveProject: (state, action: PayloadAction<string | null>) => {
      state.activeProjectId = action.payload;
      // When selecting a project, we default to the project view
      state.activeView = 'project';
      // Clear other active items when switching projects
      state.activeChatId = null;
      state.activeDocumentId = null;
    },
    
    // View navigation
    setActiveView: (state, action: PayloadAction<View>) => {
      state.activeView = action.payload;
      // Clear specific IDs based on view changes
      if (action.payload === 'mainFiles') {
        // When going to main files, clear project context
        state.activeProjectId = null;
        state.activeChatId = null;
        state.activeDocumentId = null;
      }
    },
    
    // Chat navigation
    setActiveChat: (state, action: PayloadAction<string | null>) => {
      state.activeChatId = action.payload;
      if (action.payload) {
        state.activeView = 'chat';
      }
    },
    
    // Document navigation
    setActiveDocument: (state, action: PayloadAction<string | null>) => {
      state.activeDocumentId = action.payload;
      if (action.payload) {
        state.activeView = 'document';
      }
    },
    
    // Search
    setSearchActive: (state, action: PayloadAction<boolean>) => {
      state.isSearchActive = action.payload;
      if (action.payload) {
        state.activeView = 'searchResults';
      }
    },
    
    setSearchQuery: (state, action: PayloadAction<string>) => {
      state.searchQuery = action.payload;
    },
    
    // Compound navigation actions
    navigateToMainFiles: (state) => {
      state.activeView = 'mainFiles';
      state.activeProjectId = null;
      state.activeChatId = null;
      state.activeDocumentId = null;
    },
    
    navigateToProjectFiles: (state, action: PayloadAction<string>) => {
      state.activeView = 'projectFiles';
      state.activeProjectId = action.payload;
      state.activeChatId = null;
      state.activeDocumentId = null;
    },
    
    // Reset navigation state
    resetNavigation: () => initialState,
  },
});

export const {
  setActiveProject,
  setActiveView,
  setActiveChat,
  setActiveDocument,
  setSearchActive,
  setSearchQuery,
  navigateToMainFiles,
  navigateToProjectFiles,
  resetNavigation,
} = navigationSlice.actions;

export default navigationSlice.reducer;