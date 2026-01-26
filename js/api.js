const API_URL = "https://YOUR_BACKEND_URL";

async function api(endpoint, data=null) {
  const options = {
    method: data ? "POST" : "GET",
    headers: { "Content-Type": "application/json" },
    credentials: "include"
  };

  if (data) options.body = JSON.stringify(data);

  const res = await fetch(API_URL + endpoint, options);
  return await res.json();
}
