async function loadProfile() {
  const user = await api("/me");
  document.getElementById("username").innerText = user.username.charAt(0).toUpperCase() + user.username.slice(1);

  const games = await api("/GamesList");
  const list = document.getElementById("user-games");
  list.innerHTML = "";

  for (const [gameId, rating] of Object.entries(games)) {
    const game = await api(`/get_game?id=${gameId}`, null, "POST");

    const li = document.createElement("li");

    const a = document.createElement("a");
    a.href = `game?id=${gameId}`;
    a.innerText = game.name;

    const span = document.createElement("span");
    span.innerText = ` - Rating: ${rating}`;

    li.appendChild(a);
    li.appendChild(span);
    list.appendChild(li);
  }
}

loadProfile();

if (!localStorage.getItem("access_token")) {
    window.location.href = "/GameList/";
}

document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/GameList/";
});