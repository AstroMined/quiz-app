// src/config/api.ts
import { OpenAPI } from '@/api';

export const initializeApi = () => {
  OpenAPI.BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
  console.log('API Base URL set to:', OpenAPI.BASE);
};