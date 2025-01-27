import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const chatApi = {
  // sendMessage: async (message, sessionId) => {
  //   const response = await axios.post(`${API_URL}/chat/chat/rag`, {
  //     message,
  //     session_id: sessionId
  //   });
  //   return response.data;
  // },
  sendMessage: async (message, sessionId, onChunkReceived) => {
    try {
      const response = await fetch(`${API_URL}/chat/chat/rag`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId
        }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        onChunkReceived(chunk);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  getHistory: async (sessionId) => {
    const response = await axios.get(`${API_URL}/chat/history/${sessionId}`);
    return response.data;
  },

  getAllSessions: async () => {
    const response = await axios.get(`${API_URL}/chat/sessions`);
    return response.data;
  },

  createSession: async () => {
    const response = await axios.post(`${API_URL}/chat/sessions`);
    return response.data.session_id;
  },

  renameSession: async (oldSessionId, newSessionId) => {
    await axios.put(`${API_URL}/chat/sessions/${oldSessionId}`, {
      new_session_id: newSessionId
    });
  },

  deleteSession: async (sessionId) => {
    await axios.delete(`${API_URL}/chat/sessions/${sessionId}`);
  },

  uploadPDF: async (formData) => {
    const response = await axios.post(`${API_URL}/chat/documents/upload_pdf`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  }
 };