async function loadProfile() {
  const user = await api("/me");

  document.getElementById("username").innerText =
    user.username.charAt(0).toUpperCase() + user.username.slice(1);

  const games = await api("/GamesList"); // { id: rating }

  const list = document.getElementById("user-games");
  list.innerHTML = "";

  const entries = Object.entries(games);

  if (!entries.length) {
    list.innerHTML = "<p>No rated games yet</p>";
    return;
  }

  // 🔥 extraire IDs
  const ids = entries.map(([gameId]) => parseInt(gameId));

  // 🔥 appel batch unique
  const infos = await api("/get_essential", ids, "POST");

  // 🔥 associer rating
  const combined = infos.map(game => ({
    game,
    rating: games[game.id]
  }));

  // 🔥 tri note desc + alpha
  combined.sort((a, b) => {
    if (b.rating !== a.rating) {
      return b.rating - a.rating;
    }
    return a.game.name.localeCompare(b.game.name);
  });

  // 🔥 rendu
  combined.forEach(({ game, rating }) => {
    const li = document.createElement("li");
    li.className = "game-card";

    const a = document.createElement("a");
    a.href = `game?id=${game.id}`;

    const img = document.createElement("img");
    img.src = `https://images.igdb.com/igdb/image/upload/t_cover_big/${game.cover}.jpg`;
    img.alt = game.name;

    const title = document.createElement("div");
    title.className = "game-title";
    title.innerText = game.name;

    const note = document.createElement("div");
    note.className = "game-rating";
    note.innerText = `${rating}/10`;

    a.appendChild(img);
    a.appendChild(title);
    a.appendChild(note);
    li.appendChild(a);
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