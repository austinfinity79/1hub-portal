import axios from 'axios';

const ACCESS_KEY = '1hub_access_token';
const REFRESH_KEY = '1hub_refresh_token';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  headers: { 'Content-Type': 'application/json' },
});

// Attach Authorization header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 – attempt token refresh once
let refreshPromise: Promise<string> | null = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;

    // Skip refresh for login/refresh endpoints or already retried
    if (
      !error.response ||
      error.response.status !== 401 ||
      original._retry ||
      original.url === '/api/auth/login' ||
      original.url === '/api/auth/refresh'
    ) {
      return Promise.reject(error);
    }

    original._retry = true;

    const refreshToken = localStorage.getItem(REFRESH_KEY);
    if (!refreshToken) {
      // No refresh token – force login
      localStorage.removeItem(ACCESS_KEY);
      localStorage.removeItem(REFRESH_KEY);
      window.location.href = '/login';
      return Promise.reject(error);
    }

    try {
      // Deduplicate concurrent refresh requests
      if (!refreshPromise) {
        refreshPromise = axios
          .post(
            (import.meta.env.VITE_API_BASE_URL || '') + '/api/auth/refresh',
            { refresh_token: refreshToken },
            { headers: { 'Content-Type': 'application/json' } },
          )
          .then((res) => {
            const { access_token, refresh_token } = res.data;
            localStorage.setItem(ACCESS_KEY, access_token);
            localStorage.setItem(REFRESH_KEY, refresh_token);
            return access_token as string;
          })
          .finally(() => {
            refreshPromise = null;
          });
      }

      const newToken = await refreshPromise;
      original.headers.Authorization = `Bearer ${newToken}`;
      return api(original);
    } catch {
      // Refresh failed – redirect to login
      localStorage.removeItem(ACCESS_KEY);
      localStorage.removeItem(REFRESH_KEY);
      window.location.href = '/login';
      return Promise.reject(error);
    }
  },
);

export default api;
