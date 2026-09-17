import { useState, useEffect, useMemo, useCallback } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useObservations } from "./hooks/useObservations";
import LocationSelect from "./components/LocationSelect";
function App() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedLocationId, setSelectedLocationId] = useState("");

  const { observations, loadingObservations, observationsError } =
    useObservations(selectedLocationId);

  const handleLocationChange = useCallback((event) => {
    setSelectedLocationId(event.target.value);
  }, []);

  useEffect(() => {
    async function loadLocations() {
      try {
        const response = await fetch("/api/locations");

        if (!response.ok) {
          throw new Error("Failed to load locations");
        }

        const data = await response.json();

        setLocations(data.locations);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    }

    loadLocations();
  }, []);

  const chartData = useMemo(() => {
    return observations.map((observation) => {
      return {
        ...observation,
        time: new Date(observation.observed_at).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      };
    });
  }, [observations]);

  if (loading) {
    return <p>Loading...</p>;
  }
  if (error) {
    return <p>Error - {error}...</p>;
  }

  // console.log(observations);
  return (
    <>
      <h1>City Air Tracker</h1>
      <LocationSelect
        locations={locations}
        selectedLocationId={selectedLocationId}
        onLocationChange={handleLocationChange}
      />
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <Line dataKey="pm2_5" />
        </LineChart>
      </ResponsiveContainer>
    </>
  );
}

export default App;
