"""
Web API - 聊天端点

实现 SSE (Server-Sent Events) 流式输出的聊天 API。
支持对话历史管理和职业规划状态跟踪。

Requirements: 6.1, 6.2, 6.3
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio

from web.lib.agent import AgentCore, ConfigurationError, APIError
from web.lib.models import APIConfig, SSEMessage

router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-3.5-turbo"
    provider: str = "openai"
    conversation_history: List[Dict[str, str]] = []
    career_state: Optional[Dict[str, Any]] = None


async def generate_sse_stream(request: ChatRequest):
    """
    生成 SSE 流
    
    Requirements 6.1: 流式输出，逐块显示内容
    Requirements 6.2: SSE 格式输出
    Requirements 6.3: 错误处理
    
    Args:
        request: 聊天请求
        
    Yields:
        str: SSE 格式的消息
    """
    try:
        # 创建配置
        config = APIConfig(
            provider=request.provider,
            base_url=request.base_url,
            api_key=request.api_key,
            model=request.model
        )
        
        # 创建代理
        agent = AgentCore(config)
        await agent.initialize()
        
        # 处理消息并流式输出
        async for sse_message in agent.process_message(
            user_message=request.message,
            conversation_history=request.conversation_history,
            career_state=request.career_state
        ):
            # 转换为 SSE 格式
            sse_data = f"data: {sse_message.to_json()}\n\n"
            yield sse_data
            
            # 短暂延迟，确保客户端能接收到消息
            await asyncio.sleep(0.01)
        
    except ConfigurationError as e:
        # 配置错误
        error_msg = SSEMessage.error_message(f"配置错误: {str(e)}")
        yield f"data: {error_msg.to_json()}\n\n"
        
        done_msg = SSEMessage.done_message()
        yield f"data: {done_msg.to_json()}\n\n"
        
    except APIError as e:
        # API 调用错误
        error_msg = SSEMessage.error_message(f"API 错误: {str(e)}")
        yield f"data: {error_msg.to_json()}\n\n"
        
        done_msg = SSEMessage.done_message()
        yield f"data: {done_msg.to_json()}\n\n"
        
    except Exception as e:
        # 其他错误
        error_msg = SSEMessage.error_message(f"处理消息时出错: {str(e)}")
        yield f"data: {error_msg.to_json()}\n\n"
        
        done_msg = SSEMessage.done_message()
        yield f"data: {done_msg.to_json()}\n\n"


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    聊天 API 端点
    
    接收用户消息，返回 SSE 流式响应。
    
    Requirements:
    - 6.1: 流式输出
    - 6.2: SSE 格式
    - 6.3: 错误处理
    
    Args:
        request: 聊天请求
        
    Returns:
        StreamingResponse: SSE 流式响应
    """
    return StreamingResponse(
        generate_sse_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
        }
    )


@router.get("/health")
async def health_check():
    """
    健康检查端点
    
    Returns:
        dict: 健康状态
    """
    return {
        "status": "healthy",
        "service": "chat-api",
        "version": "1.0.0"
    }
