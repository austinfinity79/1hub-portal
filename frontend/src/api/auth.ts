import api from './client';
import type { User } from '../types';

export async function loginApi(
  username: string,
  password: string,
): Promise<{ access_token: string; refresh_token: string }> {
  const { data } = await api.post('/api/auth/login', { username, password });
  return data;
}

export async function refreshApi(
  refresh_token: string,
): Promise<{ access_token: string; refresh_token: string }> {
  const { data } = await api.post('/api/auth/refresh', { refresh_token });
  return data;
}

export async function logoutApi(refresh_token: string): Promise<void> {
  await api.post('/api/auth/logout', { refresh_token });
}

export async function fetchMe(): Promise<User> {
  const { data } = await api.get<User>('/api/auth/me');
  return data;
}

export async function fetchUsers(): Promise<User[]> {
  const { data } = await api.get<User[]>('/api/users');
  return data;
}

export async function createUser(payload: {
  username: string;
  email: string;
  password: string;
  role: string;
}): Promise<User> {
  const { data } = await api.post<User>('/api/users', payload);
  return data;
}
