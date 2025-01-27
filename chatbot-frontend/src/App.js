import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from './components/NavBar';
import ChatPage from './pages/ChatPage';
import ProfilePage from './pages/ProfilePage';
import { chatApi } from './services/api';
import HomePage from './pages/HomePage';
import UploadPage from './pages/UploadPage';

function App() {
  const [messages, setMessages] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const newSession = `session-${Date.now()}`;
    setCurrentSession(newSession);
    loadSessions();
  }, []);


  useEffect(() => {
    if (currentSession) {
      loadHistory();
    } else {
      setMessages([]); // Clear messages when no session
    }
  }, [currentSession]);


  const loadSessions = async () => {
    try {
      const response = await chatApi.getAllSessions();
      setSessions(response);
      
      // Only create new session if there are NO sessions
      if (response.length === 0) {
        const newSession = await chatApi.createSession();
        setCurrentSession(newSession);
        setMessages([]);
      }
      // Else, keep current session if valid
      else if (!currentSession || !response.includes(currentSession)) {
        setCurrentSession(response[0]); // Select first session
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };


  const handleSessionChange = (newSession) => {
    setCurrentSession(newSession);
  };

  const loadHistory = async () => {
    try {
      const history = await chatApi.getHistory(currentSession);
      setMessages(history);
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  // Update the handleSendMessage function
  const handleSendMessage = async (content) => {
    let sessionId = currentSession;
    const tempMessageId = Date.now();
  
    // Immediately show user message
    setMessages(prev => [...prev, 
      { role: 'user', content, id: tempMessageId - 1 },
      { role: 'assistant', content: '', id: tempMessageId, pending: true }
    ]);
  
    if (!sessionId) {
      try {
        const newSession = await chatApi.createSession();
        sessionId = newSession;
        setCurrentSession(newSession);
        setSessions(prev => [...prev, newSession]);
      } catch (error) {
        alert('Failed to create new conversation');
        return;
      }
    }
  
    setIsLoading(true);
    
    try {
      await chatApi.sendMessage(content, sessionId, (chunk) => {
        setMessages(prev => prev.map(msg => {
          if (msg.id === tempMessageId) {
            return { 
              ...msg, 
              content: msg.content + chunk,
              pending: true
            };
          }
          return msg;
        }));
      });
      
      // Final update to mark as complete
      setMessages(prev => prev.map(msg => 
        msg.id === tempMessageId ? {...msg, pending: false} : msg
      ));
      
    } catch (error) {
      setMessages(prev => prev.map(msg => {
        if (msg.id === tempMessageId) {
          return { 
            ...msg, 
            content: 'Error: ' + error.message,
            pending: false
          };
        }
        return msg;
      }));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Router>
      <div className="h-screen bg-white flex flex-col">
        <Navbar />
        <div className="flex-grow overflow-hidden"> {/* Added overflow-hidden */}
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route
              path="/chat"
              element={
                <ChatPage
                  sessions={sessions}
                  currentSession={currentSession}
                  onSessionChange={setCurrentSession}
                  onSessionsUpdated={loadSessions}
                  onSetSessions={setSessions}
                  onSetCurrentSession={setCurrentSession}
                  messages={messages}
                  handleSendMessage={handleSendMessage}
                  isLoading={isLoading}
                />
              }
            />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="*" element={<Navigate to="/" />} />
            <Route path="/upload" element={<UploadPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;