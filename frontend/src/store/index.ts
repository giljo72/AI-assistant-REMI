import { configureStore } from '@reduxjs/toolkit';
import userPromptsReducer from './userPromptsSlice';
import systemPromptsReducer from './systemPromptsSlice';
import projectSettingsReducer from './projectSettingsSlice';
import navigationReducer from './navigationSlice';
import typedMessagesReducer from './typedMessagesSlice';
import chatSettingsReducer from './chatSettingsSlice';

export const store = configureStore({
  reducer: {
    userPrompts: userPromptsReducer,
    systemPrompts: systemPromptsReducer,
    projectSettings: projectSettingsReducer,
    navigation: navigationReducer,
    typedMessages: typedMessagesReducer,
    chatSettings: chatSettingsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false, // Allows for non-serializable data in the store
    }),
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;