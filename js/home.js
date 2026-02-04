async function loadRecommendations() {
  const res = await api("/recommendation?X=5", null, "POST");
  const list = document.getElementById("games-list");
  list.innerHTML = "";

  const gamesPromises = res.map(game =>
    api(`/get_essential?id=${game}`, null, "POST")
  );

  const gamesInfos = await Promise.all(gamesPromises);

  for (const game of gamesInfos) {
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

    a.appendChild(img);
    a.appendChild(title);
    li.appendChild(a);
    list.appendChild(li);
  }
}


loadRecommendations();

if (!localStorage.getItem("access_token")) {
    window.location.href = "/GameList/";
}

document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/GameList/";
});