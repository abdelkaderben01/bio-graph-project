import { PROJECT_STATS, PROJECT_STATS_LABELS } from "../projectStats";

function formatNumber(value) {
  return new Intl.NumberFormat("fr-FR").format(value);
}

export default function ProjectStatsPanel() {
  return (
    <section className="panel stats-panel">
      <h2>Project statistics</h2>
      <p className="panel-subtitle">Vue d'ensemble du graphe bio : proteines, ontologies, similarite, predictions.</p>

      <div className="stats-grid">
        {PROJECT_STATS_LABELS.map(([key, label]) => (
          <article className="stat-card" key={key}>
            <span>{label}</span>
            <strong>{formatNumber(PROJECT_STATS[key])}</strong>
          </article>
        ))}
      </div>
    </section>
  );
}
