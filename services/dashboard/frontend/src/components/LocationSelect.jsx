import { memo } from "react";

function LocationSelect({ locations, selectedLocationId, onLocationChange }) {
  return (
    <select value={selectedLocationId} onChange={onLocationChange}>
      <option value="">Select a city</option>
      {locations.map((item) => {
        return (
          <option key={item.id} value={item.id}>
            {item.city}
          </option>
        );
      })}
    </select>
  );
}

export default memo(LocationSelect);
