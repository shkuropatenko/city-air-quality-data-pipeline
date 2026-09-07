function CitySelector({ locations, selectedLocationId, onLocationChange }) {
  return (
    <select
      id="location-select"
      value={selectedLocationId}
      onChange={(event) => onLocationChange(event.target.value)}
    >
      <option value="">Select a city</option>
      {locations.map((location) => (
        <option key={location.id} value={location.id}>
          {location.city}
        </option>
      ))}
    </select>
  );
}

export default CitySelector;
