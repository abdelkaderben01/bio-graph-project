function normalizeValue(value) {
  if (value === null || value === undefined) {
    return "";
  }

  if (typeof value === "object") {
    if (typeof value.toString === "function" && value.toString !== Object.prototype.toString) {
      return value.toString();
    }
    return JSON.stringify(value);
  }

  return String(value);
}

function getNodeEntries(nodeData) {
  if (!nodeData || !nodeData.raw || !nodeData.raw.properties) {
    return [];
  }

  return Object.entries(nodeData.raw.properties)
    .map(([key, value]) => ({ key, value: normalizeValue(value) }))
    .sort((a, b) => a.key.localeCompare(b.key));
}

export default function NodeDetailsPanel({ selectedNode, graphMeta, entityType, queryType, onPredict }) {
  const entries = getNodeEntries(selectedNode);
  const labels = selectedNode?.raw?.labels || [];

  // Show predict banner when: we got 0 results, no error, working on proteins, not already predicting
  const showPredictBanner =
    entityType === "protein" &&
    graphMeta.recordCount === 0 &&
    !graphMeta.error &&
    queryType !== "protein_predicted";

  return (
    <aside className="panel details-panel">
      <h2>Node details</h2>
      <p className="panel-subtitle">Click a node in the graph to inspect its properties.</p>

      <div className="meta-block">
        <strong>Query state</strong>
        <p>
          {graphMeta.error
            ? `Error: ${graphMeta.error}`
            : `Records: ${graphMeta.recordCount ?? "waiting"}`}
        </p>
      </div>

      {showPredictBanner && (
        <div className="predict-banner">
          <p>No results found for this protein. Try the predicted annotations from label propagation.</p>
          <button type="button" className="predict-btn" onClick={onPredict}>
            Show predictions
          </button>
        </div>
      )}

      {!selectedNode ? (
        <p className="empty-note">No node selected yet.</p>
      ) : (
        <>
          <div className="meta-block">
            <strong>Node ID</strong>
            <p>{selectedNode.id}</p>
          </div>

          <div className="meta-block">
            <strong>Labels</strong>
            <p>{labels.length ? labels.join(", ") : "n/a"}</p>
          </div>

          <div className="kv-list">
            {entries.length ? (
              entries.map((entry) => (
                <div className="kv-item" key={entry.key}>
                  <span>{entry.key}</span>
                  <code>{entry.value}</code>
                </div>
              ))
            ) : (
              <p className="empty-note">The selected node has no exploitable properties.</p>
            )}
          </div>
        </>
      )}
    </aside>
  );
}
