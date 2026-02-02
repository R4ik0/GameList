let currentUserGames = {};
async function initUserGames() {
  window.currentUserGames = await api("/GamesList");
}
initUserGames();

function getGameIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}

async function loadGame() {
  const gameId = getGameIdFromUrl();
  if (!gameId) return;

  const game = await api(`/full_game?id=${gameId}`, null, "POST");

  document.getElementById("game-name").innerText = game.name;
  document.getElementById("game-title").innerText = game.name + " · GameList";
  document.getElementById("storyline").innerText = game.storyline || "No description available for this game.";


  fillList("genres", game.genres);
  fillList("themes", game.themes);
  fillList("platforms", game.platforms);
  fillList("modes", game.game_modes);

  const coverEl = document.getElementById("game-cover");
  if (game.cover) {
      coverEl.src = "https://images.igdb.com/igdb/image/upload/t_cover_big/" + game.cover + ".jpg";
      coverEl.style.display = "block";
  } else {
      coverEl.style.display = "none";
  }
}

function fillList(id, items) {
  const ul = document.getElementById(id);
  ul.innerHTML = "";

  if (!items) return;

  items.forEach(i => {
    const li = document.createElement("li");
    li.innerText = i;
    ul.appendChild(li);
  });
}

loadGame();

const rateBtn = document.getElementById("rate-btn");
const popup = document.getElementById("rate-popup");
const closePopup = document.getElementById("close-popup");
const saveBtn = document.getElementById("save-rating");
const deleteBtn = document.getElementById("delete-rating");
const ratingForm = document.getElementById("rating-form");
const ratingInput = document.getElementById("rating-input");

let currentGameId = getGameIdFromUrl();

// Ouvrir pop-up
rateBtn.addEventListener("click", () => {
  popup.style.display = "block";
  // si le jeu est déjà noté, pré-remplir
  const currentUserGames = window.currentUserGames || {}; // récupéré au chargement
  if (currentUserGames[currentGameId]) {
    ratingInput.value = currentUserGames[currentGameId];
  } else {
    ratingInput.value = "";
  }
});

// Fermer pop-up
closePopup.addEventListener("click", () => popup.style.display = "none");
window.addEventListener("click", (e) => {
  if (e.target === popup) popup.style.display = "none";
});

// Enregistrer / modifier note
ratingForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const rating = parseInt(ratingInput.value);
  if (rating < 1 || rating > 10 || isNaN(rating)) {
    alert("Enter a valid rating (1-10)");
    return;
  }

  const res = await api(`/GamesList/${currentGameId}/${rating}`, null, "POST");
  window.currentUserGames = res; // mettre à jour localement
  popup.style.display = "none";
});

// Supprimer note
deleteBtn.addEventListener("click", async () => {
  const res = await api(`/GamesList/${currentGameId}`, null, "DELETE");
  window.currentUserGames = res;
  popup.style.display = "none";
  alert("Game removed from your list");
});

if (!localStorage.getItem("access_token")) {
    window.location.href = "/GameList/";
}

document.getElementById("logout-btn").addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.location.href = "/GameList/";
});