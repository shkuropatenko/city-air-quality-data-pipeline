import { useEffect, useState } from "react";
import { getLocationObservations } from "../api/airQualityApi";

function useAirQuality(selectedLocationId) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let ignore = false;

    if (!selectedLocationId) {
      return () => {
        ignore = true;
      };
    }

    async function loadObservations() {
      try {
        setLoading(true);
        setError(null);

        const result = await getLocationObservations(selectedLocationId);

        if (!ignore) {
          setData(result);
        }
      } catch (err) {
        if (!ignore) {
          setError(err.message);
        }
      } finally {
        if (!ignore) {
          setLoading(false);
        }
      }
    }

    loadObservations();

    return () => {
      ignore = true;
    };
  }, [selectedLocationId]);

  return {
    data: selectedLocationId ? data : null,
    loading: selectedLocationId ? loading : false,
    error: selectedLocationId ? error : null,
  };
}

export default useAirQuality;
