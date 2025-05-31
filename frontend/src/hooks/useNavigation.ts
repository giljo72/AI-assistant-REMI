import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import {
  setActiveProject,
  setActiveView,
  setActiveChat,
  setActiveDocument,
  navigateToMainFiles,
  navigateToProjectFiles,
  View
} from '../store/navigationSlice';

/**
 * Custom hook to access and update navigation state
 */
export const useNavigation = () => {
  const dispatch = useDispatch();
  const navigationState = useSelector((state: RootState) => state.navigation);

  // Helper functions for common navigation actions
  const navigateToProject = (projectId: string) => {
    dispatch(setActiveProject(projectId));
  };

  const navigateToChat = (chatId: string, projectId?: string) => {
    if (projectId) {
      dispatch(setActiveProject(projectId));
    }
    dispatch(setActiveChat(chatId));
  };

  const navigateToDocument = (documentId: string, projectId?: string) => {
    if (projectId) {
      dispatch(setActiveProject(projectId));
    }
    dispatch(setActiveDocument(documentId));
  };

  const navigateToView = (view: View) => {
    dispatch(setActiveView(view));
  };

  const openMainFileManager = () => {
    dispatch(navigateToMainFiles());
  };

  const openProjectFileManager = (projectId: string) => {
    dispatch(navigateToProjectFiles(projectId));
  };

  return {
    // Current state
    ...navigationState,
    
    // Navigation actions
    navigateToProject,
    navigateToChat,
    navigateToDocument,
    navigateToView,
    openMainFileManager,
    openProjectFileManager,
  };
};