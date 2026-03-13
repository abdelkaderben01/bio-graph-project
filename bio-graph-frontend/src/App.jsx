import { useState } from "react";
import GraphView from "./components/GraphView";
import NodeDetailsPanel from "./components/NodeDetailsPanel";
import ProjectStatsPanel from "./components/ProjectStatsPanel";
import QuerySelector from "./components/QuerySelector";
import SearchBar from "./components/SearchBar";
import { ENTITY_TYPES, DEFAULT_QUERY_BY_TYPE, getQueryOption } from "./queryOptions";

function App() {
  const [entityType, setEntityType] = useState("protein");
  const [accession, setAccession] = useState("Q04828");
  const [goId, setGoId] = useState("GO:0005886");
  const [ecNumber, setEcNumber] = useState("1.1.1.1");
  const [iprId, setIprId] = useState("IPR000276");
  const [queryType, setQueryType] = useState("protein_neighbors");
  const [selectedNode, setSelectedNode] = useState(null);
  const [graphMeta, setGraphMeta] = useState({ recordCount: null, error: null });

  const selectedQuery = getQueryOption(queryType);

  function handleEntityTypeChange(type) {
    setEntityType(type);
    setQueryType(DEFAULT_QUERY_BY_TYPE[type]);
    setSelectedNode(null);
    setGraphMeta({ recordCount: null, error: null });
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="kicker">Neo4j + React + NeoVis</p>
        <h1>Bio Graph Explorer</h1>
        <p>
          Explore proteins, GO terms, InterPro domains and enzymes from your Neo4j graph.
        </p>
      </section>

      {/* Global entity type filter */}
      <nav className="entity-filter" aria-label="Entity type filter">
        <span className="filter-label">Explore :</span>
        {ENTITY_TYPES.map((et) => (
          <button
            key={et.key}
            type="button"
            data-type={et.key}
            className={`entity-btn ${entityType === et.key ? "active" : ""}`}
            onClick={() => handleEntityTypeChange(et.key)}
          >
            {et.icon} {et.label}
          </button>
        ))}
      </nav>

      <section className="controls-grid">
        <SearchBar
          entityType={entityType}
          accession={accession}
          setAccession={setAccession}
          goId={goId}
          setGoId={setGoId}
          ecNumber={ecNumber}
          setEcNumber={setEcNumber}
          iprId={iprId}
          setIprId={setIprId}
        />
        <QuerySelector
          queryType={queryType}
          setQueryType={setQueryType}
          entityType={entityType}
        />
      </section>

      <ProjectStatsPanel />

      <section className="workspace-grid">
        <GraphView
          accession={accession}
          goId={goId}
          ecNumber={ecNumber}
          iprId={iprId}
          queryType={queryType}
          selectedQuery={selectedQuery}
          onNodeSelect={setSelectedNode}
          onGraphMetaChange={setGraphMeta}
        />
        <NodeDetailsPanel
          selectedNode={selectedNode}
          graphMeta={graphMeta}
          entityType={entityType}
          queryType={queryType}
          onPredict={() => setQueryType("protein_predicted")}
        />
      </section>
    </main>
  );
}

export default App;

