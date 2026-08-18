from pipeline.extract.location_validation import validate_locations


def test_valid_location():
  locations = [
    {
      "city": "Kyiv",
      "country_code": "UA",
      "state": "",
    }
  ]

  valid, errors = validate_locations(locations)

  assert len(valid) == 1
  assert len(errors) == 0


def test_missing_city():
  locations = [
    {
      "city": "",
      "country_code": "US",
      "state": "NY",
    }
  ]

  valid, errors = validate_locations(locations)

  assert len(valid) == 0
  assert errors[0] == "City is required"


def test_missing_country_code():
  locations = [
    {
      "city": "Paris",
      "country_code": "",
      "state": "",
    }
  ]

  valid, errors = validate_locations(locations)

  assert len(valid) == 0
  assert errors[0] == "Country code is required"


def test_invalid_country_code():
  locations = [
    {
      "city": "Los Angeles",
      "country_code": "USA",
      "state": "CA",
    }
  ]

  valid, errors = validate_locations(locations)

  assert len(valid) == 0
  assert errors[0] == "Country code must contain 2 characters"