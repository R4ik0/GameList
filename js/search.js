let searchTimeout = null;
let lastSearchId = 0;
let lastQuery = "";

document.getElementById("search-input").addEventListener("input", (e) => {
  const query = e.target.value.trim();
  lastQuery = query;

  if (searchTimeout) clearTimeout(searchTimeout);

  if (query.length < 1) {
    hideResults();
    return;
  }

  searchTimeout = setTimeout(() => {
    searchGames(query);
  }, 300);
});


function showLoader() {
  document.getElementById("search-loader").style.display = "block";
}

function hideLoader() {
  document.getElementById("search-loader").style.display = "none";
}

async function searchGames(query) {
  const mySearchId = ++lastSearchId;
  const box = document.getElementById("search-results");

  showLoader();

  try {
    const results = await api(
      `/search?name=${encodeURIComponent(query)}`,
      null,
      "POST"
    );

    if (mySearchId !== lastSearchId) return;

    if (mySearchId === lastSearchId) {
      box.innerHTML = "";
    }

    results.slice(0, 5).forEach(game => {
      const item = document.createElement("div");
      item.className = "search-result-item";

      const img = document.createElement("img");
      img.src =
        "https://images.igdb.com/igdb/image/upload/t_cover_small/" +
        game.image +
        ".jpg";

      const span = document.createElement("span");
      span.innerText = game.name;

      item.appendChild(img);
      item.appendChild(span);

      item.onclick = () => {
        window.location.href = `game?id=${game.id}`;
      };

      box.appendChild(item);
    });

    box.style.display = results.length ? "flex" : "none";

  } finally {
    if (mySearchId === lastSearchId) {
      hideLoader();
    }
  }
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

  if (lastQuery.length > 0) {
    searchGames(lastQuery);
  }
});


document.getElementById("search-overlay").addEventListener("click", () => {
  hideOverlay();
  document.getElementById("search-input").blur();
});

document.getElementById("results").addEventListener("click", () => {
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
