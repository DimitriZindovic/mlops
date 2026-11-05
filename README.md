# Sujet E – Online Shoppers Purchasing Intention

Membres : Dimitri Zindovic, Aurore Dimech

Prédire si une session de navigation sur un site marchand se termine par un achat, et faire passer ce modèle
du notebook à la production sur Azure Machine Learning. Tout le code est dans `Online_Shoppers_Intention.ipynb`.

## Les étapes en bref

1. **Exploration** : lecture du CSV UCI, taille, cible, proportion des classes, valeurs manquantes.
2. **Data asset** `online_shoppers_intention` : v1 = CSV brut ; v2 = booléens en 0/1, `Month` et `VisitorType` encodées avec `get_dummies` (bonus de la fiche E) au lieu d'être retirées.
3. **Job d'entraînement** : `train.py` adapté (cible `revenue`), testé en local puis lancé sur le cluster. Des `assert` vérifient les données, le code et les ressources Azure avant la soumission.
4. **MLflow** : paramètres, métriques et modèle avec signature enregistrés ; 2 runs comparés (`none` / `balanced`).
5. **Pipeline** `prep` → `train` : nettoyage (`dropna`, `drop_duplicates`), puis entraînement ; le modèle `intention-model` n'est enregistré que si le recall atteint le seuil (tag `validation`).
6. **Déploiement** : endpoint `intention-ep-dimitri-…`, déploiement `blue` (Standard_F2s_v2), 100 % du trafic. `score.py` est d'abord testé en local avec le vrai modèle (`assert`), puis l'endpoint est testé dans le studio, en Python et avec une requête incorrecte.
7. **Nettoyage** : suppression de l'endpoint après la soutenance, cluster à 0 nœud minimum.

## Données

12 330 sessions, 18 colonnes, aucune valeur manquante. Cible `Revenue` : **85 %** sans achat (10 422), **15 %** avec achat (1 908).

## Métrique choisie et seuil : recall ≥ 0,7

- La classe qui compte est l'**achat**, rare (15 %). Le recall mesure la part des acheteurs réels détectés.
- Rater un acheteur (faux négatif) fait perdre une vente ou une action ciblée ; signaler à tort un non-acheteur (faux positif) coûte peu.
- L'accuracy est trompeuse : un modèle qui répond toujours « pas d'achat » a 85 % d'accuracy et un recall nul.
- Seuil **0,7** : `balanced` l'atteint (≈ 0,75) et `none` en est loin (≈ 0,36). Le seuil impose donc la pondération des classes tout en gardant une marge.

## Résultats

| Run                          | class_weight | test_size | accuracy | precision | recall    | f1    | auc   |
| ---------------------------- | ------------ | --------- | -------- | --------- | --------- | ----- | ----- |
| intention-mlflow-none-20     | none         | 0,2       | 0,881    | 0,743     | 0,356     | 0,481 | 0,887 |
| intention-mlflow-balanced-30 | balanced     | 0,3       | 0,853    | 0,517     | **0,748** | 0,611 | 0,900 |
| Pipeline (prep + train)      | balanced     | 0,3       | –        | –         | ≥ 0,7     | –     | –     |

`balanced` double le recall au prix d'une précision plus basse : c'est le compromis voulu. Chaque exécution du pipeline a validé le modèle : `intention-model` a deux versions, et la version 1 est celle déployée sur l'endpoint.

## Preuves (dossier `captures/`)

| Étape | Capture |
| --- | --- |
| 2 – Data asset | [02_data_asset.png](captures/02_data_asset.png) : `online_shoppers_intention`, versions 1 et 2, description |
| 3 – Job | [03_jobs_completed.png](captures/03_jobs_completed.png) : `intention-logreg-baseline` et les autres jobs à l'état Completed |
| 4 – MLflow | [04_comparaison_runs.png](captures/04_comparaison_runs.png) : comparaison `balanced-30` / `none-20` (paramètres et métriques) |
| 4 – MLflow | [04_run_modele_signature.png](captures/04_run_modele_signature.png) : modèle enregistré dans le run, fichier `MLmodel` avec sa signature |
| 5 – Pipeline | [05_pipeline_graphe.png](captures/05_pipeline_graphe.png) : graphe data → prep → train terminé |
| 5 – Pipeline | [05_modele_versions.png](captures/05_modele_versions.png) : `intention-model` versions 1 et 2 issues du pipeline |
| 6 – Déploiement | [06_endpoint_details.png](captures/06_endpoint_details.png) : endpoint Succeeded, `blue` à 100 %, Standard_F2s_v2 |
| 6 – Déploiement | [06_test_studio.png](captures/06_test_studio.png) : onglet Test, prédictions `[0, 0, 1]` |
| 6 – Déploiement | [06_test_python_http.png](captures/06_test_python_http.png) : appel HTTP en Python, code 200 |
| 6 – Déploiement | [06_requete_incorrecte.png](captures/06_requete_incorrecte.png) : requête avec une seule colonne, erreur listant les 27 colonnes manquantes |
