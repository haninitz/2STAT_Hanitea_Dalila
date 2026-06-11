# 🌍Analyse des Gaz à Effet de Serre (NOAA)

Ce projet a pour objectif d'analyser l'évolution des concentrations atmosphériques de quatre gaz à effet de serre à partir des données du **NOAA Global Monitoring Laboratory**. Il inclut une décomposition saisonnière additive et multiplicative, une estimation de la tendance, ainsi que des prévisions pour les mois à venir.

**Étudiantes :** Hanitea RENETEAUD / Dalila CHEKKOUMY  


---

## 📁 Structure du projet

```
.
├── data/
│   ├── ch4_mm_gl.csv       # Méthane (CH₄) — moyennes globales
│   ├── co2_mm_mlo.csv      # Dioxyde de carbone (CO₂) — Mauna Loa
│   ├── n2o_mm_gl.csv       # Protoxyde d'azote (N₂O) — moyennes globales
│   └── sf6_mm_gl.csv       # Hexafluorure de soufre (SF₆) — moyennes globales
└── 2STAT_Projet.ipynb      # Notebook principal avec toutes les étapes de l'analyse
```

---

## 📊 Objectifs de l'analyse

* Charger et décrire les jeux de données (période, observations, unités).
* Identifier les gaz présentant des **variations saisonnières** marquées.
* Décomposer les séries temporelles en composantes : **tendance**, **saisonnalité**, **résidu**.
* Comparer les modèles de décomposition **additif** et **multiplicatif**.
* Utiliser des **régressions linéaires** et **exponentielles** pour modéliser la tendance.
* Réaliser des **prévisions sur 24 mois** 
* Interpréter les phénomènes saisonniers et les tendances de fond.

---

## 🧩 Dépendances Python

Avant de lancer le projet, installe les bibliothèques nécessaires avec `pip` :

```bash
pip install pandas numpy matplotlib scipy
```

### 📦 Librairies utilisées

* **pandas** : manipulation et nettoyage des données
* **numpy** : calculs numériques (moyennes mobiles, régressions)
* **matplotlib** : visualisations (nuages de points, tendances, prévisions)
* **scipy** : régression linéaire via `scipy.stats.linregress`

---

## 🚀 Lancement du projet

1. Clone ou télécharge le dépôt.
2. Lance `2STAT_Projet.ipynb` avec VS Code, JupyterLab ou Jupyter Notebook.
3. Exécute les cellules dans l'ordre pour :
   * Charger et nettoyer les données
   * Visualiser les séries temporelles
   * Appliquer les décompositions saisonnières
   * Calculer les régressions et générer les prévisions

---

## 🧠 Résultats attendus

* Identification des gaz avec saisonnalité (**CH₄, CO₂**) et sans (**N₂O, SF₆**).
* Extraction de la tendance de fond via la **moyenne mobile d'ordre 6**.
* Coefficients mensuels corrigés représentant la signature saisonnière de chaque mois.
* Prévisions réalistes sur les 2 prochaines années pour chaque gaz.
* Comparaison des modèles linéaires et exponentiels avec discussion du plus pertinent.

---

## 📌 À savoir

* Les fichiers NOAA contiennent des lignes de commentaires préfixées par `#` — elles sont ignorées au chargement via `pd.read_csv(..., comment='#')`.
* Les valeurs manquantes sont codées `-999.99` et remplacées par `NaN` avant analyse.
* La **moyenne mobile centrée d'ordre 6** est utilisée pour lisser la tendance : elle n'est pas calculable pour les **3 premiers et 3 derniers mois** de chaque série.
* Le choix entre modèle additif et multiplicatif dépend de la stabilité de l'amplitude saisonnière au fil du temps.
