let searchTimeout = null;

document.getElementById("search-input").addEventListener("input", (e) => {
  const query = e.target.value.trim();

  if (searchTimeout) clearTimeout(searchTimeout);

  if (query.length < 2) {
    hideResults();
    return;
  }

  searchTimeout = setTimeout(() => {
    searchGames(query);
  }, 300); // debounce 300ms
});

async function searchGames(query) {
  const results = await api(`/search?name=${encodeURIComponent(query)}`, null, "POST");
  const box = document.getElementById("search-results");
  box.innerHTML = "";

  results.slice(0, 5).forEach(game => {
    const div = document.createElement("div");
    div.innerText = game.name;
    div.onclick = () => {
      window.location.href = `game?id=${game.id}`;
    };
    box.appendChild(div);
  });

  box.style.display = results.length ? "block" : "none";
}

function hideResults() {
  const box = document.getElementById("search-results");
  box.style.display = "none";
}

document.addEventListener("click", (e) => {
  if (!e.target.closest(".search-box")) {
    hideResults();
  }
});

document.getElementById("search-input").addEventListener("focus", () => {
  showOverlay();
});

document.getElementById("search-overlay").addEventListener("click", () => {
  hideOverlay();
  document.getElementById("search-input").blur();
});

function showOverlay() {
  document.getElementById("search-overlay").style.display = "block";
}

function hideOverlay() {
  document.getElementById("search-overlay").style.display = "none";
  hideResults();
}
