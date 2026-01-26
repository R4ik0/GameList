async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await api("/login", { username, password });

  // Ici on suppose que le backend renvoie { success: true, token: "JWT_TOKEN_HERE" }
  if (res.success && res.token) {
    // On stocke le JWT dans le navigateur
    localStorage.setItem("token", res.token);
    window.location = "home.html";
  } else {
    document.getElementById("error").innerText = "Login failed";
  }
}

async function register() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await api("/register", { username, password });

  if (res.success && res.token) {
    localStorage.setItem("token", res.token);
    window.location = "home.html";
  } else {
    document.getElementById("error").innerText = "Registration failed";
  }
}

