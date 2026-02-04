import os
import io
import joblib
import numpy as np
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Optional, Union
import requests
from pydantic import BaseModel

class NpLabelEncoder:
    def fit(self, values):
        self.classes_ = np.array(sorted(set(values)))
        self.index = {v: i for i, v in enumerate(self.classes_)}
        return self

    def transform(self, values):
        return np.array([self.index[v] for v in values])

    def fit_transform(self, values):
        self.fit(values)
        return self.transform(values)

class NpMultiLabelBinarizer:
    def fit(self, list_of_lists):
        classes = sorted({item for sub in list_of_lists for item in sub})
        self.classes_ = np.array(classes)
        self.index = {v: i for i, v in enumerate(classes)}
        return self

    def transform(self, list_of_lists):
        X = np.zeros((len(list_of_lists), len(self.classes_)))
        for i, items in enumerate(list_of_lists):
            for it in items:
                if it in self.index:
                    X[i, self.index[it]] = 1
        return X

    def fit_transform(self, list_of_lists):
        self.fit(list_of_lists)
        return self.transform(list_of_lists)

def one_hot(indices, num_classes):
    X = np.zeros((len(indices), num_classes))
    X[np.arange(len(indices)), indices] = 1
    return X


class NpMLPRegressor:

    def __init__(self, input_dim, hidden_sizes=(64,), lr=0.01, max_iter=500):
        self.lr = lr
        self.max_iter = max_iter

        layer_sizes = [input_dim] + list(hidden_sizes) + [1]

        self.W = []
        self.b = []

        for i in range(len(layer_sizes)-1):
            self.W.append(np.random.randn(layer_sizes[i], layer_sizes[i+1]) * 0.1)
            self.b.append(np.zeros((1, layer_sizes[i+1])))

    def relu(self, x):
        return np.maximum(0, x)

    def relu_grad(self, x):
        return (x > 0).astype(float)

    def forward(self, X):
        a = X
        activations = [a]
        zs = []

        for i in range(len(self.W)-1):
            z = a @ self.W[i] + self.b[i]
            zs.append(z)
            a = self.relu(z)
            activations.append(a)

        z = a @ self.W[-1] + self.b[-1]
        zs.append(z)
        activations.append(z)

        return activations, zs

    def fit(self, X, y):
        y = y.reshape(-1,1)

        for epoch in range(self.max_iter):

            acts, zs = self.forward(X)
            y_pred = acts[-1]

            loss = np.mean((y_pred - y)**2)

            print("loss:", loss)

            # backprop
            grad = 2*(y_pred - y)/len(y)

            for i in reversed(range(len(self.W))):
                a_prev = acts[i]
                dW = a_prev.T @ grad
                db = grad.sum(axis=0, keepdims=True)

                if i > 0:
                    grad = grad @ self.W[i].T
                    grad *= self.relu_grad(zs[i-1])

                self.W[i] -= self.lr * dW
                self.b[i] -= self.lr * db

    def predict(self, X):
        a = X
        for i in range(len(self.W)-1):
            a = self.relu(a @ self.W[i] + self.b[i])
        return (a @ self.W[-1] + self.b[-1]).flatten()


load_dotenv()
CLIENT_ID = os.environ["CLIENT_ID"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

# -------------------------
# Supabase client
# -------------------------
def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================
# Recommender
# =========================
class GameRecommender:

    def __init__(self, hidden_layer_sizes=(64,), lr=0.01, max_iter=500):
        self.hidden_layer_sizes = hidden_layer_sizes
        self.lr = lr
        self.max_iter = max_iter

        self.user_enc = NpLabelEncoder()
        self.game_enc = NpLabelEncoder()
        self.genre_mlb = NpMultiLabelBinarizer()
        self.platform_mlb = NpMultiLabelBinarizer()


        self.user_ohe = None
        self.game_ohe = None

        self.model = None
        self.game_features = None
        self.feature_cols = None

    # -------------------------
    # Features
    # -------------------------
    def build_game_features(self, games: List[Dict]):
        genres = [g.get("genres", []) or [] for g in games]
        platforms = [g.get("platforms", []) or [] for g in games]

        genre_features = self.genre_mlb.fit_transform(genres)
        platform_features = self.platform_mlb.fit_transform(platforms)

        self.game_features = np.concatenate([genre_features, platform_features], axis=1)
        self.feature_cols = list(self.genre_mlb.classes_) + list(self.platform_mlb.classes_)

        game_ids = [g["id"] for g in games]
        self.game_enc.fit(game_ids)

    # -------------------------
    # Train
    # -------------------------
    def train(self, ratings):
        user_ids = [r["user_id"] for r in ratings]
        game_ids = [r["game_id"] for r in ratings]
        y = np.array([r["rating"] for r in ratings], dtype=float)

        u_idx = self.user_enc.fit_transform(user_ids)
        g_idx = self.game_enc.fit_transform(game_ids)

        X_user = one_hot(u_idx, len(self.user_enc.classes_))
        X_game = one_hot(g_idx, len(self.game_enc.classes_))

        X_game_feat = self.game_features[g_idx]

        X = np.concatenate([X_user, X_game, X_game_feat], axis=1)

        self.model = NpMLPRegressor(
            input_dim=X.shape[1],
            hidden_sizes=self.hidden_layer_sizes,
            lr=self.lr,
            max_iter=self.max_iter
        )

        self.model.fit(X, y)

        print("✅ model trained numpy")


    # -------------------------
    # Save bundle → Supabase
    # -------------------------
    def save_to_supabase(self, remote_path="reco_model.joblib"):
        if self.model is None:
            raise ValueError("Model has not been trained yet.")

        bundle = {
            "model": self.model,
            "user_enc": self.user_enc,
            "game_enc": self.game_enc,
            "user_ohe": self.user_ohe,
            "game_ohe": self.game_ohe,
            "genre_mlb": self.genre_mlb,
            "platform_mlb": self.platform_mlb,
            "feature_cols": self.feature_cols,
            "game_features": self.game_features,
        }

        buffer = io.BytesIO()
        joblib.dump(bundle, buffer)
        buffer.seek(0)

        sb = get_supabase_client()
        sb.storage.from_("models").upload(
            remote_path,
            buffer.getvalue(),
            {"content-type": "application/octet-stream", "upsert": "true"},
        )
        print("✅ Model uploaded to Supabase")


# =========================
# IGDB helper
# =========================
class Game(BaseModel):
    id: int
    genres: Optional[List[Union[int, str]]] = []
    platforms: Optional[List[Union[int, str]]] = []

def get_game_from_igdb(game_id: int) -> Game:
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "text/plain"
    }
    body = f"fields name, genres, platforms, storyline, cover.url; where id = {game_id};"
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()
    data = response.json()
    if not data:
        raise ValueError(f"Game {game_id} not found in IGDB")
    g = data[0]
    return Game(
        id=game_id,
        genres=g.get("genres", []),
        platforms=g.get("platforms", [])
    )
