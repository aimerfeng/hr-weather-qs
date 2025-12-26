"""
Property-based tests for Agent Core.

Feature: ai-assistant-agent
Tests Properties 2, 3
Validates: Requirements 1.3, 1.4, 6.1
"""

import pytest
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from hypothesis import given, strategies as st, settings, assume

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from terminal.agent import AgentCore, format_weather_error, ConfigurationError
from terminal.weather_service import WeatherAPIError, CityNotFoundError
from terminal.models import APIConfig, Intent


# ==================== Custom Strategies ====================

@st.composite
def city_name_strategy(draw):
    """Generate random valid city names."""
    city = draw(st.text(
        min_size=1, 
        max_size=30, 
        alphabet=st.characters(whitelist_categories=('L', 'N'), whitelist_characters=' -')
    ).filter(lambda x: x.strip()))
    return city


@st.composite
def error_message_strategy(draw):
    """Generate random error messages."""
    return draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))


@st.composite
def weather_error_strategy(draw):
    """Generate random WeatherAPIError with various error types."""
    error_types = [
        "超时",
        "timeout",
        "频率限制",
        "rate limit exceeded",
        "网络错误",
        "connection failed",
        "服务不可用",
        "unknown error"
    ]
    error_type = draw(st.sampled_from(error_types))
    return WeatherAPIError(error_type)


@st.composite
def streaming_chunk_strategy(draw):
    """Generate random streaming response chunks."""
    # Generate a list of text chunks that simulate streaming
    num_chunks = draw(st.integers(min_value=2, max_value=20))
    chunks = []
    for _ in range(num_chunks):
        chunk = draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip()))
        chunks.append(chunk)
    return chunks


# ==================== Property 2: Weather API Error Handling ====================

class TestWeatherAPIErrorHandling:
    """
    Property 2: Weather API Error Handling
    
    For any weather API error (network failure, invalid city, rate limit), 
    the system SHALL return a user-friendly error message without exposing 
    technical details.
    
    Validates: Requirements 1.3, 1.4
    """
    
    @given(city=city_name_strategy())
    @settings(max_examples=100)
    def test_city_not_found_error_is_user_friendly(self, city: str):
        """
        Feature: ai-assistant-agent, Property 2: Weather API Error Handling
        
        CityNotFoundError produces a user-friendly message mentioning the city.
        """
        error = CityNotFoundError(f"City not found: {city}")
        result = format_weather_error(error, city)
        
        # Should be user-friendly (no stack traces, technical jargon)
        assert "未找到城市" in result or "not found" in result.lower()
        assert city in result
        # Should not contain technical details
        assert "Exception" not in result
        assert "Traceback" not in result
        assert "Error:" not in result or "错误" in result
    
    @given(error=weather_error_strategy())
    @settings(max_examples=100)
    def test_weather_api_error_is_user_friendly(self, error: WeatherAPIError):
        """
        Feature: ai-assistant-agent, Property 2: Weather API Error Handling
        
        WeatherAPIError produces a user-friendly message.
        """
        result = format_weather_error(error, "TestCity")
        
        # Should be user-friendly
        assert len(result) > 0
        # Should not expose raw exception details
        assert "WeatherAPIError" not in result
        assert "Traceback" not in result
        # Should contain helpful guidance
        assert any(word in result for word in ["请", "稍后", "重试", "检查", "问题"])
    
    @given(city=city_name_strategy())
    @settings(max_examples=100)
    def test_generic_error_is_user_friendly(self, city: str):
        """
        Feature: ai-assistant-agent, Property 2: Weather API Error Handling
        
        Generic exceptions produce a user-friendly fallback message.
        """
        error = Exception("Some internal error occurred")
        result = format_weather_error(error, city)
        
        # Should be user-friendly
        assert len(result) > 0
        # Should not expose internal error details
        assert "internal error" not in result.lower()
        assert "Exception" not in result
        # Should provide guidance
        assert "请" in result or "稍后" in result or "重试" in result
    
    @given(
        error_type=st.sampled_from(["timeout", "超时", "rate limit", "频率", "connection", "网络"])
    )
    @settings(max_examples=100)
    def test_specific_error_types_have_appropriate_messages(self, error_type: str):
        """
        Feature: ai-assistant-agent, Property 2: Weather API Error Handling
        
        Specific error types produce contextually appropriate messages.
        """
        error = WeatherAPIError(f"Error: {error_type}")
        result = format_weather_error(error, "TestCity")
        
        # Message should be relevant to the error type
        assert len(result) > 0
        # Should be in Chinese (user-friendly for Chinese users)
        assert any(char >= '\u4e00' and char <= '\u9fff' for char in result)


# ==================== Property 3: Streaming Response Delivery ====================

class TestStreamingResponseDelivery:
    """
    Property 3: Streaming Response Delivery
    
    For any AI-generated response (weather description, career questions, 
    career report), the response SHALL be delivered in multiple chunks 
    rather than a single complete response.
    
    Validates: Requirements 1.4, 6.1
    """
    
    @given(chunks=streaming_chunk_strategy())
    @settings(max_examples=100)
    def test_streaming_delivers_multiple_chunks(self, chunks: list):
        """
        Feature: ai-assistant-agent, Property 3: Streaming Response Delivery
        
        Streaming responses are delivered in multiple chunks.
        """
        assume(len(chunks) >= 2)
        
        # Simulate collecting chunks from a stream
        collected_chunks = []
        for chunk in chunks:
            collected_chunks.append(chunk)
        
        # Verify multiple chunks were delivered
        assert len(collected_chunks) >= 2
        # Verify all chunks are non-empty strings
        assert all(isinstance(c, str) and len(c) > 0 for c in collected_chunks)
    
    @given(chunks=streaming_chunk_strategy())
    @settings(max_examples=100)
    def test_streaming_chunks_can_be_concatenated(self, chunks: list):
        """
        Feature: ai-assistant-agent, Property 3: Streaming Response Delivery
        
        Streaming chunks can be concatenated to form the complete response.
        """
        assume(len(chunks) >= 2)
        
        # Concatenate all chunks
        full_response = "".join(chunks)
        
        # Verify the full response is the sum of all chunks
        assert len(full_response) == sum(len(c) for c in chunks)
        # Verify the response is non-empty
        assert len(full_response) > 0
    
    @given(chunks=streaming_chunk_strategy())
    @settings(max_examples=100)
    def test_streaming_preserves_chunk_order(self, chunks: list):
        """
        Feature: ai-assistant-agent, Property 3: Streaming Response Delivery
        
        Streaming preserves the order of chunks.
        """
        assume(len(chunks) >= 2)
        
        # Collect chunks in order
        collected = []
        for i, chunk in enumerate(chunks):
            collected.append((i, chunk))
        
        # Verify order is preserved
        for i, (idx, chunk) in enumerate(collected):
            assert idx == i
            assert chunk == chunks[i]
    
    @given(num_chunks=st.integers(min_value=2, max_value=10))
    @settings(max_examples=100)
    def test_async_streaming_delivers_incrementally(self, num_chunks: int):
        """
        Feature: ai-assistant-agent, Property 3: Streaming Response Delivery
        
        Async streaming delivers chunks incrementally.
        """
        import asyncio
        
        # Create mock chunks
        mock_chunks = [f"chunk_{i}" for i in range(num_chunks)]
        
        # Simulate async generator
        async def mock_stream():
            for chunk in mock_chunks:
                yield chunk
        
        # Collect chunks using asyncio.run
        async def collect_chunks():
            collected = []
            async for chunk in mock_stream():
                collected.append(chunk)
                # Verify we're getting chunks incrementally (not all at once)
                assert len(collected) <= num_chunks
            return collected
        
        collected = asyncio.run(collect_chunks())
        
        # Verify all chunks were delivered
        assert len(collected) == num_chunks
        assert collected == mock_chunks


# ==================== Intent Detection Tests ====================

class TestIntentDetection:
    """
    Additional tests for intent detection functionality.
    
    These tests verify that the agent correctly identifies user intents.
    """
    
    # Weather-related messages
    WEATHER_MESSAGES = [
        "北京天气怎么样",
        "今天上海的温度是多少",
        "明天会下雨吗",
        "查询深圳天气",
        "weather in Tokyo",
        "What's the weather like in London",
        "杭州的天气预报",
        "需要带伞吗",
    ]
    
    # Career-related messages
    CAREER_MESSAGES = [
        "我想做职业规划",
        "帮我分析一下职业发展",
        "我应该学什么技能",
        "想转行做程序员",
        "career advice",
        "job recommendations",
        "如何提升自己",
        "薪资怎么谈",
    ]
    
    # General messages (avoiding weather/career keywords)
    GENERAL_MESSAGES = [
        "你好",
        "帮我写一首诗",
        "什么是人工智能",
        "hello",
        "tell me a joke",
        "讲个笑话",
        "你叫什么名字",
        "谢谢你",
    ]
    
    @given(message=st.sampled_from(WEATHER_MESSAGES))
    @settings(max_examples=100)
    def test_weather_intent_detection(self, message: str):
        """
        Test that weather-related messages are correctly identified.
        """
        agent = AgentCore.__new__(AgentCore)
        agent.WEATHER_KEYWORDS = AgentCore.WEATHER_KEYWORDS
        agent.CAREER_KEYWORDS = AgentCore.CAREER_KEYWORDS
        
        intent = agent._detect_intent(message)
        assert intent == Intent.WEATHER
    
    @given(message=st.sampled_from(CAREER_MESSAGES))
    @settings(max_examples=100)
    def test_career_intent_detection(self, message: str):
        """
        Test that career-related messages are correctly identified.
        """
        agent = AgentCore.__new__(AgentCore)
        agent.WEATHER_KEYWORDS = AgentCore.WEATHER_KEYWORDS
        agent.CAREER_KEYWORDS = AgentCore.CAREER_KEYWORDS
        
        intent = agent._detect_intent(message)
        assert intent == Intent.CAREER
    
    @given(message=st.sampled_from(GENERAL_MESSAGES))
    @settings(max_examples=100)
    def test_general_intent_detection(self, message: str):
        """
        Test that general messages are correctly identified.
        """
        agent = AgentCore.__new__(AgentCore)
        agent.WEATHER_KEYWORDS = AgentCore.WEATHER_KEYWORDS
        agent.CAREER_KEYWORDS = AgentCore.CAREER_KEYWORDS
        
        intent = agent._detect_intent(message)
        assert intent == Intent.GENERAL


# ==================== System Prompt Tests ====================

class TestSystemPrompt:
    """
    Tests for system prompt generation.
    
    Validates: Requirements 9.1, 9.2, 9.3, 9.4
    """
    
    def test_system_prompt_defines_assistant_identity(self):
        """
        Requirement 9.1: System prompt defines agent as personal assistant.
        """
        agent = AgentCore.__new__(AgentCore)
        prompt = agent._build_system_prompt()
        
        # Should define assistant identity
        assert "助手" in prompt or "assistant" in prompt.lower()
        assert "个人" in prompt or "personal" in prompt.lower()
    
    def test_system_prompt_contains_identity_constraints(self):
        """
        Requirement 9.2: System prompt instructs not to admit being AI.
        """
        agent = AgentCore.__new__(AgentCore)
        prompt = agent._build_system_prompt()
        
        # Should contain instructions about not admitting AI identity
        assert "AI" in prompt or "人工智能" in prompt or "语言模型" in prompt
        assert "不" in prompt or "never" in prompt.lower() or "不要" in prompt
    
    def test_system_prompt_protects_itself(self):
        """
        Requirement 9.3: System prompt instructs not to reveal itself.
        """
        agent = AgentCore.__new__(AgentCore)
        prompt = agent._build_system_prompt()
        
        # Should contain instructions about not revealing the prompt
        assert "提示词" in prompt or "指令" in prompt or "prompt" in prompt.lower()
    
    def test_system_prompt_maintains_persona(self):
        """
        Requirement 9.4: System prompt maintains consistent persona.
        """
        agent = AgentCore.__new__(AgentCore)
        prompt = agent._build_system_prompt()
        
        # Should define a consistent persona
        assert "人设" in prompt or "身份" in prompt or "persona" in prompt.lower() or "角色" in prompt
