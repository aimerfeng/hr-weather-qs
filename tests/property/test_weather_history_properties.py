"""
Property-based tests for Weather History models.

Feature: ai-assistant-agent
Property 4: Weather History Persistence Round-Trip
Validates: Requirements 2.1, 2.4

For any weather query, saving to history and then reloading from file 
SHALL produce equivalent history data.
"""

import pytest
import tempfile
import os
from datetime import datetime
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from terminal.models import WeatherData, WeatherHistory, WeatherHistoryEntry


# Custom strategies for generating test data
@st.composite
def weather_data_strategy(draw):
    """Generate random valid WeatherData objects."""
    return WeatherData(
        city=draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('L', 'N'),
            whitelist_characters=' -'
        )).filter(lambda x: x.strip())),
        country=draw(st.text(min_size=0, max_size=10, alphabet=st.characters(
            whitelist_categories=('L',)
        ))),
        temperature=draw(st.floats(min_value=-50.0, max_value=60.0, allow_nan=False)),
        feels_like=draw(st.floats(min_value=-50.0, max_value=60.0, allow_nan=False)),
        humidity=draw(st.integers(min_value=0, max_value=100)),
        wind_speed=draw(st.floats(min_value=0.0, max_value=200.0, allow_nan=False)),
        condition=draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
        icon=draw(st.text(min_size=0, max_size=10)),
        updated_at=datetime.now()
    )


@st.composite
def city_name_strategy(draw):
    """Generate random valid city names."""
    return draw(st.text(
        min_size=1, 
        max_size=50, 
        alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters=' -')
    ).filter(lambda x: x.strip()))


class TestWeatherHistoryRoundTrip:
    """
    Property 4: Weather History Persistence Round-Trip
    
    For any weather query, saving to history and then reloading from file 
    SHALL produce equivalent history data.
    
    Validates: Requirements 2.1, 2.4
    """
    
    @given(weather_data=weather_data_strategy())
    @settings(max_examples=100)
    def test_single_entry_round_trip(self, weather_data: WeatherData):
        """
        Feature: ai-assistant-agent, Property 4: Weather History Persistence Round-Trip
        
        For any single weather entry, saving and reloading produces equivalent data.
        """
        # Create history and add entry
        history = WeatherHistory()
        history.add_entry(weather_data.city, weather_data)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            history.save_to_file(temp_path)
            
            # Reload from file
            loaded_history = WeatherHistory.load_from_file(temp_path)
            
            # Verify equivalence
            assert len(loaded_history.entries) == len(history.entries)
            assert len(loaded_history.entries) == 1
            
            original_entry = history.entries[0]
            loaded_entry = loaded_history.entries[0]
            
            assert loaded_entry.city == original_entry.city
            assert loaded_entry.query_count == original_entry.query_count
            assert loaded_entry.last_weather.city == original_entry.last_weather.city
            assert loaded_entry.last_weather.temperature == original_entry.last_weather.temperature
            assert loaded_entry.last_weather.humidity == original_entry.last_weather.humidity
            assert loaded_entry.last_weather.wind_speed == original_entry.last_weather.wind_speed
            assert loaded_entry.last_weather.condition == original_entry.last_weather.condition
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @given(weather_data_list=st.lists(weather_data_strategy(), min_size=1, max_size=15))
    @settings(max_examples=100)
    def test_multiple_entries_round_trip(self, weather_data_list):
        """
        Feature: ai-assistant-agent, Property 4: Weather History Persistence Round-Trip
        
        For any sequence of weather entries, saving and reloading produces equivalent data.
        """
        # Create history and add entries
        history = WeatherHistory()
        for weather_data in weather_data_list:
            history.add_entry(weather_data.city, weather_data)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            history.save_to_file(temp_path)
            
            # Reload from file
            loaded_history = WeatherHistory.load_from_file(temp_path)
            
            # Verify equivalence
            assert len(loaded_history.entries) == len(history.entries)
            
            for original, loaded in zip(history.entries, loaded_history.entries):
                assert loaded.city == original.city
                assert loaded.query_count == original.query_count
                assert loaded.last_weather.city == original.last_weather.city
                assert loaded.last_weather.temperature == original.last_weather.temperature
                assert loaded.last_weather.humidity == original.last_weather.humidity
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @given(weather_data=weather_data_strategy())
    @settings(max_examples=100)
    def test_json_serialization_round_trip(self, weather_data: WeatherData):
        """
        Feature: ai-assistant-agent, Property 4: Weather History Persistence Round-Trip
        
        For any weather history, JSON serialization and deserialization produces equivalent data.
        """
        # Create history and add entry
        history = WeatherHistory()
        history.add_entry(weather_data.city, weather_data)
        
        # Serialize to JSON
        json_str = history.to_json()
        
        # Deserialize from JSON
        loaded_history = WeatherHistory.from_json(json_str)
        
        # Verify equivalence
        assert len(loaded_history.entries) == len(history.entries)
        
        original_entry = history.entries[0]
        loaded_entry = loaded_history.entries[0]
        
        assert loaded_entry.city == original_entry.city
        assert loaded_entry.query_count == original_entry.query_count
        assert loaded_entry.last_weather.temperature == original_entry.last_weather.temperature
