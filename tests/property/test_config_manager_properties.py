"""
Property-based tests for Config Manager.

Feature: ai-assistant-agent
Tests Properties 17, 18, 19
Validates: Requirements 8.2, 8.6, 8.7
"""

import pytest
import tempfile
import os
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from terminal.models import APIConfig, ValidationResult
from terminal.config_manager import ConfigManager, ProviderPreset


# ==================== Custom Strategies ====================

@st.composite
def valid_https_url_strategy(draw):
    """Generate valid HTTPS URLs."""
    domains = [
        "api.openai.com",
        "api.deepseek.com",
        "dashscope.aliyuncs.com",
        "api.example.com",
        "localhost",
        "127.0.0.1",
    ]
    
    domain = draw(st.sampled_from(domains))
    
    # Add optional port for localhost/IP
    if domain in ["localhost", "127.0.0.1"]:
        port = draw(st.integers(min_value=1000, max_value=65535))
        domain = f"{domain}:{port}"
    
    paths = ["", "/v1", "/api", "/api/v1", "/compatible-mode/v1"]
    path = draw(st.sampled_from(paths))
    
    protocol = draw(st.sampled_from(["https://", "http://"]))
    
    return f"{protocol}{domain}{path}"


@st.composite
def invalid_url_strategy(draw):
    """Generate invalid URLs."""
    invalid_urls = [
        "",
        "   ",
        "not-a-url",
        "ftp://example.com",
        "://missing-protocol.com",
        "http://",
        "https://",
        "http:///path",
        "just-text",
        "http://invalid url with spaces.com",
        "http://[invalid",
    ]
    return draw(st.sampled_from(invalid_urls))


@st.composite
def valid_api_key_strategy(draw):
    """Generate valid API keys."""
    prefixes = ["sk-", "api-", "key-", ""]
    prefix = draw(st.sampled_from(prefixes))
    
    # Generate random alphanumeric string
    key_body = draw(st.text(
        min_size=10,
        max_size=50,
        alphabet=st.characters(whitelist_categories=('L', 'N'))
    ))
    
    return f"{prefix}{key_body}"


@st.composite
def invalid_api_key_strategy(draw):
    """Generate invalid API keys."""
    invalid_keys = [
        "",
        "   ",
        "\t",
        "\n",
    ]
    return draw(st.sampled_from(invalid_keys))


@st.composite
def valid_model_strategy(draw):
    """Generate valid model names."""
    models = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4o",
        "gpt-4o-mini",
        "deepseek-chat",
        "deepseek-coder",
        "qwen-turbo",
        "qwen-plus",
        "qwen-max",
        "custom-model-v1",
    ]
    return draw(st.sampled_from(models))


@st.composite
def valid_provider_strategy(draw):
    """Generate valid provider names."""
    providers = ["openai", "deepseek", "qwen", "custom"]
    return draw(st.sampled_from(providers))


@st.composite
def valid_api_config_strategy(draw):
    """Generate valid APIConfig objects."""
    provider = draw(valid_provider_strategy())
    base_url = draw(valid_https_url_strategy())
    api_key = draw(valid_api_key_strategy())
    model = draw(valid_model_strategy())
    
    return APIConfig(
        provider=provider,
        base_url=base_url,
        api_key=api_key,
        model=model
    )


# ==================== Property 17: API URL Validation ====================

class TestAPIURLValidation:
    """
    Property 17: API URL Validation
    
    For any API base URL input, the validation SHALL correctly identify valid 
    HTTPS URLs and reject invalid formats.
    
    Validates: Requirements 8.2
    """
    
    @given(url=valid_https_url_strategy())
    @settings(max_examples=100)
    def test_valid_urls_are_accepted(self, url: str):
        """
        Feature: ai-assistant-agent, Property 17: API URL Validation
        
        Valid HTTP/HTTPS URLs should be accepted.
        """
        manager = ConfigManager.__new__(ConfigManager)
        manager.PRESETS = ConfigManager.PRESETS
        
        result = manager._validate_url(url)
        
        assert result.is_valid is True, f"Expected URL '{url}' to be valid, but got error: {result.error_message}"
    
    @given(url=invalid_url_strategy())
    @settings(max_examples=100)
    def test_invalid_urls_are_rejected(self, url: str):
        """
        Feature: ai-assistant-agent, Property 17: API URL Validation
        
        Invalid URLs should be rejected with an error message.
        """
        manager = ConfigManager.__new__(ConfigManager)
        manager.PRESETS = ConfigManager.PRESETS
        
        result = manager._validate_url(url)
        
        assert result.is_valid is False, f"Expected URL '{url}' to be invalid"
        assert result.error_message is not None
        assert len(result.error_message) > 0
    
    @given(
        valid_url=valid_https_url_strategy(),
        invalid_url=invalid_url_strategy()
    )
    @settings(max_examples=100)
    def test_valid_and_invalid_urls_are_distinct(self, valid_url: str, invalid_url: str):
        """
        Feature: ai-assistant-agent, Property 17: API URL Validation
        
        Valid and invalid URLs should have different validation results.
        """
        manager = ConfigManager.__new__(ConfigManager)
        manager.PRESETS = ConfigManager.PRESETS
        
        valid_result = manager._validate_url(valid_url)
        invalid_result = manager._validate_url(invalid_url)
        
        assert valid_result.is_valid is True
        assert invalid_result.is_valid is False
        assert valid_result.is_valid != invalid_result.is_valid


# ==================== Property 18: API Config Persistence Round-Trip ====================

class TestAPIConfigPersistenceRoundTrip:
    """
    Property 18: API Config Persistence Round-Trip
    
    For any API configuration saved to storage, reloading SHALL produce 
    equivalent configuration data.
    
    Validates: Requirements 8.6
    """
    
    @given(config=valid_api_config_strategy())
    @settings(max_examples=100)
    def test_config_json_round_trip(self, config: APIConfig):
        """
        Feature: ai-assistant-agent, Property 18: API Config Persistence Round-Trip
        
        Serializing to JSON and deserializing should produce equivalent config.
        """
        # Serialize to JSON
        json_str = config.to_json()
        
        # Deserialize from JSON
        loaded_config = APIConfig.from_json(json_str)
        
        # Verify equivalence
        assert loaded_config.provider == config.provider
        assert loaded_config.base_url == config.base_url
        assert loaded_config.api_key == config.api_key
        assert loaded_config.model == config.model
    
    @given(config=valid_api_config_strategy())
    @settings(max_examples=100)
    def test_config_file_round_trip(self, config: APIConfig):
        """
        Feature: ai-assistant-agent, Property 18: API Config Persistence Round-Trip
        
        Saving to file and loading should produce equivalent config.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test_config.json")
            
            # Save to file
            config.save_to_file(filepath)
            
            # Verify file exists
            assert os.path.exists(filepath)
            
            # Load from file
            loaded_config = APIConfig.load_from_file(filepath)
            
            # Verify equivalence
            assert loaded_config.provider == config.provider
            assert loaded_config.base_url == config.base_url
            assert loaded_config.api_key == config.api_key
            assert loaded_config.model == config.model
    
    @given(config=valid_api_config_strategy())
    @settings(max_examples=100)
    def test_config_manager_round_trip(self, config: APIConfig):
        """
        Feature: ai-assistant-agent, Property 18: API Config Persistence Round-Trip
        
        Using ConfigManager to save and load should produce equivalent config.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "config.json")
            
            # Create manager and save config
            manager = ConfigManager(config_file=filepath)
            manager.update_config(config)
            
            # Create new manager and load config
            new_manager = ConfigManager(config_file=filepath)
            loaded_config = new_manager.get_config()
            
            # Verify equivalence
            assert loaded_config.provider == config.provider
            assert loaded_config.base_url == config.base_url
            assert loaded_config.api_key == config.api_key
            assert loaded_config.model == config.model


# ==================== Property 19: Invalid Config Error Specificity ====================

class TestInvalidConfigErrorSpecificity:
    """
    Property 19: Invalid Config Error Specificity
    
    For any invalid API configuration (missing key, invalid URL, wrong model), 
    the error message SHALL specify which field is invalid.
    
    Validates: Requirements 8.7
    """
    
    @given(
        base_url=valid_https_url_strategy(),
        model=valid_model_strategy()
    )
    @settings(max_examples=100)
    def test_missing_api_key_error_is_specific(self, base_url: str, model: str):
        """
        Feature: ai-assistant-agent, Property 19: Invalid Config Error Specificity
        
        Missing API key should produce a specific error message.
        """
        config = APIConfig(
            provider="openai",
            base_url=base_url,
            api_key="",  # Empty API key
            model=model
        )
        
        manager = ConfigManager.__new__(ConfigManager)
        manager.PRESETS = ConfigManager.PRESETS
        
        result = manager.validate_config(config)
        
        assert result.is_valid is False
        assert result.error_message is not None
        # Error message should mention API Key
        assert "API Key" in result.error_message or "api_key" in result.error_message.lower()
    
    @given(
        api_key=valid_api_key_strategy(),
        model=valid_model_strategy()
    )
    @settings(max_examples=100)
    def test_invalid_url_error_is_specific(self, api_key: str, model: str):
        """
        Feature: ai-assistant-agent, Property 19: Invalid Config Error Specificity
        
        Invalid URL should produce a specific error message.
        """
        config = APIConfig(
            provider="openai",
            base_url="not-a-valid-url",  # Invalid URL
            api_key=api_key,
            model=model
        )
        
        manager = ConfigManager.__new__(ConfigManager)
        manager.PRESETS = ConfigManager.PRESETS
        
        result = manager.validate_config(config)
        
        assert result.is_valid is False
        assert result.error_message is not None
        # Error message should mention URL
        assert "URL" in result.error_message or "url" in result.error_message.lower()
    
    @given(
        base_url=valid_https_url_strategy(),
        api_key=valid_api_key_strategy()
    )
    @settings(max_examples=100)
    def test_missing_model_error_is_specific(self, base_url: str, api_key: str):
        """
        Feature: ai-assistant-agent, Property 19: Invalid Config Error Specificity
        
        Missing model should produce a specific error message.
        """
        config = APIConfig(
            provider="openai",
            base_url=base_url,
            api_key=api_key,
            model=""  # Empty model
        )
        
        manager = ConfigManager.__new__(ConfigManager)
        manager.PRESETS = ConfigManager.PRESETS
        
        result = manager.validate_config(config)
        
        assert result.is_valid is False
        assert result.error_message is not None
        # Error message should mention model
        assert "模型" in result.error_message or "model" in result.error_message.lower()
    
    @given(config=valid_api_config_strategy())
    @settings(max_examples=100)
    def test_valid_config_has_no_error(self, config: APIConfig):
        """
        Feature: ai-assistant-agent, Property 19: Invalid Config Error Specificity
        
        Valid config should not produce any error message.
        """
        manager = ConfigManager.__new__(ConfigManager)
        manager.PRESETS = ConfigManager.PRESETS
        
        result = manager.validate_config(config)
        
        assert result.is_valid is True
        assert result.error_message is None
    
    @given(
        base_url=valid_https_url_strategy(),
        api_key=valid_api_key_strategy(),
        model=valid_model_strategy()
    )
    @settings(max_examples=100)
    def test_missing_provider_error_is_specific(self, base_url: str, api_key: str, model: str):
        """
        Feature: ai-assistant-agent, Property 19: Invalid Config Error Specificity
        
        Missing provider should produce a specific error message.
        """
        config = APIConfig(
            provider="",  # Empty provider
            base_url=base_url,
            api_key=api_key,
            model=model
        )
        
        manager = ConfigManager.__new__(ConfigManager)
        manager.PRESETS = ConfigManager.PRESETS
        
        result = manager.validate_config(config)
        
        assert result.is_valid is False
        assert result.error_message is not None
        # Error message should mention provider
        assert "提供商" in result.error_message or "provider" in result.error_message.lower()


# ==================== Additional Tests for ConfigManager ====================

class TestConfigManagerPresets:
    """
    Additional tests for ConfigManager preset functionality.
    """
    
    @given(provider=st.sampled_from(["openai", "deepseek", "qwen"]))
    @settings(max_examples=100)
    def test_preset_providers_have_required_fields(self, provider: str):
        """
        Each preset provider should have all required fields.
        """
        manager = ConfigManager.__new__(ConfigManager)
        manager.PRESETS = ConfigManager.PRESETS
        
        preset = manager.get_preset(provider)
        
        assert preset is not None
        assert preset.name == provider
        assert len(preset.display_name) > 0
        assert len(preset.base_url) > 0
        assert len(preset.models) > 0
        assert preset.default_model in preset.models
    
    @given(
        provider=st.sampled_from(["openai", "deepseek", "qwen"]),
        api_key=valid_api_key_strategy()
    )
    @settings(max_examples=100)
    def test_create_config_from_preset(self, provider: str, api_key: str):
        """
        Creating config from preset should use preset values.
        """
        manager = ConfigManager.__new__(ConfigManager)
        manager.PRESETS = ConfigManager.PRESETS
        
        config = manager.create_config_from_preset(provider, api_key)
        preset = manager.get_preset(provider)
        
        assert config.provider == provider
        assert config.base_url == preset.base_url
        assert config.api_key == api_key
        assert config.model == preset.default_model
    
    @given(
        base_url=valid_https_url_strategy(),
        api_key=valid_api_key_strategy(),
        model=valid_model_strategy()
    )
    @settings(max_examples=100)
    def test_create_custom_config(self, base_url: str, api_key: str, model: str):
        """
        Creating custom config should use provided values.
        """
        manager = ConfigManager.__new__(ConfigManager)
        manager.PRESETS = ConfigManager.PRESETS
        
        config = manager.create_custom_config(base_url, api_key, model)
        
        assert config.provider == "custom"
        assert config.base_url == base_url
        assert config.api_key == api_key
        assert config.model == model


class TestAPIKeyMasking:
    """
    Tests for API key masking functionality.
    """
    
    @given(api_key=st.text(min_size=9, max_size=100, alphabet=st.characters(whitelist_categories=('L', 'N'))))
    @settings(max_examples=100)
    def test_api_key_is_masked(self, api_key: str):
        """
        API key should be masked when displayed.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "config.json")
            
            config = APIConfig(
                provider="openai",
                base_url="https://api.openai.com/v1",
                api_key=api_key,
                model="gpt-3.5-turbo"
            )
            
            manager = ConfigManager(config_file=filepath)
            manager.update_config(config)
            
            masked = manager.get_masked_api_key()
            
            # Masked key should not equal original
            assert masked != api_key
            # Masked key should contain asterisks
            assert "****" in masked
            # Masked key should show first 4 and last 4 characters
            assert masked.startswith(api_key[:4])
            assert masked.endswith(api_key[-4:])
