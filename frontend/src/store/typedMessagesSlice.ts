import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface TypedMessagesState {
  typedMessageIds: Set<string>;
}

const initialState: TypedMessagesState = {
  typedMessageIds: new Set<string>()
};

// Convert Set to Array for serialization
const typedMessagesSlice = createSlice({
  name: 'typedMessages',
  initialState: {
    typedMessageIds: [] as string[]
  },
  reducers: {
    markMessageAsTyped: (state, action: PayloadAction<string>) => {
      if (!state.typedMessageIds.includes(action.payload)) {
        state.typedMessageIds.push(action.payload);
      }
    },
    markMultipleMessagesAsTyped: (state, action: PayloadAction<string[]>) => {
      action.payload.forEach(id => {
        if (!state.typedMessageIds.includes(id)) {
          state.typedMessageIds.push(id);
        }
      });
    },
    clearTypedMessages: (state) => {
      state.typedMessageIds = [];
    }
  }
});

export const { markMessageAsTyped, markMultipleMessagesAsTyped, clearTypedMessages } = typedMessagesSlice.actions;

// Selector to check if a message has been typed
export const selectIsMessageTyped = (state: any, messageId: string) => 
  state.typedMessages.typedMessageIds.includes(messageId);

// Selector to get all typed message IDs as a Set
export const selectTypedMessageIds = (state: any) => 
  new Set(state.typedMessages.typedMessageIds);

export default typedMessagesSlice.reducer;