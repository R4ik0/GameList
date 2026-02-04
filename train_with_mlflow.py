import mlflow
import mlflow.pyfunc
from game_recommender import GameRecommender, get_game_from_igdb, get_supabase_client
from dotenv import load_dotenv
import joblib

load_dotenv()

class NumpyRecommenderWrapper(mlflow.pyfunc.PythonModel):

    def load_context(self, context):
        import joblib
        self.model = joblib.load(context.artifacts["model"])

    def predict(self, context, model_input):
        return self.model.predict(model_input)

# -------------------------
# MLflow config
# -------------------------
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("game_recommender")

# -------------------------
# Supabase client
# -------------------------
supabase = get_supabase_client()

# -------------------------
# 1 Récupérer tous les utilisateurs avec leur gamelist
# -------------------------
res = supabase.table("users").select("id, gamelist").execute()
users = res.data if res.data else []

# -------------------------
# 2 Générer la liste de ratings globale
# -------------------------
ratings = []
for user in users:
    for game_id, rating in (user.get("gamelist") or {}).items():
        ratings.append({
            "user_id": user["id"],
            "game_id": int(game_id),
            "rating": rating
        })

# -------------------------
# 3 Récupérer tous les IDs uniques de jeux notés
# -------------------------
game_ids = list({r["game_id"] for r in ratings})

# -------------------------
# 4 Récupérer les infos depuis IGDB
# -------------------------
games = []
for gid in game_ids:
    try:
        game_obj = get_game_from_igdb(gid)
        games.append({
            "id": game_obj.id,
            "genres": game_obj.genres,
            "platforms": game_obj.platforms
        })
    except Exception as e:
        print(f"⚠️ Erreur pour le jeu {gid}: {e}")

print(f"✅ Récupération des données terminée: {len(users)} utilisateurs, {len(ratings)} ratings, {len(games)} jeux.")

# -------------------------
# 5️⃣ Training + MLflow + Supabase
# -------------------------
with mlflow.start_run(run_name="reco_training"):

    rec = GameRecommender(
        hidden_layer_sizes=(64,),   # remplace emb_dim
        lr=0.01,
        max_iter=25                 # remplace epochs
    )

    # Construire les features des jeux
    rec.build_game_features(games)

    # Entraîner le modèle avec les ratings
    rec.train(ratings)

    # -------------------------
    # MLflow logging
    # -------------------------
    mlflow.log_params({
        "hidden_layer_sizes": rec.hidden_layer_sizes,
        "learning_rate": rec.lr,
        "max_iter": rec.max_iter,
        "n_users": len(rec.user_enc.classes_),
        "n_games": len(rec.game_enc.classes_),
        "n_features": rec.game_features.shape[1]
    })

    # log sklearn model
    joblib.dump(rec.model, "model.joblib")

    mlflow.pyfunc.log_model(
        artifact_path="model",
        python_model=NumpyRecommenderWrapper(),
        artifacts={"model": "model.joblib"}
    )

    # tags
    mlflow.set_tags({
        "type": "game_recommender",
        "arch": "user+game+features",
        "backend": "numpy"
    })

    # -------------------------
    # Export PROD → Supabase
    # -------------------------
    rec.save_to_supabase("reco_model.joblib")

    print("✅ Training + MLflow + Supabase OK")
