async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const res = await api("/login", { username, password });
  if (res.success) window.location = "home.php";
  else document.getElementById("error").innerText = "Login failed";
}

async function register() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await api("/register", { username, password });
  if (res.success) window.location = "home.php";
}
