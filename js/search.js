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
    searchAll(query);
  }, 300);
});


function showLoader() {
  document.getElementById("search-loader").style.display = "block";
}

function hideLoader() {
  document.getElementById("search-loader").style.display = "none";
}

async function searchAll(query) {
  const mySearchId = ++lastSearchId;

  const gamesWrap = document.getElementById("games-container");
  const usersWrap = document.getElementById("users-container");

  const gamesBox = document.getElementById("games-results");
  const usersBox = document.getElementById("users-results");

  const resultsWrap = document.getElementById("results");

  showLoader();

  try {

    const [games, users] = await Promise.all([
      api(`/search?name=${encodeURIComponent(query)}`, null, "POST"),
      api(`/searchUser?query=${encodeURIComponent(query)}`, null, "POST")
    ]);

    if (mySearchId !== lastSearchId) return;

    gamesBox.innerHTML = "";
    usersBox.innerHTML = "";

    // ---------- GAMES ----------
    if (games.length) {
      gamesWrap.style.display = "block";

      games.slice(0, 5).forEach(game => {
        const item = document.createElement("div");
        item.className = "search-result-item";

        item.innerHTML = `
          <img src="https://images.igdb.com/igdb/image/upload/t_cover_small/${game.image}.jpg">
          <span>${game.name}</span>
        `;

        item.onclick = () => {
          window.location.href = `game?id=${game.id}`;
        };

        gamesBox.appendChild(item);
      });

    } else {
      gamesWrap.style.display = "none";
    }

    // ---------- USERS ----------
    if (users.length) {
      usersWrap.style.display = "block";

      users.slice(0, 5).forEach(user => {
        const item = document.createElement("div");
        item.className = "search-result-item";

        item.innerHTML = `
          <span class="material-icons">account_circle</span>
          <span>${user.username}</span>
        `;

        item.onclick = () => {
          window.location.href = `profile?user=${user.username}`;
        };

        usersBox.appendChild(item);
      });

    } else {
      usersWrap.style.display = "none";
    }

    resultsWrap.style.display =
      (games.length || users.length) ? "flex" : "none";

  } finally {
    if (mySearchId === lastSearchId) hideLoader();
  }
}

function hideResults() {
  document.getElementById("results").style.display = "none";
}

document.addEventListener("click", (e) => {
  if (!e.target.closest(".search-box")) {
    hideResults();
  }
});

document.getElementById("search-input").addEventListener("focus", () => {
  showOverlay();
  hideMobileNav();

  if (lastQuery.length > 0) {
    searchAll(lastQuery);
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
  showMobileNav();
}

function isMobileWidth() {
  return window.innerWidth < 830;
}

function hideMobileNav() {
  if (!isMobileWidth()) return;
  document.querySelector(".nav-links-mobile")
    ?.classList.add("hidden-for-search");
  document.querySelector(".search-box")
    ?.classList.add("expanded");
}

function showMobileNav() {
  document.querySelector(".nav-links-mobile")
    ?.classList.remove("hidden-for-search");
  document.querySelector(".search-box")
    ?.classList.remove("expanded");
}

document.getElementById("search-input").addEventListener("blur", () => {
  setTimeout(showMobileNav, 150);
});
