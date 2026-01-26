const API_URL = "https://YOUR_BACKEND_URL";

export async function api(endpoint, data = null) {
  const token = localStorage.getItem("token");

  const options = {
    method: data ? "POST" : "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { "Authorization": "Bearer " + token } : {})
    },
    body: data ? JSON.stringify(data) : null
  };

  const res = await fetch(API_URL + endpoint, options);

  // Si le token est invalide ou expiré
  if (res.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "index.html";
  }

  return res.json();
}
