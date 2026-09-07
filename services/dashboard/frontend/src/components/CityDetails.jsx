function CityDetails({ location, observations }) {
  if (!location || !observations?.length) {
    return null;
  }

  const latestObservation = observations[observations.length - 1];

  const latestTime = new Date(latestObservation.observed_at).toLocaleString(
    [],
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  );

  return (
    <section className="dashboard-panel city-details">
      <div>
        <p className="section-eyebrow">Location details</p>

        <h2>
          {location.city}, {location.country_code}
        </h2>
      </div>

      <div className="city-details-grid">
        <div>
          <span className="detail-label">Latitude</span>
          <strong>{Number(location.latitude).toFixed(4)}</strong>
        </div>

        <div>
          <span className="detail-label">Longitude</span>
          <strong>{Number(location.longitude).toFixed(4)}</strong>
        </div>

        <div>
          <span className="detail-label">Latest observation</span>
          <strong>{latestTime}</strong>
        </div>
      </div>
    </section>
  );
}

export default CityDetails;
