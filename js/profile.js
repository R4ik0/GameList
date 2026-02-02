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

  // 🔥 on récupère toutes les infos en parallèle
  const infos = await Promise.all(
    entries.map(([gameId]) =>
      api(`/get_essential?id=${gameId}`, null, "POST")
    )
  );

  infos.forEach((game, index) => {
    const rating = entries[index][1];

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