import { useEffect, useState } from "react";
import { getLocations } from "./api/airQualityApi";
import CitySelector from "./components/CitySelector";
import useAirQuality from "./hooks/useAirQuality";

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
    <div>
      <h1>City Air Tracker</h1>

      <CitySelector
        locations={locations}
        selectedLocationId={selectedLocationId}
        onLocationChange={setSelectedLocationId}
      />

      {airQualityLoading && <p>Loading air quality data...</p>}

      {airQualityError && <p>Error: {airQualityError}</p>}

      {airQualityData && <pre>{JSON.stringify(airQualityData, null, 2)}</pre>}
    </div>
  );
}

export default App;
