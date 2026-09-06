function SummaryCards({ observations }) {
  if (!observations?.length) {
    return null;
  }

  const latestObservation = observations[observations.length - 1];

  const metrics = [
    {
      label: "Air Quality Index",
      value: latestObservation.aqi,
      unit: "",
    },
    {
      label: "PM2.5",
      value: latestObservation.pm2_5,
      unit: "µg/m³",
    },
    {
      label: "PM10",
      value: latestObservation.pm10,
      unit: "µg/m³",
    },
    {
      label: "Ozone",
      value: latestObservation.o3,
      unit: "µg/m³",
    },
  ];

  return (
    <section className="summary-grid">
      {metrics.map((metric) => (
        <article className="summary-card" key={metric.label}>
          <p className="summary-label">{metric.label}</p>

          <div className="summary-value-row">
            <span className="summary-value">{metric.value}</span>
            {metric.unit && <span className="summary-unit">{metric.unit}</span>}
          </div>
        </article>
      ))}
    </section>
  );
}

export default SummaryCards;
