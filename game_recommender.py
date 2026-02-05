import os
import io
import joblib
from supabase import create_client
from dotenv import load_dotenv
from src.models.game import get_game_from_igdb, create_game_in_bdd
import numpy as np


load_dotenv()



### Fonctions au préalable

def one_hot(indices, num_classes):
    X = np.zeros((len(indices), num_classes))
    X[np.arange(len(indices)), indices] = 1
    return X

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

            if epoch % 50 == 0:
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


### Recommender (Inference only)

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


    ## Supabase client

    def _supabase(self):
        return create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_KEY"]
        )


    ## Load bundle ← Supabase

    def load_from_supabase(self, remote_path="reco_model.joblib"):
        sb = self._supabase()
        data = sb.storage.from_("models").download(remote_path)
        bundle = joblib.load(io.BytesIO(data))

        self.model = bundle["model"]
        self.user_enc = bundle["user_enc"]
        self.game_enc = bundle["game_enc"]
        self.user_ohe = bundle["user_ohe"]
        self.game_ohe = bundle["game_ohe"]
        self.genre_mlb = bundle["genre_mlb"]
        self.platform_mlb = bundle["platform_mlb"]
        self.feature_cols = bundle["feature_cols"]
        self.game_features = bundle["game_features"]

        print("model loaded from supabase")


    ## Recommend

    def recommend_from_candidates(self, user_id, candidate_game_ids, top_k=10):
        if self.model is None:
            raise ValueError("Model has not been trained or loaded.")

        # Transformer l'utilisateur
        try:
            u_idx = self.user_enc.transform([user_id])
            X_user = one_hot(u_idx, len(self.user_enc.classes_))

        except ValueError:
            print(f"User {user_id} not found in the model.")
            return []

        results = []

        for gid in candidate_game_ids:
            if gid in self.game_enc.classes_:
                g_idx = self.game_enc.transform([gid])
                X_game = one_hot(g_idx, len(self.game_enc.classes_))
                f_feat = self.game_features[g_idx]

            else:
                X_game = np.zeros((1, len(self.game_enc.classes_)))
                
                try:
                    g = get_game_from_igdb(gid)
                    genres = g.genres
                    platforms = g.platforms
                except Exception as e:
                    print(f"Erreur IGDB pour le jeu {gid}: {e}")
                    genres, platforms = [], []

                genre_vec = self.genre_mlb.transform([genres])
                platform_vec = self.platform_mlb.transform([platforms])


                f_feat = np.concatenate([genre_vec, platform_vec], axis=1)

                expected_dim = self.game_features.shape[1]
                if f_feat.shape[1] < expected_dim:
                    pad = np.zeros((1, expected_dim - f_feat.shape[1]))
                    f_feat = np.concatenate([f_feat, pad], axis=1)

            X_pred = np.concatenate([X_user, X_game, f_feat], axis=1)
            score = self.model.predict(X_pred)[0]
            results.append((gid, score))

        results.sort(key=lambda x: x[1], reverse=True)
        
        for gid, _ in results[:top_k]:
            create_game_in_bdd(gid)
        
        return results[:top_k]