import csv

input_file = "data/raw/go-basic.obo"
terms_output = "data/processed/go_terms.csv"
relations_output = "data/processed/go_relations.csv"

terms = []
relations = []

current_term = None
inside_term = False

def clean_def(def_line: str) -> str:
    if def_line.startswith('"'):
        parts = def_line.split('"')
        if len(parts) >= 3:
            return parts[1]
    return def_line

with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if line == "[Term]":
            if current_term and "id" in current_term:
                terms.append(current_term)
            current_term = {
                "id": None,
                "name": None,
                "namespace": None,
                "def": None,
                "is_obsolete": "false"
            }
            inside_term = True
            continue

        if line.startswith("[Typedef]"):
            if current_term and "id" in current_term:
                terms.append(current_term)
            current_term = None
            inside_term = False
            continue

        if not inside_term or current_term is None:
            continue

        if line == "":
            continue

        if line.startswith("id: "):
            current_term["id"] = line.replace("id: ", "").strip()

        elif line.startswith("name: "):
            current_term["name"] = line.replace("name: ", "").strip()

        elif line.startswith("namespace: "):
            current_term["namespace"] = line.replace("namespace: ", "").strip()

        elif line.startswith("def: "):
            raw_def = line.replace("def: ", "").strip()
            current_term["def"] = clean_def(raw_def)

        elif line.startswith("is_obsolete: "):
            current_term["is_obsolete"] = line.replace("is_obsolete: ", "").strip()

        elif line.startswith("is_a: "):
            target = line.replace("is_a: ", "").split(" ! ")[0].strip()
            if current_term["id"]:
                relations.append({
                    "source_go_id": current_term["id"],
                    "relation_type": "IS_A",
                    "target_go_id": target
                })

        elif line.startswith("relationship: "):
            content = line.replace("relationship: ", "").strip()
            parts = content.split()
            if len(parts) >= 2 and current_term["id"]:
                relation_name = parts[0].upper()
                target = parts[1]
                relations.append({
                    "source_go_id": current_term["id"],
                    "relation_type": relation_name,
                    "target_go_id": target
                })

if current_term and "id" in current_term:
    terms.append(current_term)

# Écriture go_terms.csv
with open(terms_output, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["go_id", "name", "namespace", "definition", "is_obsolete"])
    for term in terms:
        writer.writerow([
            term["id"],
            term["name"],
            term["namespace"],
            term["def"],
            term["is_obsolete"]
        ])

# Écriture go_relations.csv
with open(relations_output, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["source_go_id", "relation_type", "target_go_id"])
    for rel in relations:
        writer.writerow([
            rel["source_go_id"],
            rel["relation_type"],
            rel["target_go_id"]
        ])

print("Parsing terminé.")
print(f"Nombre de termes GO : {len(terms)}")
print(f"Nombre de relations GO : {len(relations)}")
print(f"Fichier créé : {terms_output}")
print(f"Fichier créé : {relations_output}")
