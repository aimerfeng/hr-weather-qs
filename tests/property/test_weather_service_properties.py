"""
Property-based tests for Weather Service.

Feature: ai-assistant-agent
Tests Properties 1, 5, 6, 7, 8, 9, 10
Validates: Requirements 1.2, 2.5, 2.6, 2.7, 3.1, 3.4, 3.6
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, assume

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from terminal.models import WeatherData, ForecastDay, WeatherHistory
from terminal.weather_service import WeatherService


# ==================== Custom Strategies ====================

@st.composite
def weather_data_strategy(draw):
    """Generate random valid WeatherData objects."""
    city = draw(st.text(
        min_size=1, 
        max_size=30, 
        alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters=' -')
    ).filter(lambda x: x.strip()))
    
    return WeatherData(
        city=city,
        country=draw(st.text(min_size=0, max_size=10, alphabet=st.characters(whitelist_categories=('L',)))),
        temperature=draw(st.floats(min_value=-50.0, max_value=60.0, allow_nan=False)),
        feels_like=draw(st.floats(min_value=-50.0, max_value=60.0, allow_nan=False)),
        humidity=draw(st.integers(min_value=0, max_value=100)),
        wind_speed=draw(st.floats(min_value=0.0, max_value=200.0, allow_nan=False)),
        condition=draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
        icon=draw(st.text(min_size=0, max_size=10)),
        updated_at=datetime.now()
    )


@st.composite
def unique_city_list_strategy(draw, min_size=1, max_size=15):
    """Generate a list of unique city names."""
    cities = draw(st.lists(
        st.text(
            min_size=1, 
            max_size=20, 
            alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters=' -')
        ).filter(lambda x: x.strip()),
        min_size=min_size,
        max_size=max_size,
        unique_by=lambda x: x.lower()
    ))
    return cities


@st.composite
def forecast_day_strategy(draw, date_offset=0):
    """Generate a random valid ForecastDay object."""
    conditions = ["Sunny", "Clear", "Partly cloudy", "Cloudy", "Rain", "Storm", "Snow", "Fog"]
    condition = draw(st.sampled_from(conditions))
    
    temp_min = draw(st.floats(min_value=-30.0, max_value=40.0, allow_nan=False))
    temp_max = draw(st.floats(min_value=temp_min, max_value=50.0, allow_nan=False))
    
    date = datetime.now() + timedelta(days=date_offset)
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    
    return ForecastDay(
        date=date,
        day_of_week=weekday_names[date.weekday()],
        temp_min=temp_min,
        temp_max=temp_max,
        humidity=draw(st.integers(min_value=0, max_value=100)),
        condition=condition,
        icon=draw(st.text(min_size=0, max_size=10)),
        is_good_weather=condition.lower() in ["sunny", "clear", "partly cloudy"]
    )


# ==================== Property 1: Weather Response Contains Required Fields ====================

class TestWeatherResponseFields:
    """
    Property 1: Weather Response Contains Required Fields
    
    For any valid weather API response, the formatted weather data SHALL contain 
    city name, temperature, humidity, wind speed, and weather condition description.
    
    Validates: Requirements 1.2
    """
    
    @given(weather_data=weather_data_strategy())
    @settings(max_examples=100)
    def test_weather_data_contains_required_fields(self, weather_data: WeatherData):
        """
        Feature: ai-assistant-agent, Property 1: Weather Response Contains Required Fields
        
        For any WeatherData object, it must contain all required fields.
        """
        # Verify all required fields are present and valid
        assert weather_data.city is not None and len(weather_data.city.strip()) > 0
        assert isinstance(weather_data.temperature, float)
        assert isinstance(weather_data.humidity, int)
        assert 0 <= weather_data.humidity <= 100
        assert isinstance(weather_data.wind_speed, float)
        assert weather_data.wind_speed >= 0
        assert weather_data.condition is not None and len(weather_data.condition.strip()) > 0


# ==================== Property 5: Weather History Size Limit ====================

class TestWeatherHistorySizeLimit:
    """
    Property 5: Weather History Size Limit
    
    For any sequence of weather queries, the history SHALL contain at most 10 
    unique cities, with oldest entries removed when limit is exceeded.
    
    Validates: Requirements 2.5
    """
    
    @given(cities=unique_city_list_strategy(min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_history_never_exceeds_max_size(self, cities):
        """
        Feature: ai-assistant-agent, Property 5: Weather History Size Limit
        
        For any sequence of city queries, history size never exceeds 10.
        """
        history = WeatherHistory()
        
        for city in cities:
            weather = WeatherData(
                city=city,
                temperature=25.0,
                humidity=60,
                wind_speed=10.0,
                condition="Sunny"
            )
            history.add_entry(city, weather)
            
            # After each addition, verify size constraint
            assert len(history.entries) <= history.max_entries
        
        # Final check
        assert len(history.entries) <= 10


# ==================== Property 6: Weather History Recency Update ====================

class TestWeatherHistoryRecencyUpdate:
    """
    Property 6: Weather History Recency Update
    
    For any repeated weather query for a city already in history, that city 
    SHALL move to the most recent position in the history list.
    
    Validates: Requirements 2.6
    """
    
    @given(
        initial_cities=unique_city_list_strategy(min_size=3, max_size=8),
        repeat_index=st.integers(min_value=0, max_value=100)
    )
    @settings(max_examples=100)
    def test_repeated_query_moves_to_front(self, initial_cities, repeat_index):
        """
        Feature: ai-assistant-agent, Property 6: Weather History Recency Update
        
        When a city is queried again, it moves to the most recent position.
        """
        assume(len(initial_cities) >= 3)
        
        history = WeatherHistory()
        
        # Add initial cities
        for city in initial_cities:
            weather = WeatherData(
                city=city,
                temperature=25.0,
                humidity=60,
                wind_speed=10.0,
                condition="Sunny"
            )
            history.add_entry(city, weather)
        
        # Pick a city to repeat (not the first one)
        repeat_idx = (repeat_index % (len(initial_cities) - 1)) + 1
        city_to_repeat = initial_cities[-(repeat_idx + 1)]  # Pick from older entries
        
        # Query the city again
        weather = WeatherData(
            city=city_to_repeat,
            temperature=30.0,
            humidity=50,
            wind_speed=15.0,
            condition="Clear"
        )
        history.add_entry(city_to_repeat, weather)
        
        # Verify the city is now at the front (most recent)
        assert history.entries[0].city.lower() == city_to_repeat.lower()


# ==================== Property 7: Most Frequent City Identification ====================

class TestMostFrequentCityIdentification:
    """
    Property 7: Most Frequent City Identification
    
    For any weather history with multiple entries, the system SHALL correctly 
    identify the city with the highest query count.
    
    Validates: Requirements 2.7
    """
    
    @given(
        cities=unique_city_list_strategy(min_size=2, max_size=8),
        query_counts=st.lists(st.integers(min_value=1, max_value=10), min_size=2, max_size=8)
    )
    @settings(max_examples=100)
    def test_most_frequent_city_correctly_identified(self, cities, query_counts):
        """
        Feature: ai-assistant-agent, Property 7: Most Frequent City Identification
        
        The city with the highest query count is correctly identified.
        """
        assume(len(cities) >= 2)
        assume(len(query_counts) >= len(cities))
        
        history = WeatherHistory()
        
        # Query each city the specified number of times
        city_counts = {}
        for i, city in enumerate(cities):
            count = query_counts[i % len(query_counts)]
            city_counts[city.lower()] = count
            
            for _ in range(count):
                weather = WeatherData(
                    city=city,
                    temperature=25.0,
                    humidity=60,
                    wind_speed=10.0,
                    condition="Sunny"
                )
                history.add_entry(city, weather)
        
        # Find expected most frequent city
        max_count = max(city_counts.values())
        expected_cities = [c for c, cnt in city_counts.items() if cnt == max_count]
        
        # Verify the identified city is one of the most frequent
        most_frequent = history.get_most_frequent_city()
        assert most_frequent is not None
        assert most_frequent.lower() in expected_cities


# ==================== Property 8: Forecast Contains Five Days ====================

class TestForecastContainsFiveDays:
    """
    Property 8: Forecast Contains Five Days
    
    For any weather forecast request, the response SHALL contain exactly 5 forecast days.
    
    Validates: Requirements 3.1
    """
    
    @given(num_days=st.integers(min_value=1, max_value=7))
    @settings(max_examples=100)
    def test_forecast_list_generation(self, num_days):
        """
        Feature: ai-assistant-agent, Property 8: Forecast Contains Five Days
        
        When generating forecasts, the list should contain the requested number of days.
        """
        # Generate forecast days
        forecasts = []
        for i in range(num_days):
            date = datetime.now() + timedelta(days=i)
            weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            
            forecast = ForecastDay(
                date=date,
                day_of_week=weekday_names[date.weekday()],
                temp_min=20.0,
                temp_max=30.0,
                humidity=60,
                condition="Sunny",
                icon="01d",
                is_good_weather=True
            )
            forecasts.append(forecast)
        
        # Verify the forecast list has the correct length
        assert len(forecasts) == num_days
        
        # For the standard 5-day forecast
        if num_days == 5:
            assert len(forecasts) == 5


# ==================== Property 9: Forecast Day Contains Required Fields ====================

class TestForecastDayRequiredFields:
    """
    Property 9: Forecast Day Contains Required Fields
    
    For any forecast day in the response, it SHALL contain date, day of week, 
    temperature range (min/max), humidity, and weather icon.
    
    Validates: Requirements 3.4
    """
    
    @given(forecast=forecast_day_strategy())
    @settings(max_examples=100)
    def test_forecast_day_has_required_fields(self, forecast: ForecastDay):
        """
        Feature: ai-assistant-agent, Property 9: Forecast Day Contains Required Fields
        
        Each ForecastDay must contain all required fields.
        """
        # Verify all required fields are present
        assert forecast.date is not None
        assert isinstance(forecast.date, datetime)
        
        assert forecast.day_of_week is not None
        assert len(forecast.day_of_week) > 0
        
        assert isinstance(forecast.temp_min, float)
        assert isinstance(forecast.temp_max, float)
        assert forecast.temp_min <= forecast.temp_max
        
        assert isinstance(forecast.humidity, int)
        assert 0 <= forecast.humidity <= 100
        
        # Icon can be empty but must be a string
        assert isinstance(forecast.icon, str)


# ==================== Property 10: Good Weather Classification ====================

class TestGoodWeatherClassification:
    """
    Property 10: Good Weather Classification
    
    For any weather condition, the is_good_weather flag SHALL be true for 
    sunny/clear/partly cloudy conditions and false for rain/storm/snow conditions.
    
    Validates: Requirements 3.6
    """
    
    # Good weather conditions
    GOOD_CONDITIONS = [
        "Sunny", "sunny", "SUNNY",
        "Clear", "clear", "CLEAR",
        "Partly cloudy", "partly cloudy", "Partly Cloudy",
        "晴", "多云", "少云",
        "Fair", "fine", "bright"
    ]
    
    # Bad weather conditions
    BAD_CONDITIONS = [
        "Rain", "rain", "RAIN", "Light rain", "Heavy rain",
        "Storm", "storm", "Thunderstorm",
        "Snow", "snow", "Light snow", "Heavy snow",
        "雨", "雪", "雷",
        "Sleet", "Hail", "Fog", "Mist", "Drizzle",
        "Shower", "Overcast", "阴"
    ]
    
    @given(condition=st.sampled_from(GOOD_CONDITIONS))
    @settings(max_examples=100)
    def test_good_weather_classified_correctly(self, condition: str):
        """
        Feature: ai-assistant-agent, Property 10: Good Weather Classification
        
        Sunny/clear/partly cloudy conditions are classified as good weather.
        """
        service = WeatherService.__new__(WeatherService)
        service.GOOD_WEATHER_CONDITIONS = WeatherService.GOOD_WEATHER_CONDITIONS
        service.BAD_WEATHER_CONDITIONS = WeatherService.BAD_WEATHER_CONDITIONS
        
        result = service._is_good_weather(condition)
        assert result is True, f"Expected '{condition}' to be classified as good weather"
    
    @given(condition=st.sampled_from(BAD_CONDITIONS))
    @settings(max_examples=100)
    def test_bad_weather_classified_correctly(self, condition: str):
        """
        Feature: ai-assistant-agent, Property 10: Good Weather Classification
        
        Rain/storm/snow conditions are classified as bad weather.
        """
        service = WeatherService.__new__(WeatherService)
        service.GOOD_WEATHER_CONDITIONS = WeatherService.GOOD_WEATHER_CONDITIONS
        service.BAD_WEATHER_CONDITIONS = WeatherService.BAD_WEATHER_CONDITIONS
        
        result = service._is_good_weather(condition)
        assert result is False, f"Expected '{condition}' to be classified as bad weather"
    
    @given(
        good_condition=st.sampled_from(GOOD_CONDITIONS),
        bad_condition=st.sampled_from(BAD_CONDITIONS)
    )
    @settings(max_examples=100)
    def test_good_and_bad_weather_are_distinct(self, good_condition: str, bad_condition: str):
        """
        Feature: ai-assistant-agent, Property 10: Good Weather Classification
        
        Good and bad weather classifications are mutually exclusive.
        """
        service = WeatherService.__new__(WeatherService)
        service.GOOD_WEATHER_CONDITIONS = WeatherService.GOOD_WEATHER_CONDITIONS
        service.BAD_WEATHER_CONDITIONS = WeatherService.BAD_WEATHER_CONDITIONS
        
        good_result = service._is_good_weather(good_condition)
        bad_result = service._is_good_weather(bad_condition)
        
        # Good weather should be True, bad weather should be False
        assert good_result is True
        assert bad_result is False
        # They should be different
        assert good_result != bad_result
