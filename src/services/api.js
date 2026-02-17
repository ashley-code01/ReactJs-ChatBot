// src/services/api.js
// Backend API service for chatbot

const BACKEND_URL = 'http://localhost:5000/api';

// Generate or retrieve session ID
const getSessionId = () => {
  let sessionId = localStorage.getItem('chatbot_session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('chatbot_session_id', sessionId);
  }
  return sessionId;
};

// Get user ID (optional - for tracking users)
const getUserId = () => {
  let userId = localStorage.getItem('chatbot_user_id');
  if (!userId) {
    userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('chatbot_user_id', userId);
  }
  return userId;
};

/**
 * Send message to backend for storage
 * @param {string} message - The message content
 * @param {string} role - 'user' or 'assistant'
 * @param {string} source - Where the message came from (e.g., 'groq', 'user_input')
 */
export const sendMessageToBackend = async (message, role = 'user', source = 'user_input') => {
  try {
    const response = await fetch(`${BACKEND_URL}/chat/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: getSessionId(),
        user_id: getUserId(),
        role,
        source,
      }),
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Backend API error:', error);
    // Don't throw - just log and return null so app continues working
    return null;
  }
};

/**
 * Get chat history from backend
 */
export const getChatHistory = async () => {
  try {
    const sessionId = getSessionId();
    const response = await fetch(`${BACKEND_URL}/chat/history/${sessionId}`);

    if (!response.ok) {
      throw new Error(`History error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('History API error:', error);
    return null;
  }
};

/**
 * Submit feedback for a message
 * @param {number} messageId - Database message ID
 * @param {string} feedback - 'positive' or 'negative'
 * @param {string} comment - Optional comment
 */
export const submitFeedback = async (messageId, feedback, comment = '') => {
  try {
    const response = await fetch(`${BACKEND_URL}/chat/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message_id: messageId,
        feedback,
        comment,
      }),
    });

    if (!response.ok) {
      throw new Error(`Feedback error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Feedback API error:', error);
    return null;
  }
};

/**
 * Check backend health
 */
export const checkBackendHealth = async () => {
  try {
    const response = await fetch('http://localhost:5001/api/health');
    if (!response.ok) {
      return false;
    }
    const data = await response.json();
    return data.status === 'healthy';
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
};

/**
 * Get admin statistics
 */
export const getAdminStats = async () => {
  try {
    const response = await fetch(`${BACKEND_URL}/admin/stats`);
    if (!response.ok) {
      throw new Error(`Stats error: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Stats API error:', error);
    return null;
  }
};

export default {
  sendMessageToBackend,
  getChatHistory,
  submitFeedback,
  checkBackendHealth,
  getAdminStats,
  getSessionId,
  getUserId,
};