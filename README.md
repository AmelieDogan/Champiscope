# Champiscope


Une application interactive pour explorer et comprendre les champignons en France.

## 🚀 Objectifs du projet

Champiscope est une application web destinée à :
- *Explorer les données sur les champignons présents en France* grâce à des fiches d’identité détaillées et des recherches avancées.
- *Sensibiliser à la biodiversité fongique* par le biais de visualisations interactives (cartes et graphiques).

Cette application s’adresse à un public francophone, comprenant :
- Les amateurs de champignons (mycophiles).
- Les étudiants et chercheurs en biologie.
- Le grand public curieux.

---

## 🗂️ Fonctionnalités essentielles

- *Gestion des utilisateurs* :
  - Inscription, connexion, déconnexion.
  - Gestion de profils : favoris et historiques des résultats pour le quiz "Es-tu un expert en comestibilité ?".
- *Recherche avancée* :
  - Recherche par nom ou caractéristiques (toxicité, couleur, milieu, saison, etc.).
  - Présentation des champignons sous forme de catalogue avec fiches d’identité détaillées.
- *Visualisations de données* :
  - Carte interactive des observations de champignons en France sur la fiche d'identité de chaque espèce.
  - Graphiques pour explorer la comestibilité et saison de pousse.
- *Interface utilisateur* :
  - Design adapté aux ordinateurs.

---

## 📊 Sources de données

Les données utilisées proviennent de sources ouvertes et fiables, telles que :
- [Identifier les champignons (1249 espèces)](https://www.data.gouv.fr/en/datasets/donnees-du-site-identifier-les-champignons-com/).
- [TaxRef (Référentiel des espèces françaises)](https://inpn.mnhn.fr/telechargement/referentielEspece/taxref/18.0/menu#).
- [Liste rouge des champignons menacés en France (PDF et CSV)](https://uicn.fr/).
- [GBIF (1 159 016 occurrences d'observations en France)](https://www.gbif.org/occurrence/search?country=FR&taxon_key=5).

---

## 🛠️ Technologies utilisées

- *Back-end* : Python, Flask, SQLAlchemy, Requests.
- *Front-end* : HTML5, CSS3, JavaScript.
- *Base de données* : SQL (SGBD : SQLite).
- *Gestion des versions* : Git avec dépôt collaboratif sur GitHub.

---

## 🔧 Installation et utilisation

### Prérequis
- *Python 3.9+* installé.
- Gestionnaire de paquets *pip*.
- Environnement virtuel recommandé : venv.

### Installation sur Linux (avec bash)
1. Clonez le dépôt Git :
   ```bash
   git clone [https://github.com/votre-utilisateur/champiscope.git](https://github.com/AmelieDogan/Champiscope.git)
   ```
2. Déplacez-vous dans le répertoire du projet :
   ```bash
   cd Champiscope
   ```
3. Créez un environnement virtuel :
   ```bash
   python -m venv env
   ```
4. Activez votre environnement virtuel :
    ```bash
    source env/bin/activate
    ```
5. Installez les dépendances de l'application
    ```bash
    pip install -r requirements.txt
    ```
6. Lancez l'application
    ```bash
    python run.py
    ```
