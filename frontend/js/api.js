const API_BASE_URL = "";

const tokenKey = "crm_access_token";

export function getToken() {
  return localStorage.getItem(tokenKey);
}

export function saveToken(token) {
  localStorage.setItem(tokenKey, token);
}

export function removeToken() {
  localStorage.removeItem(tokenKey);
}

export function authHeaders(extra = {}) {
  const token = getToken();
  return {
    ...extra,
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
}

function validationMessage(data) {
  if (!data) return "Request failed";
  if (Array.isArray(data.detail)) {
    return data.detail
      .map(item => item?.msg || "Invalid value")
      .join("; ");
  }
  return data.detail || "Request failed";
}

export async function apiRequest(path, options = {}) {
  const headers = authHeaders(options.headers || {});
  if (options.body && !(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
  });

  const text = await response.text();
  let data = null;
  if (text) {
    try { data = JSON.parse(text); }
    catch { data = text; }
  }

  if (response.status === 401) {
    removeToken();
    if (!location.pathname.endsWith("login.html")) {
      location.href = "/app/login.html";
    }
  }

  if (!response.ok) {
    const error = new Error(validationMessage(data));
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

export async function login(email, password) {
  const body = new URLSearchParams({
    username: email,
    password
  });

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body
  });

  const text = await response.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = null; }

  if (!response.ok) {
    const error = new Error(validationMessage(data));
    error.status = response.status;
    error.data = data;
    throw error;
  }

  saveToken(data.access_token);
  return data;
}

export async function me() {
  return apiRequest("/users/me");
}
