loadRecommendations();

async function loadRecommendations() {
  const games = await api("/recommendations");

  const grid = document.getElementById("reco-grid");
  grid.innerHTML = "";

  games.forEach(g => {
    grid.innerHTML += `
      <div class="card">
        <h3>${g.name}</h3>
        <p>Predicted score: ${g.score.toFixed(1)}</p>
        <p>${g.genres.join(", ")}</p>
      </div>
    `;
  });
}
