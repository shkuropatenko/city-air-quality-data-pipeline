import { useEffect, useState } from "react";
import { getLocations } from "./api/airQualityApi";
import CitySelector from "./components/CitySelector";

import "./App.css";

function App() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLocationId, setSelectedLocationId] = useState("");

  useEffect(() => {
    async function loadLocations() {
      try {
        setLoading(true);
        setError(null);

        const data = await getLocations();

        setLocations(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadLocations();
  }, []);

  console.log(locations);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <CitySelector
        locations={locations}
        selectedLocationId={selectedLocationId}
        onLocationChange={setSelectedLocationId}
      />
    </div>
  );
}

export default App;
