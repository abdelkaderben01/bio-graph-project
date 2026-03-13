import { ENTITY_TYPES } from "../queryOptions";

export default function SearchBar({
  entityType,
  accession, setAccession,
  goId,      setGoId,
  ecNumber,  setEcNumber,
  iprId,     setIprId,
}) {
  const currentType = ENTITY_TYPES.find((e) => e.key === entityType) || ENTITY_TYPES[0];

  const setterMap = {
    protein:  setAccession,
    go:       setGoId,
    enzyme:   setEcNumber,
    interpro: setIprId,
  };

  const valueMap = {
    protein:  accession,
    go:       goId,
    enzyme:   ecNumber,
    interpro: iprId,
  };

  const setValue = setterMap[entityType] || setAccession;
  const value    = valueMap[entityType]  || accession;

  return (
    <article className="panel">
      <h2>Search</h2>
      <p className="panel-subtitle">
        Enter a <strong>{currentType.label}</strong> identifier to explore the graph.
      </p>

      <label htmlFor="main-search">{currentType.inputLabel}</label>
      <input
        id="main-search"
        key={entityType}
        type="text"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder={currentType.placeholder}
        autoComplete="off"
      />
    </article>
  );
}

