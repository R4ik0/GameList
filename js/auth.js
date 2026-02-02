async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch(API_URL + "/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: formData
  });

  if (!res.ok) {
    document.getElementById("error").innerText = "Password or username incorrect";
    return;
  }

  const data = await res.json();

  // Backend renvoie { access_token, refresh_token }
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);

  window.location.href = "home";
}

document.getElementById("login-form").addEventListener("submit", (e) => {
  e.preventDefault();
  login();
});


async function register() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!username || !password) {
    document.getElementById("error").innerText = "Username and password required";
    return;
  }

  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);
  formData.append("role", "user");

  const res = await fetch(API_URL + "/signin", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => null);
    document.getElementById("error").innerText =
      err?.detail || "Registration failed";
    return;
  }

  const data = await res.json();

  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);

  window.location.href = "home";
}


