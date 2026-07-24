# OM News — Blog Django

Média en ligne en Django : articles, catégories, émissions, commentaires modérés, comptes utilisateurs, SEO.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # puis éditer .env si besoin
python manage.py migrate
python manage.py createsuperuser   # optionnel, pour l'admin
python manage.py runserver
```

L'application est disponible sur http://127.0.0.1:8000/.

## Configuration (`.env`)

- `DATABASE_URL` : optionnel, bascule vers PostgreSQL (ex: `postgres://user:pass@host:5432/db`). Laisser vide pour SQLite en local.
- `DJANGO_EMAIL_*` : optionnel, pour brancher un vrai envoi SMTP (mot de passe oublié, vérification email). Par défaut les emails s'affichent dans le terminal du serveur.
- `DJANGO_DEBUG=False` en production active automatiquement les en-têtes de sécurité (HTTPS forcé, cookies sécurisés, HSTS).

## Fonctionnalités

- Articles (éditeur riche CKEditor), catégories, pages auteur, émissions avec replay vidéo, pagination
- Recherche par titre et filtre par catégorie
- Commentaires avec réponses imbriquées, likes, signalement et modération (masquage automatique après 3 signalements)
- Comptes utilisateurs : inscription avec vérification par email, connexion, mot de passe oublié, profil éditable
- SEO : meta/Open Graph, sitemap.xml, robots.txt, flux RSS, données structurées Article
- Limitation de débit (rate limiting) sur la connexion, les commentaires et les likes
- Validation des fichiers uploadés (taille et extension), pages d'erreur personnalisées (403/404/500)

## Tests

```bash
python manage.py test
```
