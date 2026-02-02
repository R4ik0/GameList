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
  }, 500); // debounce 500ms
});

async function searchGames(query) {
  const results = await api(`/search?name=${encodeURIComponent(query)}`, null, "POST");
  const box = document.getElementById("search-results");
  box.innerHTML = "";

  results.slice(0, 5).forEach(game => {
    const item = document.createElement("div");
    item.className = "search-result-item";

    const img = document.createElement("img");
    img.src = "https://images.igdb.com/igdb/image/upload/t_cover_small/" + game.image + ".jpg";
    img.alt = game.name;

    const span = document.createElement("span");
    span.innerText = game.name;

    item.appendChild(img);
    item.appendChild(span);

    item.onclick = () => {
        window.location.href = `game?id=${game.id}`;
    };

    box.appendChild(item);
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
