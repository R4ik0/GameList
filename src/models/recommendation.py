import os
import io
import joblib
import torch
import torch.nn as nn
from sklearn.preprocessing import LabelEncoder
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()


### Model

class RatingModel(nn.Module):
    def __init__(self, n_users, n_games, n_features, emb_dim=32):
        super().__init__()

        self.user_emb = nn.Embedding(n_users, emb_dim)
        self.game_emb = nn.Embedding(n_games, emb_dim)
        self.feature_layer = nn.Linear(n_features, emb_dim)

        self.fc = nn.Sequential(
            nn.Linear(emb_dim * 3, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, u, g, f):
        x = torch.cat([
            self.user_emb(u),
            self.game_emb(g),
            self.feature_layer(f)
        ], dim=1)
        return self.fc(x)



### Recommender (Inference only)

class GameRecommender:

    def __init__(self):
        self.emb_dim = None
        self.user_enc = None
        self.game_enc = None
        self.game_feature_tensor = None
        self.model = None


    ## Supabase client

    def _supabase(self):
        return create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_KEY"]
        )


    ## Load bundle ← Supabase

    def load_from_supabase(self, remote_path="recommender_bundle.joblib"):

        sb = self._supabase()
        data = sb.storage.from_("models").download(remote_path)

        bundle = joblib.load(io.BytesIO(data))

        self.emb_dim = bundle["emb_dim"]
        self.user_enc = bundle["user_enc"]
        self.game_enc = bundle["game_enc"]

        self.game_feature_tensor = torch.tensor(
            bundle["game_features"],
            dtype=torch.float32
        )

        self.model = RatingModel(
            len(self.user_enc.classes_),
            len(self.game_enc.classes_),
            self.game_feature_tensor.shape[1],
            self.emb_dim
        )

        self.model.load_state_dict(bundle["state_dict"])
        self.model.eval()

        print("model loaded from supabase")


    ## Recommend

    def recommend_from_candidates(self, user_id, candidate_game_ids, top_k=10):

        if user_id not in self.user_enc.classes_:
            raise ValueError("Unknown user_id")

        self.model.eval()

        u_idx = torch.tensor([self.user_enc.transform([user_id])[0]])

        results = []

        for gid in candidate_game_ids:
            if gid not in self.game_enc.classes_:
                continue

            g_idx = torch.tensor([self.game_enc.transform([gid])[0]])
            f = self.game_feature_tensor[g_idx]

            with torch.no_grad():
                score = self.model(u_idx, g_idx, f).item()

            results.append((gid, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
