# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.3
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # 2STAT - Analyse de données temporelles des gaz à  effets de serre
#
# **Source des données :** Global Monitoring Laboratory  
# **Gaz étudiés :** CH₄ (méthane), CO₂ (dioxyde de carbone), N₂O (protoxyde d'azote), SF₆ (hexafluorure de soufre)
#
# **Étudiants :** Hanitea RENETEAUD / Dalila CHEKKOUMY

# %% [markdown]
# ---
# ## Question 1 — Exploration et description des jeux de données

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats
from IPython.display import display

plt.rcParams['figure.figsize'] = (12, 5)
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['font.size'] = 11

chemins = {
    'CH4': 'data/ch4_mm_gl.csv',
    'CO2': 'data/co2_mm_mlo.csv',
    'N2O': 'data/n2o_mm_gl.csv',
    'SF6': 'data/sf6_mm_gl.csv',
}

datasets_raw = {gaz: pd.read_csv(p, comment='#', skip_blank_lines=True)
                for gaz, p in chemins.items()}

# Harmonisation CO2
datasets_raw['CO2'].columns = [c.strip().lower() for c in datasets_raw['CO2'].columns]

df_ch4 = datasets_raw['CH4']
df_co2 = datasets_raw['CO2']
df_n2o = datasets_raw['N2O']
df_sf6 = datasets_raw['SF6']

for gaz, df in datasets_raw.items():
    df.columns = [c.strip().lower() for c in df.columns]
    print(f'=== {gaz} ===')
    print(f"  Colonnes     : {list(df.columns)}")
    print(f"  Observations : {len(df)}")
    print(f"  Période      : {int(df['year'].iloc[0])}-{int(df['month'].iloc[0]):02d} "
          f"→ {int(df['year'].iloc[-1])}-{int(df['month'].iloc[-1]):02d}")
    display(df.head(3))
    print()


# %% [markdown]
# **Interprétation :**
#
# Les quatre jeux de données proviennent du NOAA Global Monitoring Laboratory et contiennent des mesures mensuelles de concentration atmosphérique. Après chargement, on observe :
#
# - **CH₄** : environ **511** observations depuis **1983** (global)
# - **CO₂** : environ **818** observations depuis **1958** (Mauna Loa)
# - **N₂O** : environ **301** observations depuis **2001** (global)
# - **SF₆** : environ **343** observations depuis **1997** (global)
#
# Chaque fichier contient plusieurs colonnes dont `year`, `month`, `decimal`, `average`, `trend`. La valeur -999.99 indique une donnée manquante.

# %% [markdown]
# ---
# ## Question 2 — Nettoyage : conservation des variables `month` et `average`

# %%
def clean_dataset(df):
    df.columns = [c.strip().lower() for c in df.columns]
    df['average'] = df['average'].replace(-999.99, np.nan)
    df = df.dropna(subset=['average']).reset_index(drop=True)
    return df

df_ch4 = clean_dataset(df_ch4)
df_co2 = clean_dataset(df_co2)
df_n2o = clean_dataset(df_n2o)
df_sf6 = clean_dataset(df_sf6)

# datasets avec year conservé (utile pour Q9)
datasets_full = {'CH4': df_ch4, 'CO2': df_co2, 'N2O': df_n2o, 'SF6': df_sf6}
# datasets réduits à month + average pour les questions suivantes
datasets = {gaz: df[['month', 'average']].copy() for gaz, df in datasets_full.items()}

for name, df in datasets.items():
    print(f'{name} : {len(df)} observations | colonnes : {list(df.columns)}')
    display(df.head(4))
    print()


# %% [markdown]
# **Interprétation :**
#
# Après nettoyage, chaque dataset ne conserve que deux colonnes :
# - `month` : le **numéro du mois** (1 à 12), qui servira d'indice pour **identifier la saison**
# - `average` : la concentration moyenne mensuelle du gaz, exprimée dans l'unité correspondante
#
# Les valeurs manquantes codées -999.99 ont été remplacées par NaN puis supprimées. Les lignes restantes constituent la série temporelle complète de chaque gaz.

# %% [markdown]
# ---
# ## Question 3 — Présentation des gaz étudiés

# %% [markdown]
# ### CO₂ — Dioxyde de carbone
#
# | Propriété | Valeur |
# |---|---|
# | Formule chimique | CO₂ |
# | Concentration actuelle | ≈ 424 ppm (2024) |
# | Unité de mesure | ppm (parties par million en volume) |
# | Pouvoir de réchauffement global (PRG) | référence = 1 |
# | Durée de vie atmosphérique | des siècles |
#
# **Sources :** combustion de carburants fossiles (charbon, pétrole, gaz naturel), déforestation, production de ciment.  
# **Effets sur l'atmosphère :** principal gaz à effet de serre d'origine anthropique. Il absorbe le rayonnement infrarouge émis par la Terre et le réémet vers la surface, contribuant au réchauffement climatique. Les mesures de Mauna Loa (Hawaii) depuis 1958 constituent la série historique la plus emblématique du suivi du climat.
#
# ---
#
# ### CH₄ — Méthane
#
# | Propriété | Valeur |
# |---|---|
# | Formule chimique | CH₄ |
# | Concentration actuelle | ≈ 1910 ppb (2024) |
# | Unité de mesure | ppb (parties par milliard en volume) |
# | PRG sur 100 ans | ≈ 28× le CO₂ |
# | Durée de vie atmosphérique | ≈ 12 ans |
#
# **Sources :** élevage bovin (fermentation entérique), riziculture, décharges, exploitation du gaz naturel et du charbon.  
# **Effets sur l'atmosphère :** gaz à effet de serre très puissant à court terme. Il participe également à la formation d'ozone troposphérique, un polluant. Sa durée de vie plus courte que le CO₂ signifie que réduire ses émissions aurait un effet climatique relativement rapide.
#
# ---
#
# ### N₂O — Protoxyde d'azote
#
# | Propriété | Valeur |
# |---|---|
# | Formule chimique | N₂O |
# | Concentration actuelle | ≈ 336 ppb (2024) |
# | Unité de mesure | ppb |
# | PRG sur 100 ans | ≈ 265× le CO₂ |
# | Durée de vie atmosphérique | ≈ 114 ans |
#
# **Sources :** utilisation d'engrais azotés en agriculture, élevage, certains procédés industriels (fabrication d'acide nitrique).  
# **Effets sur l'atmosphère :** puissant gaz à effet de serre et principal destructeur de la couche d'ozone stratosphérique aujourd'hui. Sa longue durée de vie le rend particulièrement préoccupant sur le long terme.
#
# ---
#
# ### SF₆ — Hexafluorure de soufre
#
# | Propriété | Valeur |
# |---|---|
# | Formule chimique | SF₆ |
# | Concentration actuelle | ≈ 11 ppt (2024) |
# | Unité de mesure | ppt (parties par trillion en volume) |
# | PRG sur 100 ans | ≈ 23 500× le CO₂ |
# | Durée de vie atmosphérique | ≈ 3 200 ans |
#
# **Sources :** industrie électrique (isolation des disjoncteurs à haute tension), fabrication de semi-conducteurs, production de magnésium.  
# **Effets sur l'atmosphère :** gaz à effet de serre le plus puissant connu. Bien que sa concentration soit infime comparée au CO₂, son PRG extraordinaire et sa durée de vie quasi-permanente en font une menace climatique à très long terme. Ses émissions sont entièrement d'origine industrielle.

# %% [markdown]
# ---
# ## Question 4 — Nuages de points

# %%
units = {'CH4': 'ppb', 'CO2': 'ppm', 'N2O': 'ppb', 'SF6': 'ppt'}
colors = {'CH4': '#e74c3c', 'CO2': '#3498db', 'N2O': '#2ecc71', 'SF6': '#9b59b6'}

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
axes = axes.flatten()

for i, (name, df) in enumerate(datasets.items()):
    ax = axes[i]
    ax.scatter(df.index, df['average'], s=4, alpha=0.7, color=colors[name])
    ax.set_title(f'{name} — Concentration atmosphérique', fontweight='bold')
    ax.set_xlabel('Indice observation temporel (mois)')
    ax.set_ylabel(f'Concentration ({units[name]})')

plt.suptitle('Évolution des concentrations de gaz à effet de serre', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()


# %% [markdown]
# **Interprétation :**
#
# Les quatre graphiques révèlent deux comportements distincts :
#
# **Gaz avec variations saisonnières marquées — CH₄ et CO₂ :**  
# On observe clairement des oscillations régulières et répétées autour de la tendance générale. Ces ondulations correspondent à des hausses et baisses qui se reproduisent chaque année au même moment, ce qui est la signature d'un phénomène saisonnier. La tendance à long terme est néanmoins nettement croissante.
#
# **Gaz sans variations saisonnières — N₂O et SF₆ :**  
# La courbe est quasi-monotone et lisse, sans oscillations visibles à l'œil nu. La concentration augmente de façon régulière d'année en année, ce qui suggère une croissance continue liée aux activités industrielles et agricoles, sans influence saisonnière notable.
#
# **Les deux gaz présentant clairement des variations saisonnières sont donc CH₄ et CO₂.**

# %% [markdown]
# ---
# ## Question 5 — Décomposition additive (CH₄ et CO₂)

# %%
def decomposition_additive(df, name, unit):
    x = df['average'].values
    n = len(x)
    T = np.arange(n)
    mois = df['month'].values

    # 5.1 Moyenne mobile d'ordre 6
    x_star = np.full(n, np.nan)
    for t in range(3, n - 3):
        x_star[t] = (0.5*x[t-3] + x[t-2] + x[t-1]
                     + x[t] + x[t+1] + x[t+2]
                     + 0.5*x[t+3]) / 6

    # 5.2 Résidus saisonniers
    S = x - x_star

    # 5.3 Coefficients mensuels bruts
    c = np.zeros(12)
    for j in range(1, 13):
        vals = S[mois == j]
        vals = vals[~np.isnan(vals)]
        c[j-1] = np.mean(vals)

    # 5.4 Coefficients corrigés
    c_bar = np.mean(c)
    c_prime = c - c_bar

    mois_noms = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
    print(f'\n=== {name} — Coefficients mensuels corrigés ===')
    for nom, cp in zip(mois_noms, c_prime):
        print(f'  {nom} : {cp:+.4f} {unit}')
    print(f'  Somme : {c_prime.sum():.6f}')

    # 5.5 Série désaisonnalisée
    x_desais = np.array([x[t] - c_prime[mois[t]-1] for t in range(n)])

    # 5.6 Régression linéaire
    slope, intercept, r, p, se = stats.linregress(T, x_desais)
    trend = intercept + slope * T
    print(f'\n  Tendance : y = {intercept:.4f} + {slope:.6f}·t   R² = {r**2:.4f}')

    # 5.7 Prévisions 24 mois
    T_prev = np.arange(n, n + 24)
    mois_prev = np.array([(mois[-1] + i - 1) % 12 + 1 for i in range(1, 25)])
    prev = (intercept + slope * T_prev) + c_prime[mois_prev - 1]

    # Graphiques
    fig, axes = plt.subplots(3, 1, figsize=(14, 14))

    axes[0].scatter(T, x, s=4, color='steelblue', alpha=0.6, label='Données brutes')
    axes[0].plot(T, x_star, color='red', lw=2, label='Série lissée (MM6)')
    axes[0].set_title(f'{name} — Série originale et moyenne mobile')
    axes[0].set_ylabel(f'({unit})'); axes[0].legend()

    axes[1].scatter(T, x_desais, s=4, color='green', alpha=0.6, label='Désaisonnalisée')
    axes[1].plot(T, trend, color='orange', lw=2, label=f'Tendance R²={r**2:.3f}')
    axes[1].set_title(f'{name} — Série désaisonnalisée et tendance')
    axes[1].set_ylabel(f'({unit})'); axes[1].legend()

    axes[2].scatter(T, x, s=4, color='steelblue', alpha=0.5, label='Historique')
    axes[2].scatter(T_prev, prev, s=20, color='red', zorder=5, label='Prévisions')
    axes[2].plot(T_prev, prev, '--', color='red', alpha=0.7)
    axes[2].set_title(f'{name} — Prévisions 24 mois')
    axes[2].set_ylabel(f'({unit})'); axes[2].set_xlabel('Indice'); axes[2].legend()

    plt.suptitle(f'{name} — Décomposition additive', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

    return x_star, c_prime, x_desais, trend, slope, intercept

res_ch4_add = decomposition_additive(df_ch4, 'CH4', 'ppb')
res_co2_add = decomposition_additive(df_co2, 'CO2', 'ppm')


# %% [markdown]
# **Interprétation — Question 5 :**
#
# **5.1 — Moyenne mobile :**  
# La moyenne mobile d'ordre 12 ne peut pas être calculée pour les 6 premiers et les 6 derniers mois de la série, car la formule nécessite 6 voisins de chaque côté. Cette série lissée représente la tendance de fond : en moyennant sur 12 mois consécutifs, on efface les effets saisonniers et on ne garde que l'évolution lente à long terme. On parle de "série lissée" car les oscillations sont atténuées.
#
# **5.2 — Résidus saisonniers :**  
# La série Sₜ = xₜ − x*ₜ représente ce qui reste une fois la tendance retirée, c'est-à-dire l'effet pur de la saison sur chaque mois. Un Sₜ positif signifie que ce mois-là est au-dessus de la tendance, négatif qu'il est en dessous.
#
# **5.3-5.4 — Coefficients mensuels corrigés :**  
# Les coefficients c'ⱼ donnent la "signature" de chaque mois de l'année. Par exemple, un coefficient positif en hiver pour le CO₂ signifie que la concentration est systématiquement plus haute en hiver qu'en été. La correction (soustraction de la moyenne) garantit que la somme des 12 coefficients est exactement zéro, ce qui est nécessaire pour la cohérence du modèle additif.
#
# **5.5 — Série désaisonnalisée :**  
# En soustrayant le coefficient mensuel corrigé correspondant à chaque observation, on obtient une série dont les variations saisonnières ont été supprimées. Cette série ne montre plus que la tendance longue et les fluctuations aléatoires.
#
# **5.6 — Tendance (trend) :**  
# La droite de régression calculée sur la série désaisonnalisée représente la croissance structurelle à long terme des concentrations. Sa pente indique l'augmentation moyenne par mois en dehors de tout effet saisonnier. Un R² proche de 1 confirme que cette croissance est très régulière.
#
# **5.7 — Prévisions :**  
# Pour chaque mois futur, on additionne la valeur de la tendance à ce mois (extrapolation de la droite) et le coefficient saisonnier corrigé du mois correspondant. Cette méthode suppose que la tendance de fond et les effets saisonniers restent stables dans les deux prochaines années.
#
# **5.8 — Causes des variations saisonnières :**  
# Pour le CO₂ : les oscillations sont principalement dues à la photosynthèse de la végétation de l'hémisphère Nord. Au printemps et en été, les plantes absorbent massivement du CO₂, ce qui fait baisser la concentration. En automne et en hiver, la respiration et la décomposition de la matière organique dominent, ce qui la fait remonter.  
# Pour le CH₄ : les variations saisonnières sont liées à l'activité des zones humides (plus forte en été), aux réactions chimiques atmosphériques (les radicaux OH qui détruisent le méthane sont plus actifs en été) et aux émissions de combustion plus importantes en hiver.

# %% [markdown]
# ---
# ## Question 6 — Décomposition multiplicative (CH₄ et CO₂)

# %%
def decomposition_multiplicative(df, name, unit):
    x = df['average'].values
    n = len(x)
    T = np.arange(n)
    mois = df['month'].values

    x_star = np.full(n, np.nan)
    for t in range(3, n - 3):
        x_star[t] = (0.5*x[t-3] + x[t-2] + x[t-1]
                     + x[t] + x[t+1] + x[t+2]
                     + 0.5*x[t+3]) / 6

    S = x / x_star

    c = np.zeros(12)
    for j in range(1, 13):
        vals = S[mois == j]
        vals = vals[~np.isnan(vals)]
        c[j-1] = np.mean(vals)

    c_bar = np.mean(c)
    c_prime = c / c_bar

    mois_noms = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
    print(f'\n=== {name} — Coefficients mensuels corrigés (multiplicatif) ===')
    for nom, cp in zip(mois_noms, c_prime):
        print(f'  {nom} : {cp:.6f}')
    print(f'  Moyenne : {c_prime.mean():.6f}')

    x_desais = np.array([x[t] / c_prime[mois[t]-1] for t in range(n)])

    slope, intercept, r, p, se = stats.linregress(T, x_desais)
    trend = intercept + slope * T
    print(f'\n  Tendance : y = {intercept:.4f} + {slope:.6f}·t   R² = {r**2:.4f}')

    T_prev = np.arange(n, n + 24)
    mois_prev = np.array([(mois[-1] + i - 1) % 12 + 1 for i in range(1, 25)])
    prev = (intercept + slope * T_prev) * c_prime[mois_prev - 1]

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    axes[0].scatter(T, x_desais, s=4, color='darkorange', alpha=0.6, label='Désaisonnalisée')
    axes[0].plot(T, trend, color='navy', lw=2, label=f'Tendance R²={r**2:.3f}')
    axes[0].set_title(f'{name} — Désaisonnalisée et tendance (multiplicatif)')
    axes[0].set_ylabel(f'({unit})'); axes[0].legend()

    axes[1].scatter(T, x, s=4, color='steelblue', alpha=0.5, label='Historique')
    axes[1].scatter(T_prev, prev, s=20, color='red', zorder=5, label='Prévisions')
    axes[1].plot(T_prev, prev, '--', color='red', alpha=0.7)
    axes[1].set_title(f'{name} — Prévisions (multiplicatif)')
    axes[1].set_ylabel(f'({unit})'); axes[1].set_xlabel('Indice'); axes[1].legend()

    plt.suptitle(f'{name} — Décomposition multiplicative', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()

res_ch4_mul = decomposition_multiplicative(df_ch4, 'CH4', 'ppb')
res_co2_mul = decomposition_multiplicative(df_co2, 'CO2', 'ppm')

# %% [markdown]
# **Interprétation — Question 6 :**
#
# **6.2 — Série quotient :**  
# La série Sₜ = Xₜ / X*ₜ représente le rapport entre la valeur observée et la tendance lissée. Une valeur supérieure à 1 indique que ce mois est au-dessus de la tendance, une valeur inférieure à 1 qu'il est en dessous. Contrairement au modèle additif où l'écart était exprimé en unités absolues, ici il est exprimé en proportion.
#
# **6.4 — Coefficients corrigés :**  
# Les coefficients c'ⱼ sont obtenus en divisant chaque coefficient mensuel par leur moyenne. Leur moyenne vaut donc exactement 1 par construction. Un coefficient de 1.02 signifie que ce mois est en moyenne 2% au-dessus de la tendance de fond.
#
# **6.5 — Série désaisonnalisée :**  
# On divise les données initiales par le coefficient du mois correspondant. On obtient une série ne montrant plus que la tendance, libérée de l'effet saisonnier.
#
# **6.7 — Prévisions :**  
# Pour chaque mois futur, on multiplie la valeur de la tendance par le coefficient mensuel corrigé. Ce modèle suppose que l'amplitude saisonnière évolue proportionnellement à la tendance.

# %% [markdown]
# ---
# ## Question 7 — Comparaison additive vs multiplicative

# %%
for name, df in [('CH4', df_ch4), ('CO2', df_co2)]:
    x = df['average'].values
    n = len(x)
    x_star = np.full(n, np.nan)
    for t in range(3, n-3):
        x_star[t] = (0.5*x[t-3]+x[t-2]+x[t-1]
                     +x[t]+x[t+1]+x[t+2]+0.5*x[t+3])/6

    S_add = x - x_star
    S_mul = x / x_star

    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    axes[0].plot(S_add, color='steelblue', lw=0.8, alpha=0.8)
    axes[0].set_title(f'{name} — Résidus additifs')
    axes[0].set_ylabel('xₜ − x*ₜ')
    axes[1].plot(S_mul, color='darkorange', lw=0.8, alpha=0.8)
    axes[1].set_title(f'{name} — Résidus multiplicatifs')
    axes[1].set_ylabel('xₜ / x*ₜ')
    plt.suptitle(f'{name} — Comparaison résidus', fontweight='bold')
    plt.tight_layout()
    plt.show()


# %% [markdown]
# **Interprétation — Question 7 :**
#
# Pour choisir entre les deux modèles, on observe si l'amplitude des résidus saisonniers est stable ou croissante au cours du temps :
#
# - Si l'amplitude est **constante** → le modèle **additif** est le plus pertinent, car l'effet saisonnier s'ajoute à la tendance avec une valeur fixe chaque année.
# - Si l'amplitude **augmente proportionnellement** à la tendance → le modèle **multiplicatif** est préférable, car l'effet saisonnier représente alors un pourcentage constant de la valeur.
#
# Dans notre cas, l'amplitude des oscillations saisonnières du CO₂ et du CH₄ est **relativement stable** sur l'ensemble de la période. Le modèle **additif** est donc le plus adapté ici. Il présente également l'avantage d'être plus simple à interpréter : les coefficients mensuels sont directement exprimés dans l'unité du gaz (ppm ou ppb), ce qui leur donne une signification physique immédiate.

# %% [markdown]
# ---
# ## Question 8 — Régression linéaire et exponentielle (N₂O et SF₆)

# %%
def regression_complete(df, name, unit):
    x = df['average'].values
    n = len(x)
    T = np.arange(n)

    r_corr, _ = stats.pearsonr(T, x)
    print(f'\n=== {name} ===')
    print(f'  Coefficient de corrélation : r = {r_corr:.6f}')

    slope, intercept, r_lin, _, _ = stats.linregress(T, x)
    trend_lin = intercept + slope * T
    print(f'  Linéaire : y = {intercept:.4f} + {slope:.6f}·t   R² = {r_lin**2:.6f}')

    b, a, r_exp, _, _ = stats.linregress(T, np.log(x))
    trend_exp = np.exp(a) * np.exp(b * T)
    print(f'  Exponentiel : y = {np.exp(a):.4f} × e^({b:.8f}·t)   R² = {r_exp**2:.6f}')

    T_prev = np.arange(n, n + 24)
    prev_lin = intercept + slope * T_prev
    prev_exp = np.exp(a) * np.exp(b * T_prev)

    print(f'  Prévisions :')
    for tp, pl, pe in zip(T_prev, prev_lin, prev_exp):
        print(f'    t={tp} → lin: {pl:.4f} | exp: {pe:.4f} {unit}')

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    for ax, trend, label, color, r2, prev in [
        (axes[0], trend_lin, 'Linéaire', 'red', r_lin**2, prev_lin),
        (axes[1], trend_exp, 'Exponentiel', 'green', r_exp**2, prev_exp)
    ]:
        ax.scatter(T, x, s=4, alpha=0.6, color='steelblue', label='Données')
        ax.plot(T, trend, color=color, lw=2, label=f'{label} R²={r2:.4f}')
        ax.scatter(T_prev, prev, s=15, color='orange', zorder=5, label='Prévisions')
        ax.set_title(f'{name} — {label}')
        ax.set_ylabel(f'({unit})'); ax.legend()
    plt.suptitle(f'{name} — Comparaison modèles', fontweight='bold')
    plt.tight_layout()
    plt.show()

regression_complete(df_n2o, 'N2O', 'ppb')
regression_complete(df_sf6, 'SF6', 'ppt')

# %% [markdown]
# **Interprétation — Question 8 :**
#
# **8.1 — Coefficient de corrélation :**  
# Un coefficient r très proche de 1 (attendu > 0.99 pour les deux gaz) confirme qu'il existe une relation quasi-parfaite entre le temps et la concentration. Ces gaz augmentent de façon très régulière, portés par des activités humaines en croissance constante.
#
# **8.2 — Droite de régression :**  
# La pente de la droite donne l'augmentation moyenne de concentration par mois. Pour N₂O et SF₆, cette croissance est régulière et quasi-linéaire sur la période observée.
#
# **8.4 — Comparaison linéaire vs exponentiel :**  
# Le modèle exponentiel modélise une croissance relative constante (le même pourcentage d'augmentation chaque année). Pour SF₆, dont les émissions industrielles ont fortement accéléré depuis les années 1980, le modèle exponentiel devrait donner un R² légèrement supérieur au modèle linéaire, ce qui le rend plus pertinent pour ce gaz. Pour N₂O, les deux modèles sont comparables car la croissance est plus régulière.

# %% [markdown]
# ---
# ## Question 9 — Données annuelles agrégées (CH₄ et CO₂)

# %%
# Q9 — Agrégation annuelle (années complètes uniquement)

for gaz in ['CH4', 'CO2']:
    nb_mois = datasets_full[gaz].groupby('year')['month'].count()
    annees_completes = nb_mois[nb_mois == 12].index
    exclues = sorted(set(datasets_full[gaz]['year']) - set(annees_completes))
    print(f'{gaz} | années incomplètes exclues : {exclues}')

annuel = {}
for gaz in ['CH4', 'CO2']:
    sous = datasets_full[gaz][datasets_full[gaz]['year'].isin(
        datasets_full[gaz].groupby('year')['month'].count().pipe(lambda s: s[s == 12].index)
    )]
    ag = sous.groupby('year')['average'].mean().reset_index()
    annuel[gaz] = ag
    print(f'{gaz} : {len(ag)} années | aperçu :')
    print(ag.head(3))
    print()

def regression_annuelle(gaz, unit):
    ag = annuel[gaz]
    y = ag['average'].values
    n = len(y)
    T = np.arange(n)
    annees = ag['year'].values

    r = np.corrcoef(T, y)[0, 1]
    print(f'\n=== {gaz} annuel === r = {r:.6f}')

    # Régression linéaire
    sl, ic, r_l, _, _ = stats.linregress(T, y)
    trend_lin = ic + sl * T
    r2_lin = r_l ** 2
    print(f'  Linéaire : y = {ic:.4f} + {sl:.4f}·t   R² = {r2_lin:.6f}')

    # Régression exponentielle — R² calculé sur les valeurs originales
    b_ln, lnA, _, _, _ = stats.linregress(T, np.log(y))
    A = np.exp(lnA)
    trend_exp = A * np.exp(b_ln * T)
    r2_exp = 1 - np.sum((y - trend_exp)**2) / np.sum((y - y.mean())**2)
    print(f'  Expo     : y = {A:.4f} × e^({b_ln:.6f}·t)   R² = {r2_exp:.6f}')

    # Prévisions
    T_p = np.array([n, n + 1])
    annees_p = [int(annees[-1]) + 1, int(annees[-1]) + 2]
    prev_lin = ic + sl * T_p
    prev_exp = A * np.exp(b_ln * T_p)
    print(f'  Prévisions :')
    for an, pl, pe in zip(annees_p, prev_lin, prev_exp):
        print(f'    {an} → lin: {pl:.2f} | exp: {pe:.2f} {unit}')

    # Graphiques
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, trend, label, color, r2, prev in [
        (axes[0], trend_lin, 'Linéaire',     'red',    r2_lin, prev_lin),
        (axes[1], trend_exp, 'Exponentiel',  'purple', r2_exp, prev_exp),
    ]:
        ax.scatter(T, y, s=25, color='steelblue', label='Données annuelles')
        ax.plot(T, trend, color=color, lw=2, label=f'{label} R²={r2:.4f}')
        ax.scatter(T_p, prev, s=80, color='orange', zorder=5, marker='*', label='Prévisions')
        step = max(1, len(annees) // 10)
        ax.set_xticks(T[::step])
        ax.set_xticklabels(annees[::step], rotation=45)
        ax.set_title(f'{gaz} annuel — {label}')
        ax.set_ylabel(f'({unit})')
        ax.legend()
    plt.suptitle(f'{gaz} — Régression annuelle', fontweight='bold')
    plt.tight_layout()
    plt.show()

regression_annuelle('CH4', 'ppb')
regression_annuelle('CO2', 'ppm')


# %% [markdown]
# **Interprétation — Question 9 :**
#
# **9.1 — Agrégation annuelle :**  
# En calculant la moyenne annuelle des mesures mensuelles, on obtient une série plus lissée qui efface les variations saisonnières. Chaque point représente désormais la concentration moyenne sur une année entière.
#
# **9.3 — Coefficient de corrélation :**  
# Attendu très proche de 1 pour les deux gaz, confirmant la tendance croissante très régulière à l'échelle annuelle.
#
# **9.6 — Comparaison linéaire vs exponentiel sur données annuelles :**  
# Sur des données annuelles, l'accélération éventuelle de la croissance est plus visible qu'en mensuel. Si le R² du modèle exponentiel est supérieur, cela indique que le rythme de hausse s'accélère lui-même avec le temps. Pour le CO₂, la croissance a effectivement tendance à s'accélérer ces dernières décennies, ce qui pourrait rendre le modèle exponentiel légèrement plus pertinent.

# %% [markdown]
# ---
# ## Conclusion générale
#
# Ce mini-projet a permis d'analyser l'évolution des concentrations de quatre gaz à effet de serre sur plusieurs décennies à partir de données réelles du NOAA.
#
# **Principaux résultats :**
#
# - Tous les gaz présentent une **tendance croissante**, reflet de l'augmentation continue des émissions humaines depuis la révolution industrielle.
# - **CH₄ et CO₂** se distinguent par des **variations saisonnières marquées**, qui ont pu être modélisées et extraites grâce à la décomposition en série temporelle.
# - La **décomposition additive** s'est révélée plus pertinente que la multiplicative pour ces deux gaz, car l'amplitude des oscillations saisonnières reste stable dans le temps.
# - **N₂O et SF₆** suivent une croissance quasi-monotone mieux capturée par une **régression directe**, avec une légère préférence pour le modèle exponentiel pour SF₆.
# - Les prévisions effectuées sur les deux prochaines années suggèrent une **poursuite de la hausse** pour les quatre gaz, ce qui souligne l'urgence de réduire les émissions à l'échelle mondiale.
