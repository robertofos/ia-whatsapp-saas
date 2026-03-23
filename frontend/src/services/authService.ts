import api from "./api";

export async function login(payload: { username: string; password: string }) {
  const response = await api.post("/auth/login/", payload);
  return response.data;
}

export async function getMe() {
  const response = await api.get("/auth/me/");
  return response.data;
}