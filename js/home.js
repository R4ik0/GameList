async function loadRecommendations() {
  const res = await api("/recommendation?X=10", null, "POST");
  const list = document.getElementById("games-list");
  list.innerHTML = "";

  const gamesPromises = res.map(game =>
    api(`/get_game?id=${game.id}`, null, "POST")
  );

  const gamesInfos = await Promise.all(gamesPromises);

  for (const info_game of gamesInfos) {
    const li = document.createElement("li");

    const a = document.createElement("a");
    a.href = `game?id=${info_game.id}`;
    a.innerText = info_game.name;

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