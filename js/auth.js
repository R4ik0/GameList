const API_URL = "https://game-list-murex.vercel.app";

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
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await api("/register", { username, password });

  if (res.success && res.token) {
    localStorage.setItem("token", res.token);
    window.location.href = "home";
  } else {
    document.getElementById("error").innerText = "Registration failed";
  }
}

