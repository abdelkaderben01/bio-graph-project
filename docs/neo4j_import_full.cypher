// Bio Graph Explorer - Full Neo4j import script
// Prerequisite: copy CSV files to Neo4j import directory
// - proteins_all_clean.csv
// - go_terms.csv
// - interpro_nodes.csv
// - enzyme_nodes.csv
// - go_relations.csv
// - protein_go_rel.csv
// - protein_interpro_rel.csv
// - protein_enzyme_rel.csv

// Etape 4 - creer les contraintes Neo4j

CREATE CONSTRAINT protein_accession IF NOT EXISTS
FOR (p:Protein) REQUIRE p.accession IS UNIQUE;

CREATE CONSTRAINT go_id_unique IF NOT EXISTS
FOR (g:GOTerm) REQUIRE g.go_id IS UNIQUE;

CREATE CONSTRAINT interpro_id_unique IF NOT EXISTS
FOR (i:InterProEntry) REQUIRE i.ipr_id IS UNIQUE;

CREATE CONSTRAINT enzyme_ec_unique IF NOT EXISTS
FOR (e:Enzyme) REQUIRE e.ec_number IS UNIQUE;

// Etape 5 - importer les noeuds

// 5.1 Import des proteines
LOAD CSV WITH HEADERS FROM 'file:///proteins_all_clean.csv' AS row
MERGE (p:Protein {accession: row.accession})
SET p.entry_name = row.entry_name,
    p.protein_name = row.protein_name,
    p.interpro_ids = row.interpro_ids,
    p.ec_number = row.ec_number;

// 5.2 Import des termes GO
LOAD CSV WITH HEADERS FROM 'file:///go_terms.csv' AS row
MERGE (g:GOTerm {go_id: row.go_id})
SET g.name = row.name,
    g.namespace = row.namespace,
    g.definition = row.definition,
    g.is_obsolete = row.is_obsolete;

// 5.3 Import des noeuds InterPro
LOAD CSV WITH HEADERS FROM 'file:///interpro_nodes.csv' AS row
MERGE (i:InterProEntry {ipr_id: row.ipr_id})
SET i.ipr_name = row.ipr_name;

// 5.4 Import des noeuds Enzyme
LOAD CSV WITH HEADERS FROM 'file:///enzyme_nodes.csv' AS row
MERGE (e:Enzyme {ec_number: row.ec_number})
SET e.enzyme_name = row.enzyme_name;

// Etape 6 - importer les relations

// 6.1 Relations GO entre termes
// IS_A
LOAD CSV WITH HEADERS FROM 'file:///go_relations.csv' AS row
WITH row
WHERE row.relation_type = 'IS_A'
MATCH (a:GOTerm {go_id: row.source_go_id})
MATCH (b:GOTerm {go_id: row.target_go_id})
MERGE (a)-[:IS_A]->(b);

// PART_OF
LOAD CSV WITH HEADERS FROM 'file:///go_relations.csv' AS row
WITH row
WHERE row.relation_type = 'PART_OF'
MATCH (a:GOTerm {go_id: row.source_go_id})
MATCH (b:GOTerm {go_id: row.target_go_id})
MERGE (a)-[:PART_OF]->(b);

// REGULATES
LOAD CSV WITH HEADERS FROM 'file:///go_relations.csv' AS row
WITH row
WHERE row.relation_type = 'REGULATES'
MATCH (a:GOTerm {go_id: row.source_go_id})
MATCH (b:GOTerm {go_id: row.target_go_id})
MERGE (a)-[:REGULATES]->(b);

// POSITIVELY_REGULATES
LOAD CSV WITH HEADERS FROM 'file:///go_relations.csv' AS row
WITH row
WHERE row.relation_type = 'POSITIVELY_REGULATES'
MATCH (a:GOTerm {go_id: row.source_go_id})
MATCH (b:GOTerm {go_id: row.target_go_id})
MERGE (a)-[:POSITIVELY_REGULATES]->(b);

// NEGATIVELY_REGULATES
LOAD CSV WITH HEADERS FROM 'file:///go_relations.csv' AS row
WITH row
WHERE row.relation_type = 'NEGATIVELY_REGULATES'
MATCH (a:GOTerm {go_id: row.source_go_id})
MATCH (b:GOTerm {go_id: row.target_go_id})
MERGE (a)-[:NEGATIVELY_REGULATES]->(b);

// 6.2 Relations Protein -> GO
LOAD CSV WITH HEADERS FROM 'file:///protein_go_rel.csv' AS row
MATCH (p:Protein {accession: row.accession})
MATCH (g:GOTerm {go_id: row.go_id})
MERGE (p)-[r:ANNOTATED_WITH]->(g)
SET r.evidence_code = row.evidence_code,
    r.reference = row.reference,
    r.aspect = row.aspect,
    r.aspect_name = row.aspect_name,
    r.assigned_by = row.assigned_by,
    r.qualifier = row.qualifier;

// 6.3 Relations Protein -> InterPro
LOAD CSV WITH HEADERS FROM 'file:///protein_interpro_rel.csv' AS row
MATCH (p:Protein {accession: row.accession})
MATCH (i:InterProEntry {ipr_id: row.ipr_id})
MERGE (p)-[:HAS_INTERPRO]->(i);

// 6.4 Relations Protein -> Enzyme
LOAD CSV WITH HEADERS FROM 'file:///protein_enzyme_rel.csv' AS row
MATCH (p:Protein {accession: row.accession})
MATCH (e:Enzyme {ec_number: row.ec_number})
MERGE (p)-[:HAS_EC]->(e);