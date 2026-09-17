import { useEffect, useState } from "react";

export function useObservations(selectedLocationId) {
  const [observations, setObservations] = useState([]);
  const [loadingObservations, setLoadingObservations] = useState(false);
  const [observationsError, setObservationsError] = useState(null);

  useEffect(() => {
    if (!selectedLocationId) {
      return;
    }
    const controller = new AbortController();
    async function loadObservations() {
      setLoadingObservations(true);

      try {
        const response = await fetch(
          `/api/locations/${selectedLocationId}/observations`,
          { signal: controller.signal },
        );
        if (!response.ok) {
          throw new Error("Failed to load observations");
        }
        const data = await response.json();

        setObservations(data.observations);
      } catch (error) {
        if (error.name !== "AbortError") {
          setObservationsError(error.message);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoadingObservations(false);
        }
      }
    }
    loadObservations();
    return () => {
      controller.abort();
    };
  }, [selectedLocationId]);

  return {
    observations,
    loadingObservations,
    observationsError,
  };
}
