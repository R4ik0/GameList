loadMyGames();

async function loadMyGames() {
  const games = await api("/my-games");
  const div = document.getElementById("my-games");
  div.innerHTML = "";

  games.forEach(g => {
    div.innerHTML += `
      <div class="card">
        <h3>${g.name}</h3>
        <input type="number" min="1" max="10"
               value="${g.rating}"
               onchange="rateGame(${g.id}, this.value)">
      </div>
    `;
  });
}

async function rateGame(gameId, rating) {
  await api("/rate", {
    game_id: gameId,
    rating: rating
  });
}

// if (!localStorage.getItem("token")) {
//     window.location.href = "index.html";
// }

document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("token");
    window.location.href = "/";
});