def validate_location(location):
  city = location.get("city", "").strip()
  country_code = location.get("country_code", "").strip().upper()
  state = location.get("state", "").strip()

  if not city:
    return None, "City is required"

  if not country_code:
    return None, "Country code is required"

  if len(country_code) != 2:
    return None, "Country code must contain 2 characters"

  validated_location = {
    "city": city,
    "country_code": country_code,
    "state": state,
  }

  return validated_location, None