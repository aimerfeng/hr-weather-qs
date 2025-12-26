"""
Pytest configuration and shared fixtures for AI Assistant Agent tests.
"""
import pytest
from hypothesis import settings

# Configure hypothesis for property-based testing
# Each property test runs 100 times as per design requirements
settings.register_profile("default", max_examples=100)
settings.load_profile("default")


@pytest.fixture
def mock_weather_data():
    """Fixture providing mock weather data for testing."""
    return {
        "city": "Beijing",
        "country": "CN",
        "temperature": 25.0,
        "feels_like": 27.0,
        "humidity": 60,
        "wind_speed": 10.5,
        "condition": "晴",
        "icon": "01d",
        "updated_at": "2024-01-01T12:00:00"
    }


@pytest.fixture
def mock_forecast_data():
    """Fixture providing mock forecast data for testing."""
    return [
        {
            "date": "2024-01-01",
            "day_of_week": "周一",
            "temp_min": 20.0,
            "temp_max": 28.0,
            "humidity": 55,
            "condition": "晴",
            "icon": "01d",
            "is_good_weather": True
        }
    ]
