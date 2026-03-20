# Bio Graph Frontend

README rapide frontend. Le guide complet du projet est dans ../README.md.

## Lancer
```bash
npm install
npm run dev
```

## Build
```bash
npm run lint
npm run build
```

## Variables .env
Vous devez créer ou modifier le fichier `.env` à la racine du dossier `bio-graph-frontend`.
Copiez le contenu de `.env.example` et changez le mot de passe :
```env
VITE_NEO4J_URL=neo4j://127.0.0.1:7687
VITE_NEO4J_USER=neo4j
VITE_NEO4J_PASSWORD=changez_ceci
```
**Attention :** Le mot de passe doit correspondre à celui de votre instance Neo4j.
