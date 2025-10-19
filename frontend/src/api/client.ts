import axios from 'axios';
import type {
  SessionInfo,
  SessionMetrics,
  CreateSessionResponse,
  ResetSessionResponse,
  HealthResponse,
  ChatResponse,
  EventResponse,
} from '../types';

// Get API URL from environment variable or use relative path for development
const API_BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1'; // Fallback to proxy for development

console.log('API Base URL:', API_BASE_URL);

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add session ID to requests
let currentSessionId: string | null = null;

export const setSessionId = (sessionId: string | null) => {
  currentSessionId = sessionId;
};

apiClient.interceptors.request.use((config) => {
  if (currentSessionId) {
    config.headers['X-Session-ID'] = currentSessionId;
  }
  return config;
});

// API Functions

export const createSession = async (): Promise<CreateSessionResponse> => {
  const response = await apiClient.post<CreateSessionResponse>('/sessions/create');
  return response.data;
};

export const getCurrentSessionInfo = async (): Promise<SessionInfo> => {
  const response = await apiClient.get<SessionInfo>('/sessions/current/info');
  return response.data;
};

export const getCurrentSessionMetrics = async (): Promise<SessionMetrics> => {
  const response = await apiClient.get<SessionMetrics>('/sessions/current/metrics');
  return response.data;
};

export const resetCurrentSession = async (): Promise<ResetSessionResponse> => {
  const response = await apiClient.post<ResetSessionResponse>('/sessions/current/reset');
  return response.data;
};

export const getHealth = async (): Promise<HealthResponse> => {
  const healthURL = import.meta.env.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL}/health`
    : '/health';
  const response = await axios.get<HealthResponse>(healthURL);
  return response.data;
};

// Chat Functions
export const sendChatMessage = async (message: string): Promise<ChatResponse> => {
  const response = await apiClient.post<ChatResponse>('/playground/chat', { message });
  return response.data;
};

export const getRecentEvents = async (limit: number = 50): Promise<EventResponse[]> => {
  const response = await apiClient.get<EventResponse[]>(`/events/recent?limit=${limit}`);
  return response.data;
};

export default apiClient;
