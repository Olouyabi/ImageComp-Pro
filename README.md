# ImageComp Pro

Application avancée de compression d'images avec interface graphique moderne.

## Structure du Projet

```
imagecomp_pro/
├── core/                    # Logique métier principale
│   ├── __pycache__/        # Fichiers compilés Python
│   ├── compression.py      # Logique de compression
│   ├── file_utils.py      # Utilitaires de manipulation de fichiers
│   ├── settings.py        # Gestion des paramètres
│   └── stats.py           # Statistiques de compression
├── resources/              # Ressources du projet
│   ├── icons/             # Icônes de l'application
│   │   ├── app_icon.ico   # Icône de l'application
│   │   ├── app_icon.png   # Icône de l'application (PNG)
│   │   ├── dark_mode.png  # Icône mode sombre
│   │   ├── light_mode.png # Icône mode clair
│   │   ├── settings_icon.png
│   │   ├── about_icon.png
│   │   └── stats_icon.png
│   └── resources.qrc      # Fichier de ressources Qt
├── ui/                     # Interface utilisateur
│   ├── __pycache__/       # Fichiers compilés Python
│   ├── components/        # Composants UI réutilisables
│   │   ├── __pycache__/  # Fichiers compilés Python
│   │   ├── file_list.py  # Liste de fichiers avec glisser-déposer
│   │   ├── log_view.py   # Vue de log
│   │   └── settings_panel.py # Panneau de paramètres
│   ├── dialogs/          # Dialogues de l'application
│   │   ├── __pycache__/  # Fichiers compilés Python
│   │   ├── about.py      # Dialogue À Propos
│   │   └── stats.py      # Dialogue Statistiques
│   └── main_window.py     # Fenêtre principale
├── main.py                # Point d'entrée de l'application
├── requirements.txt       # Dépendances Python
└── resources_rc.py       # Fichier de ressources Qt compilé
```

## Fonctionnalités

- Compression d'images en masse
- Interface utilisateur moderne avec thème sombre/clair
- Glisser-déposer de fichiers
- Prévisualisation des fichiers
- Paramètres de compression personnalisables
- Statistiques détaillées
- Journalisation des opérations
- Interface multilingue (Français)

## Dépendances

Les dépendances nécessaires sont listées dans `requirements.txt`:
- PySide6
- Pillow
- numpy
- pandas (pour les statistiques)

## Installation

1. Créer un environnement virtuel:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

2. Installer les dépendances:
```bash
pip install -r requirements.txt
```

3. Lancer l'application:
```bash
python main.py
```

## Configuration

Les paramètres de l'application sont stockés dans un fichier JSON (`settings.json`) et peuvent être modifiés via l'interface "Préférences".

## Contribuer

1. Créer une branche pour votre fonctionnalité:
```bash
git checkout -b feature/nom-de-votre-fonctionnalite
```

2. Commit vos changements:
```bash
git commit -m "Ajout de la fonctionnalité X"
```

3. Pousser vers la branche:
```bash
git push origin feature/nom-de-votre-fonctionnalite
```

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
