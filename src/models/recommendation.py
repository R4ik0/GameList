import os
import io
import joblib
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from supabase import create_client
from dotenv import load_dotenv
from src.models.game import get_game_from_igdb
import numpy as np


load_dotenv()


### Recommender (Inference only)

class GameRecommender:

    def init(self, hidden_layer_sizes=(64,), lr=0.01, max_iter=500):
            self.hidden_layer_sizes = hidden_layer_sizes
            self.lr = lr
            self.max_iter = max_iter

            self.user_enc = LabelEncoder()
            self.game_enc = LabelEncoder()
            self.genre_mlb = MultiLabelBinarizer()
            self.platform_mlb = MultiLabelBinarizer()

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
            u_idx = self.user_enc.transform([user_id]).reshape(-1,1)
            X_user = self.user_ohe.transform(u_idx)
        except ValueError:
            print(f"User {user_id} not found in the model.")
            return []

        results = []

        for gid in candidate_game_ids:
            if gid in self.game_enc.classes_:
                g_idx = self.game_enc.transform([gid]).reshape(-1,1)
                X_game = self.game_ohe.transform(g_idx)
                f_feat = self.game_features[g_idx.flatten()]
            else:
                X_game = np.zeros((1, len(self.game_enc.classes_)))
                
                try:
                    g = get_game_from_igdb(gid)
                    genres = g.genres
                    platforms = g.platforms
                except Exception as e:
                    print(f"Erreur IGDB pour le jeu {gid}: {e}")
                    genres, platforms = [], []

                genre_vec = self.genre_mlb.transform([genres]) if hasattr(self.genre_mlb, "classes_") else np.zeros((1, 0))
                platform_vec = self.platform_mlb.transform([platforms]) if hasattr(self.platform_mlb, "classes_") else np.zeros((1, 0))

                f_feat = np.concatenate([genre_vec, platform_vec], axis=1)

                expected_dim = self.game_features.shape[1]
                if f_feat.shape[1] < expected_dim:
                    pad = np.zeros((1, expected_dim - f_feat.shape[1]))
                    f_feat = np.concatenate([f_feat, pad], axis=1)

            X_pred = np.concatenate([X_user, X_game, f_feat], axis=1)
            score = self.model.predict(X_pred)[0]
            results.append((gid, score))

        results.sort(key=lambda x: x[1], reverse=True)
        print(results[:top_k])
        return results[:top_k]