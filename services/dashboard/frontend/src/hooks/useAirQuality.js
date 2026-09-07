import { useEffect, useState } from "react";
import { getLocationObservations } from "../api/airQualityApi";

function useAirQuality(selectedLocationId) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!selectedLocationId) {
      return;
    }

    async function loadObservations() {
      try {
        setLoading(true);
        setError(null);

        const result = await getLocationObservations(selectedLocationId);

        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadObservations();
  }, [selectedLocationId]);

  return { data, loading, error };
}

export default useAirQuality;
