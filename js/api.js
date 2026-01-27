async function api(path, data = null, method = "GET") {
  const token = localStorage.getItem("access_token");

  const res = await fetch("http://localhost:8000" + path, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { "Authorization": "Bearer " + token } : {})
    },
    body: data ? JSON.stringify(data) : null
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

  const res = await fetch("http://localhost:8000" + "/refresh", {
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
