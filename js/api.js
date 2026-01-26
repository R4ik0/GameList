const API_URL = "http://localhost:8000";

export async function api(endpoint, options = {}) {
  const accessToken = localStorage.getItem("access_token");

  const headers = {
    ...(accessToken && { Authorization: "Bearer " + accessToken }),
    ...(options.headers || {})
  };

  const res = await fetch(API_URL + endpoint, {
    ...options,
    headers
  });

  // Access token expiré → refresh automatique
  if (res.status === 401 && localStorage.getItem("refresh_token")) {
    const refreshed = await refreshToken();
    if (refreshed) return api(endpoint, options);
  }

  return res.json();
}

async function refreshToken() {
  const refreshToken = localStorage.getItem("refresh_token");

  const res = await fetch(API_URL + "/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(refreshToken)
  });

  if (!res.ok) {
    logout();
    return false;
  }

  const data = await res.json();
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);
  return true;
}
