import React from 'react';
import ConversationsList from '../components/ConversationsList';
import ChatWindow from '../components/ChatWindow';
import MessageInput from '../components/MessageInput';

const ChatPage = ({ 
  sessions, 
  currentSession, 
  onSessionChange,
  onSessionsUpdated,
  onSetSessions,
  onSetCurrentSession,
  messages, 
  handleSendMessage, 
  isLoading 
}) => {
  return (
    <div className="flex h-full overflow-hidden">
      <ConversationsList
        sessions={sessions}
        currentSession={currentSession}
        onSessionChange={onSessionChange}
        onSessionsUpdated={onSessionsUpdated}
        onSetSessions={onSetSessions}
        onSetCurrentSession={onSetCurrentSession}
      />
      <div className="flex-1 flex flex-col h-full">
        <ChatWindow messages={messages} />
        <MessageInput 
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
};

export default ChatPage;