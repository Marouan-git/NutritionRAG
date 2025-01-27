import { useState } from 'react';
import { FiPlus, FiEdit, FiTrash2 } from 'react-icons/fi';
import { chatApi } from '../services/api';

const ConversationsList = ({ 
  sessions, 
  currentSession, 
  onSessionChange,
  onSessionsUpdated,
  onSetSessions,
  onSetCurrentSession
}) => {
  const [renamingSession, setRenamingSession] = useState(null);
  const [newSessionName, setNewSessionName] = useState('');

  const handleCreateSession = async () => {
    try {
      const newSession = await chatApi.createSession();
      onSessionChange(newSession);
      onSessionsUpdated();
    } catch (error) {
      alert('Error creating session');
    }
  };


  const handleDeleteSession = async (sessionId) => {
    if (window.confirm('Are you sure you want to delete this session?')) {
      try {
        await chatApi.deleteSession(sessionId);
        
        // Use passed state setters
        onSetSessions(prev => prev.filter(s => s !== sessionId));
        
        if (currentSession === sessionId) {
          if (sessions.length > 1) {
            onSetCurrentSession(sessions.find(s => s !== sessionId));
          } else {
            const newSession = await chatApi.createSession();
            onSetCurrentSession(newSession);
            onSetSessions([newSession]);
          }
        }
      } catch (error) {
        alert('Error deleting session');
        onSessionsUpdated();
      }
    }
  };

  const handleRenameSession = async (oldSessionId) => {
    if (!newSessionName.trim()) return;
    
    try {
      await chatApi.renameSession(oldSessionId, newSessionName);
      setRenamingSession(null);
      setNewSessionName('');
      onSessionsUpdated();
      
      if (currentSession === oldSessionId) {
        onSessionChange(newSessionName);
      }
    } catch (error) {
      alert('Error renaming session');
    }
  };

  return (
    <div className="w-64 border-r p-4 hidden md:block flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Conversations</h2>
        <button
          onClick={handleCreateSession}
          className="p-2 hover:bg-gray-100 rounded-lg"
          title="New session"
        >
          <FiPlus className="w-5 h-5" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto max-h-[calc(100vh-160px)] space-y-2">
        {sessions.map((session) => (
          <div key={session} className="group flex items-center justify-between hover:bg-gray-100 rounded-lg">
            {renamingSession === session ? (
              <input
                type="text"
                value={newSessionName}
                onChange={(e) => setNewSessionName(e.target.value)}
                onBlur={() => handleRenameSession(session)}
                onKeyPress={(e) => e.key === 'Enter' && handleRenameSession(session)}
                autoFocus
                className="flex-1 px-3 py-2 rounded-lg"
              />
            ) : (
              <button
                onClick={() => onSessionChange(session)}
                className={`w-full text-left px-3 py-2 rounded-lg ${
                  currentSession === session
                    ? 'bg-blue-100 text-blue-800'
                    : 'hover:bg-gray-100'
                }`}
              >
                 {session}
              </button>
            )}

            <div className="flex opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={() => {
                  setRenamingSession(session);
                  setNewSessionName(session);
                }}
                className="p-1 hover:text-blue-600"
                title="Rename"
              >
                <FiEdit className="w-4 h-4" />
              </button>
              <button
                onClick={() => handleDeleteSession(session)}
                className="p-1 hover:text-red-600"
                title="Delete"
              >
                <FiTrash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ConversationsList;