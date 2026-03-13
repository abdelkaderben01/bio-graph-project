import { getQueriesForType, getQueryOption } from "../queryOptions";

export default function QuerySelector({ queryType, setQueryType, entityType }) {
  const options = getQueriesForType(entityType);
  const selected = getQueryOption(queryType);

  return (
    <article className="panel">
      <h2>Cypher queries</h2>
      <p className="panel-subtitle">Choose the graph view to display.</p>

      <label htmlFor="query-select">Graph view</label>
      <select
        id="query-select"
        value={queryType}
        onChange={(event) => setQueryType(event.target.value)}
        className="query-select"
      >
        {options.map((option) => (
          <option key={option.key} value={option.key}>
            {option.label}
          </option>
        ))}
      </select>

      <p className="query-help">{selected.description}</p>
      <div className="chip-row" aria-label="Quick-select views">
        {options.map((option) => (
          <button
            key={option.key}
            type="button"
            className={`chip ${queryType === option.key ? "active" : ""}`}
            onClick={() => setQueryType(option.key)}
          >
            {option.label}
          </button>
        ))}
      </div>
    </article>
  );
}

