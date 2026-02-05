async function loadProfile() {

  const usernameParam = getProfileUsernameFromURL();

  const titleEl = document.getElementById("games-title");
  titleEl.innerText = usernameParam ? "Games" : "My Games";

  // ---------- USER ----------
  const user = usernameParam
    ? await api(`/user/${encodeURIComponent(usernameParam)}`)
    : await api("/me");

  document.getElementById("username").innerText =
    user.username.charAt(0).toUpperCase() + user.username.slice(1);

  // ---------- GAMES ----------
  const games = user.gamelist || {};

  const list = document.getElementById("user-games");
  list.innerHTML = "";

  const entries = Object.entries(games);

  if (!entries.length) {
    list.innerHTML = "<p>No rated games yet</p>";
    return;
  }

  const ids = entries.map(([gameId]) => parseInt(gameId));
  const infos = await api("/get_essential", ids, "POST");

  const combined = infos.map(game => ({
    game,
    rating: games[game.id]
  }));

  combined.sort((a, b) => {
    if (b.rating !== a.rating) return b.rating - a.rating;
    return a.game.name.localeCompare(b.game.name);
  });

  combined.forEach(({ game, rating }) => {
    const li = document.createElement("li");
    li.className = "game-card";

    li.innerHTML = `
      <a href="game?id=${game.id}">
        <img src="https://images.igdb.com/igdb/image/upload/t_cover_big/${game.cover}.jpg">
        <div class="game-title">${game.name}</div>
        <div class="game-rating">${rating}/10</div>
      </a>
    `;

    list.appendChild(li);
  });
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

document.getElementById("logout-btn-mobile").addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/GameList/";
});

function getProfileUsernameFromURL() {
  const params = new URLSearchParams(window.location.search);
  return params.get("user");
}