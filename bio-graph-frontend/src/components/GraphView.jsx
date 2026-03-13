import { useEffect, useRef } from "react";
import { NeoVis, NeoVisEvents } from "neovis.js";

function sanitizeCypherValue(value) {
  return String(value || "").replace(/'/g, "\\'");
}

function buildCypher(queryType, accession, goId, ecNumber, iprId) {
  const safeAccession = sanitizeCypherValue(accession || "A0A023GRW5");
  const safeGoId = sanitizeCypherValue(goId);
  const safeEcNumber = sanitizeCypherValue(ecNumber);
  const safeIprId = sanitizeCypherValue(iprId);

  switch (queryType) {
    case "protein_predicted":
      return `
          MATCH (p:Protein {accession:'${safeAccession}'})-[r:PREDICTED_ANNOTATION]->(g:GOTerm)
          RETURN p, r, g
          LIMIT 30
        `;

    case "protein_go":
      return `
          MATCH (p:Protein {accession:'${safeAccession}'})-[r:ANNOTATED_WITH]->(g:GOTerm)
          RETURN p, r, g
          LIMIT 100
        `;

    case "protein_ppn_neighbors":
      return `
          MATCH (p:Protein {accession:'${safeAccession}'})-[r:SIMILAR_TO]-(q:Protein)
          RETURN p, r, q
          LIMIT 120
        `;

    case "protein_interpro":
      return `
          MATCH (p:Protein {accession:'${safeAccession}'})-[r:HAS_INTERPRO]->(i:InterProEntry)
          RETURN p, r, i
          LIMIT 100
        `;

    case "protein_enzyme":
      return `
          MATCH (p:Protein {accession:'${safeAccession}'})-[r:HAS_EC]->(e:Enzyme)
          RETURN p, r, e
          LIMIT 50
        `;

    case "go_hierarchy":
      return `
          MATCH (g:GOTerm {go_id:'${safeGoId}'})-[r]-(n)
          RETURN g, r, n
          LIMIT 80
        `;

    case "enzyme_to_proteins":
      return `
          MATCH (e:Enzyme {ec_number:'${safeEcNumber}'})<-[r:HAS_EC]-(p:Protein)
          RETURN e, r, p
          LIMIT 80
        `;

    case "go_annotated_proteins":
      return `
          MATCH (g:GOTerm {go_id:'${safeGoId}'})<-[r:ANNOTATED_WITH]-(p:Protein)
          RETURN g, r, p
          LIMIT 80
        `;

    case "interpro_to_proteins":
      return `
          MATCH (i:InterProEntry {ipr_id:'${safeIprId}'})<-[r:HAS_INTERPRO]-(p:Protein)
          RETURN i, r, p
          LIMIT 80
        `;

    case "protein_neighbors":
    default:
      return `
          MATCH (p:Protein {accession:'${safeAccession}'})-[r]-(n)
          RETURN p, r, n
          LIMIT 100
        `;
  }
}

function getNeo4jConfig(containerId) {
  return {
    containerId,
    neo4j: {
      serverUrl: import.meta.env.VITE_NEO4J_URL || "neo4j://127.0.0.1:7687",
      serverUser: import.meta.env.VITE_NEO4J_USER || "neo4j",
      serverPassword: import.meta.env.VITE_NEO4J_PASSWORD || "",
    },
    labels: {
      Protein: {
        label: "accession",
        [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
          static: {
            size: 26,
            color: "#0b6e61",
            borderWidth: 2,
            font: {
              color: "#071322",
              size: 16,
              face: "IBM Plex Sans",
            },
          },
          function: {
            title: (node) =>
              `Protein\naccession: ${node.properties.accession || ""}\nname: ${node.properties.protein_name || ""}`,
          },
        },
      },
      GOTerm: {
        label: "name",
        [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
          static: {
            size: 22,
            color: "#df4f2b",
            borderWidth: 2,
            font: {
              color: "#071322",
              size: 14,
              face: "IBM Plex Sans",
            },
          },
          function: {
            title: (node) =>
              `GO\nid: ${node.properties.go_id || ""}\nname: ${node.properties.name || ""}\nnamespace: ${node.properties.namespace || ""}`,
          },
        },
      },
      InterProEntry: {
        label: "ipr_id",
        [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
          static: {
            size: 22,
            color: "#35526d",
            borderWidth: 2,
            font: {
              color: "#071322",
              size: 14,
              face: "IBM Plex Sans",
            },
          },
        },
      },
      Enzyme: {
        label: "ec_number",
        [NeoVis.NEOVIS_ADVANCED_CONFIG]: {
          static: {
            size: 22,
            color: "#4b8b3b",
            borderWidth: 2,
            font: {
              color: "#071322",
              size: 14,
              face: "IBM Plex Sans",
            },
          },
        },
      },
    },
    relationships: {
      SIMILAR_TO: { label: true },
      ANNOTATED_WITH: { label: true },
      PREDICTED_ANNOTATION: { label: true },
      HAS_INTERPRO: { label: true },
      HAS_EC: { label: true },
      IS_A: { label: true },
      PART_OF: { label: true },
      REGULATES: { label: true },
      POSITIVELY_REGULATES: { label: true },
      NEGATIVELY_REGULATES: { label: true },
    },
    visConfig: {
      nodes: {
        shape: "dot",
        size: 22,
        borderWidth: 2,
        font: {
          size: 16,
          face: "IBM Plex Sans",
          color: "#071322",
        },
      },
      edges: {
        width: 1.4,
        color: "#35526d",
        arrows: {
          to: {
            enabled: true,
            scaleFactor: 0.4,
          },
        },
      },
      interaction: {
        hover: true,
      },
      physics: {
        stabilization: {
          iterations: 200,
        },
        barnesHut: {
          gravitationalConstant: -2300,
          springLength: 160,
        },
      },
    },
  };
}

export default function GraphView({
  accession,
  goId,
  ecNumber,
  iprId,
  queryType,
  selectedQuery,
  onNodeSelect,
  onGraphMetaChange,
}) {
  const containerRef = useRef(null);
  const vizRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) {
      return undefined;
    }

    if (vizRef.current) {
      vizRef.current.clearNetwork();
    }

    const cypherQuery = buildCypher(queryType, accession, goId, ecNumber, iprId);

    const config = {
      ...getNeo4jConfig(containerRef.current.id),
      initialCypher: cypherQuery,
    };
    const viz = new NeoVis(config);

    viz.registerOnEvent(NeoVisEvents.CompletionEvent, (event) => {
      onGraphMetaChange({ recordCount: event.recordCount, error: null });
    });

    viz.registerOnEvent(NeoVisEvents.ErrorEvent, (event) => {
      onGraphMetaChange({ recordCount: null, error: event.error.message });
    });

    viz.registerOnEvent(NeoVisEvents.ClickNodeEvent, (event) => {
      onNodeSelect(event.node);
    });

    viz.render();

    vizRef.current = viz;

    return () => {
      if (vizRef.current) {
        vizRef.current.clearNetwork();
      }
    };
  }, [queryType, accession, goId, ecNumber, iprId, onGraphMetaChange, onNodeSelect]);

  const missingCredentials = !import.meta.env.VITE_NEO4J_PASSWORD;

  return (
    <section className="panel graph-panel">
      <div className="graph-header">
        <div>
          <h2>Graph visualization</h2>
          <p className="panel-subtitle">Vue active: {selectedQuery.label}</p>
        </div>
        {missingCredentials ? (
          <p className="env-warning">
            Definis <code>VITE_NEO4J_PASSWORD</code> dans <code>.env</code> pour eviter les erreurs de connexion.
          </p>
        ) : null}
      </div>
      <div id="neo-graph" ref={containerRef} className="graph-canvas" />
    </section>
  );
}
