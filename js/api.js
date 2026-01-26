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

  return res.json();
}
