import { configureStore } from '@reduxjs/toolkit';
import userPromptsReducer from './userPromptsSlice';
import projectSettingsReducer from './projectSettingsSlice';
import navigationReducer from './navigationSlice';
import typedMessagesReducer from './typedMessagesSlice';

export const store = configureStore({
  reducer: {
    userPrompts: userPromptsReducer,
    projectSettings: projectSettingsReducer,
    navigation: navigationReducer,
    typedMessages: typedMessagesReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false, // Allows for non-serializable data in the store
    }),
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;