export async function getLocations() {
  const response = await fetch("/api/locations");

  if (!response.ok) {
    throw new Error("Failed to load locations");
  }

  const data = await response.json();

  return data.locations;
}

export async function getLocationObservations(locationId) {
  const response = await fetch(`/api/locations/${locationId}/observations`);

  if (!response.ok) {
    throw new Error("Failed to load air quality data");
  }
  const data = await response.json();
  return data;
}
