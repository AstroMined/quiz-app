import { Configuration, QuestionSetsApi } from '../api';

const getConfig = () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  return new Configuration({
    basePath: 'http://localhost:8000', // Update this to your backend URL
    accessToken: token || undefined,
  });
};

export const questionSetsApi = new QuestionSetsApi(getConfig());

// You can create similar exports for other API services