function CitySelector({ locations, selectedLocationId, onLocationChange }) {
  console.log(locations);

  return (
    <select
      value={selectedLocationId}
      onChange={(event) => onLocationChange(event.target.value)}
    >
      {locations.map((location) => (
        <option key={location.id} value={location.id}>
          {location.city}
        </option>
      ))}
    </select>
  );
}

export default CitySelector;
