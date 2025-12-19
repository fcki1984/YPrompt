# -*- coding: utf-8 -*-
"""社区功能数据模型"""
from sanic_ext import openapi
from typing import Optional, List


@openapi.component
class PromptListQuery:
    """公开提示词查询参数"""
    page: int = openapi.Integer(description="页码", default=1)
    limit: int = openapi.Integer(description="每页数量", default=20)
    sort: str = openapi.String(description="排序方式: hot(热门)/latest(最新)", default="hot")
    tag: Optional[str] = openapi.String(description="标签筛选")
    keyword: Optional[str] = openapi.String(description="关键词搜索")


@openapi.component
class PromptDetailResponse:
    """提示词详情响应"""
    id: int
    title: str
    description: Optional[str]
    final_prompt: str
    prompt_type: str
    language: str
    format: str
    tags: Optional[str]
    
    # 作者信息
    user_id: int
    author_name: str
    author_avatar: Optional[str]
    
    # 统计信息
    view_count: int
    use_count: int
    like_count: int
    comment_count: int
    hot_score: float
    
    # 当前用户状态
    is_liked: bool
    
    create_time: str
    update_time: str


@openapi.component
class CommentCreate:
    """创建评论"""
    content: str = openapi.String(description="评论内容", required=True, min_length=1, max_length=1000)


@openapi.component
class CommentUpdate:
    """更新评论"""
    content: str = openapi.String(description="评论内容", required=True, min_length=1, max_length=1000)


@openapi.component  
class CommentResponse:
    """评论响应"""
    id: int
    prompt_id: int
    user_id: int
    content: str
    is_edited: bool
    
    # 用户信息
    user_name: str
    user_avatar: Optional[str]
    
    create_time: str
    update_time: str
