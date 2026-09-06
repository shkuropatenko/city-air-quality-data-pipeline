import { useEffect, useState } from "react";
import { getLocations } from "./api/airQualityApi";
import CitySelector from "./components/CitySelector";
import useAirQuality from "./hooks/useAirQuality";
import SummaryCards from "./components/SummaryCards";
import AirQualityChart from "./components/AirQualityChart";
import StatusMessage from "./components/StatusMessage";
import CityDetails from "./components/CityDetails";

import "./App.css";

function App() {
  const [locations, setLocations] = useState([]);
  const [locationsLoading, setLocationsLoading] = useState(true);
  const [locationsError, setLocationsError] = useState(null);

  const [selectedLocationId, setSelectedLocationId] = useState("");

  const {
    data: airQualityData,
    loading: airQualityLoading,
    error: airQualityError,
  } = useAirQuality(selectedLocationId);

  useEffect(() => {
    async function loadLocations() {
      try {
        setLocationsLoading(true);
        setLocationsError(null);

        const data = await getLocations();
        setLocations(data);
      } catch (err) {
        setLocationsError(err.message);
      } finally {
        setLocationsLoading(false);
      }
    }

    loadLocations();
  }, []);

  console.log(airQualityData);

  if (locationsLoading) {
    return <div>Loading locations...</div>;
  }

  if (locationsError) {
    return <div>Error: {locationsError}</div>;
  }

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">Environmental Data Platform</p>

          <h1 className="dashboard-title">City Air Tracker</h1>

          <p className="dashboard-subtitle">
            Explore current air-quality measurements and trends across monitored
            cities.
          </p>
        </div>
      </header>

      <section className="dashboard-panel">
        <div className="location-control">
          <label htmlFor="location-select">Select location</label>

          <CitySelector
            locations={locations}
            selectedLocationId={selectedLocationId}
            onLocationChange={setSelectedLocationId}
          />
        </div>
      </section>

      {!selectedLocationId && (
        <StatusMessage>
          Select a location to explore air-quality measurements and historical
          trends.
        </StatusMessage>
      )}

      {airQualityLoading && (
        <StatusMessage>Loading air quality data...</StatusMessage>
      )}

      {airQualityError && (
        <div className="status-message">Error: {airQualityError}</div>
      )}

      {airQualityData?.observations?.length > 0 && (
        <>
          <SummaryCards observations={airQualityData.observations} />
          <AirQualityChart observations={airQualityData.observations} />
        </>
      )}

      {airQualityData && (
        <CityDetails
          location={airQualityData.location}
          observations={airQualityData.observations}
        />
      )}

      {airQualityData && airQualityData.observations.length === 0 && (
        <StatusMessage>
          No air-quality observations are available for this location.
        </StatusMessage>
      )}
    </main>
  );
}

export default App;
