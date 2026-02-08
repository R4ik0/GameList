# GameList --- Plateforme de recommandation de jeux vidéo

## Présentation du projet

GameList est une plateforme web de gestion et de recommandation de jeux
vidéo. Le site permet aux utilisateurs de rechercher des jeux, de leur
attribuer des notes, de consulter leur profil ainsi que celui des autres
utilisateurs, et d'obtenir des recommandations personnalisées en
fonction de leurs préférences. L'objectif du projet est de démontrer la
mise en place complète d'une application moderne avec un frontend
déployé, une API backend, une base de données distante, et une brique
d'intelligence artificielle pour la recommandation.

## Fonctionnalités principales

-   Le site permet de rechercher des jeux en temps réel grâce à l'API
    IGDB, avec affichage dynamique des résultats.
-   L'utilisateur peut attribuer une note aux jeux afin de construire
    son profil de préférences.
-   Une page de profil affiche les jeux notés par un utilisateur avec
    tri par note puis par ordre alphabétique.
-   Il est possible de consulter le profil d'un autre utilisateur via la
    recherche.
-   Le moteur de recommandation propose des jeux adaptés aux goûts de
    l'utilisateur lorsqu'il possède déjà des notes.
-   Si un utilisateur ne possède aucune note, le système affiche
    automatiquement les jeux les mieux notés globalement.
-   L'interface est responsive et s'adapte aux écrans ordinateur et
    mobile.
-   Une barre de recherche unifiée permet de rechercher à la fois des
    jeux et des utilisateurs avec deux sections de résultats distinctes.

## Comptes de démonstration

-   Le compte **user / userpass** permet de tester un utilisateur sans
    jeux notés ; aucune recommandation personnalisée n'est calculée et
    la page affiche les jeux les mieux notés.
-   Le compte **admin / adminpass** permet de tester un utilisateur avec
    des jeux déjà notés ; le moteur de recommandation est donc actif et
    affiche des suggestions personnalisées.

## Architecture technique

-   Le frontend est une interface web statique déployée sur GitHub
    Pages.
-   Le backend est une API développée en Python (FastAPI) et déployée
    sur Vercel.
-   La base de données est hébergée sur Supabase pour le stockage des
    utilisateurs, des notes et des métadonnées de jeux.
-   Les données jeux (noms, images, genres, plateformes) sont récupérées
    via l'API IGDB.
-   Le système de recommandation utilise un modèle de machine learning
    entraîné séparément.

## Machine Learning et expérimentation

-   Le modèle de recommandation a été entraîné et suivi avec MLflow en
    environnement local.
-   MLflow n'est pas exposé en production ; il est uniquement utilisé
    pour l'expérimentation et le suivi des runs.
-   Toute la partie IA et entraînement est accessible dans la branche
    dédiée **ia** du projet.

## Monitoring

-   Grafana est utilisé pour la visualisation des métriques et le suivi
    du comportement du système.
-   Les tableaux de bord permettent d'observer les mesures collectées
    pendant l'exécution.

## Déploiement

-   Frontend : https://r4ik0.github.io/GameList/
-   Backend : déployé sur Vercel
-   Base de données : Supabase
-   Suivi ML : MLflow en local (branche ia)
-   Monitoring : Grafana
