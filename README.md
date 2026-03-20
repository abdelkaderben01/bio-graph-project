# Bio Graph Explorer - README

## 1) Presentation
Ce projet construit un graphe biologique a partir de donnees UniProt, GO, InterPro et Enzyme (EC), puis propose une interface React pour l'exploration dans Neo4j.

Le travail est organise en 3 blocs:
- pipeline data (scripts Python)
- construction des relations graphe
- visualisation et requetes via frontend React + NeoVis

## 2) Objectifs realises
- Nettoyage et fusion des donnees proteins (Humain + Rat).
- Extraction des termes GO et des relations d'ontologie.
- Parsing des annotations GOA, InterPro et Enzyme.
- Construction du PPN (Protein-Protein Network) avec similarite Jaccard.
- Calcul des statistiques du projet.
- Baseline de label propagation pour predire des annotations.
- Interface web de consultation et visualisation.

## 3) Etapes executees 
### Etape 1 - Inspection et nettoyage UniProt
Scripts:
- scripts/01_inspect_uniprot.py
- scripts/02_compare_9606.py
- scripts/03_clean_uniprot.py
- scripts/04_merge_proteins.py

Sorties:
- data/processed/proteins_human_clean.csv
- data/processed/proteins_rat_clean.csv
- data/processed/proteins_all_clean.csv

### Etape 2 - Parsing GO (ontology)
Script:
- scripts/05_parse_go_obo.py

Sorties:
- data/processed/go_terms.csv
- data/processed/go_relations.csv

### Etape 3 - Parsing GOA (annotations proteins -> GO)
Script:
- scripts/06_parse_goa_gaf.py

Sortie:
- data/processed/protein_go_rel.csv

### Etape 4 - Parsing InterPro
Script:
- scripts/07_parse_interpro.py

Sorties:
- data/processed/protein_interpro_rel.csv
- data/processed/interpro_nodes.csv

### Etape 5 - Parsing Enzyme (EC)
Script:
- scripts/08_parse_enzyme.py

Sorties:
- data/processed/protein_enzyme_rel.csv
- data/processed/enzyme_nodes.csv

### Etape 6 - Construction PPN (Jaccard)
Script:
- scripts/09_build_ppn_jaccard.py

Sortie:
- data/processed/protein_similarity_jaccard.csv

### Etape 7 - Statistiques projet
Script:
- scripts/10_compute_project_stats.py

Sorties:
- data/processed/project_stats.json
- data/processed/project_stats_table.csv

### Etape 8 - Label propagation (baseline)
Script:
- scripts/11_label_propagation_baseline.py

Sortie:
- data/processed/protein_label_predictions.csv

## 4) Arborescence utile
- bio-graph-frontend/ : application React
- scripts/ : pipeline data
- data/raw/ : donnees brutes
- data/extracted/ : exports intermediaires
- data/processed/ : fichiers finaux pour Neo4j
- docs/ : notes soutenance

## 5) Prerequis
- Python 3.10+
- Node.js 18+ (20 recommande)
- npm
- Neo4j local

## 6) Lancer l'application (etape par etape)
Note importante: l'application peut demarrer sans CSV, mais pour explorer des donnees il faut importer les CSV requis dans Neo4j (voir section 11).

### 6.1 Frontend
```bash
cd bio-graph-frontend
npm install
npm run dev
```
Application: http://localhost:5173

### 6.2 Configuration Neo4j
Creer le fichier bio-graph-frontend/.env
```env
VITE_NEO4J_URL=neo4j://127.0.0.1:7687
VITE_NEO4J_USER=neo4j
VITE_NEO4J_PASSWORD=your_password
```

## 7) Interface utilisateur + requetes utilisees

L'interface principale est composee de 5 zones:
- Filtre de type d'entite (Protein / GO Term / Enzyme / InterPro)
- Zone de saisie (Search)
- Selecteur de requete (Cypher queries)
- Visualisation du graphe
- Panneau de details du noeud

### 7.1 Filtre d'entite (barre Explore)
Quand on change d'entite, l'UI charge une requete par defaut:
- `protein` -> `protein_neighbors`
- `go` -> `go_hierarchy`
- `enzyme` -> `enzyme_to_proteins`
- `interpro` -> `interpro_to_proteins`

### 7.2 Search (champ identifiant)
Le champ change selon l'entite active:
- Protein: accession (ex: `Q04828`)
- GO Term: go_id (ex: `GO:0005886`)
- Enzyme: ec_number (ex: `1.1.1.1`)
- InterPro: ipr_id (ex: `IPR000276`)

### 7.3 Requetes disponibles cote interface
#### Requetes Protein
- `protein_neighbors` (Protein + neighbours)
```cypher
MATCH (p:Protein {accession:'<ACC>'})-[r]-(n)
RETURN p, r, n
LIMIT 100
```

- `protein_ppn_neighbors` (PPN: Similar proteins)
```cypher
MATCH (p:Protein {accession:'<ACC>'})-[r:SIMILAR_TO]-(q:Protein)
RETURN p, r, q
LIMIT 120
```

- `protein_go` (Protein + GO)
```cypher
MATCH (p:Protein {accession:'<ACC>'})-[r:ANNOTATED_WITH]->(g:GOTerm)
RETURN p, r, g
LIMIT 100
```

- `protein_interpro` (Protein + InterPro)
```cypher
MATCH (p:Protein {accession:'<ACC>'})-[r:HAS_INTERPRO]->(i:InterProEntry)
RETURN p, r, i
LIMIT 100
```

- `protein_enzyme` (Protein + Enzyme)
```cypher
MATCH (p:Protein {accession:'<ACC>'})-[r:HAS_EC]->(e:Enzyme)
RETURN p, r, e
LIMIT 50
```

- `protein_predicted` (Predicted functions)
```cypher
MATCH (p:Protein {accession:'<ACC>'})-[r:PREDICTED_ANNOTATION]->(g:GOTerm)
RETURN p, r, g
LIMIT 30
```

#### Requetes GO
- `go_hierarchy` (GO + hierarchy)
```cypher
MATCH (g:GOTerm {go_id:'<GO_ID>'})-[r]-(n)
RETURN g, r, n
LIMIT 80
```

- `go_annotated_proteins` (GO + proteins)
```cypher
MATCH (g:GOTerm {go_id:'<GO_ID>'})<-[r:ANNOTATED_WITH]-(p:Protein)
RETURN g, r, p
LIMIT 80
```

#### Requete Enzyme
- `enzyme_to_proteins` (Enzyme + proteins)
```cypher
MATCH (e:Enzyme {ec_number:'<EC>'})<-[r:HAS_EC]-(p:Protein)
RETURN e, r, p
LIMIT 80
```

#### Requete InterPro
- `interpro_to_proteins` (InterPro + proteins)
```cypher
MATCH (i:InterProEntry {ipr_id:'<IPR_ID>'})<-[r:HAS_INTERPRO]-(p:Protein)
RETURN i, r, p
LIMIT 80
```

### 7.4 Comportement du panneau de droite (Node details)
- Affiche l'etat de la requete (`Records`, `Error`).
- Affiche les proprietes du noeud clique.
- Si une requete Protein retourne 0 resultat, le bouton `Show predictions` apparait et bascule sur `protein_predicted`.

### 7.5 Visualisation graphe
- Moteur: NeoVis.
- Clic sur noeud -> details dans le panneau droit.
- Types de relations visualisees: `SIMILAR_TO`, `ANNOTATED_WITH`, `PREDICTED_ANNOTATION`, `HAS_INTERPRO`, `HAS_EC`, `IS_A`, `PART_OF`, `REGULATES`, `POSITIVELY_REGULATES`, `NEGATIVELY_REGULATES`.

## 8) Import des predictions dans Neo4j
Copier:
- data/processed/protein_label_predictions.csv
vers le dossier import de Neo4j.

Puis executer:
```cypher
LOAD CSV WITH HEADERS FROM 'file:///protein_label_predictions.csv' AS row
WITH row WHERE row.label_type = 'GO'
MATCH (p:Protein {accession: row.accession})
MATCH (g:GOTerm {go_id: row.predicted_label})
MERGE (p)-[r:PREDICTED_ANNOTATION]->(g)
SET r.score = toFloat(row.score),
    r.support = toInteger(row.support_neighbors),
    r.rank = toInteger(row.rank);
```

## 9) Rejouer le pipeline (si besoin)
Depuis la racine du projet:
```bash
python scripts/05_parse_go_obo.py
python scripts/06_parse_goa_gaf.py
python scripts/07_parse_interpro.py
python scripts/08_parse_enzyme.py
python scripts/09_build_ppn_jaccard.py
python scripts/10_compute_project_stats.py
python scripts/11_label_propagation_baseline.py
```

## 10) Verification avant rendu
```bash
cd bio-graph-frontend
npm run lint
npm run build
```

## 11) Fichiers CSV requis 

Important: le frontend n'explore pas directement les CSV. Il interroge Neo4j.
Le prof doit donc disposer des CSV suivants et les importer dans Neo4j.
Script d'import complet pret a executer: docs/neo4j_import_full.cypher

### Minimum utile (exploration de base)
- data/processed/proteins_human_clean.csv (ou data/processed/proteins_all_clean.csv)
- data/processed/go_terms.csv
- data/processed/protein_go_rel.csv

### Experience complete (toutes les vues de l'interface)
- data/processed/proteins_human_clean.csv (ou data/processed/proteins_all_clean.csv)
- data/processed/go_terms.csv
- data/processed/go_relations.csv
- data/processed/protein_go_rel.csv
- data/processed/interpro_nodes.csv
- data/processed/protein_interpro_rel.csv
- data/processed/enzyme_nodes.csv
- data/processed/protein_enzyme_rel.csv
- data/processed/protein_similarity_jaccard.csv

### Optionnel
- data/processed/protein_label_predictions.csv
    (active les relations PREDICTED_ANNOTATION et la vue de prediction)
