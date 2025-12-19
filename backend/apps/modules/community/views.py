# -*- coding: utf-8 -*-
"""社区功能API路由"""
from sanic import Blueprint
from sanic.response import json as sanic_json
from sanic_ext import openapi
from sanic.log import logger

from apps.utils.auth_middleware import auth_required, optional_auth
from .services import CommunityService
from .models import PromptListQuery, CommentCreate, CommentUpdate

# 创建社区功能蓝图（变量名必须与模块名相同）
community = Blueprint('community', url_prefix='/api/community')


@community.get('/prompts')
@optional_auth
@openapi.summary('获取公开提示词列表')
@openapi.parameter('page', int, 'query', description='页码', required=False)
@openapi.parameter('limit', int, 'query', description='每页数量', required=False)
@openapi.parameter('sort', str, 'query', description='排序方式: hot/latest', required=False)
@openapi.parameter('tag', str, 'query', description='标签筛选', required=False)
@openapi.parameter('keyword', str, 'query', description='关键词搜索', required=False)
async def get_public_prompts(request):
    """获取公开提示词列表（支持分页、筛选、排序）"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        sort = request.args.get('sort', 'hot')
        tag = request.args.get('tag')
        keyword = request.args.get('keyword')
        
        # 获取当前用户ID（可选）
        current_user_id = getattr(request.ctx, 'user_id', None)
        
        service = CommunityService(request.app.ctx.db)
        result = await service.get_public_prompts(
            page=page,
            limit=limit,
            sort=sort,
            tag=tag,
            keyword=keyword,
            current_user_id=current_user_id
        )
        
        return sanic_json({'code': 200, 'data': result})
    except Exception as exc:
        logger.error(f'❌ 获取公开提示词列表失败: {exc}')
        return sanic_json({'code': 500, 'message': f'查询失败: {str(exc)}'})


@community.get('/prompts/<prompt_id:int>')
@optional_auth
@openapi.summary('获取公开提示词详情')
async def get_prompt_detail(request, prompt_id):
    """获取公开提示词详情"""
    try:
        current_user_id = getattr(request.ctx, 'user_id', None)
        
        service = CommunityService(request.app.ctx.db)
        prompt = await service.get_prompt_detail(prompt_id, current_user_id)
        
        if not prompt:
            return sanic_json({'code': 404, 'message': '提示词不存在或未公开'})
        
        return sanic_json({'code': 200, 'data': prompt})
    except Exception as exc:
        logger.error(f'❌ 获取提示词详情失败: {exc}')
        return sanic_json({'code': 500, 'message': f'查询失败: {str(exc)}'})


@community.post('/prompts/<prompt_id:int>/like')
@auth_required
@openapi.summary('点赞/取消点赞提示词')
async def toggle_like(request, prompt_id):
    """点赞/取消点赞"""
    try:
        user_id = request.ctx.user_id
        
        service = CommunityService(request.app.ctx.db)
        result = await service.toggle_like(prompt_id, user_id)
        
        return sanic_json({'code': 200, 'data': result})
    except Exception as exc:
        logger.error(f'❌ 切换点赞失败: {exc}')
        return sanic_json({'code': 500, 'message': f'操作失败: {str(exc)}'})


@community.get('/prompts/<prompt_id:int>/comments')
@openapi.summary('获取评论列表')
@openapi.parameter('page', int, 'query', description='页码', required=False)
@openapi.parameter('limit', int, 'query', description='每页数量', required=False)
async def get_comments(request, prompt_id):
    """获取评论列表"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        service = CommunityService(request.app.ctx.db)
        result = await service.get_comments(prompt_id, page, limit)
        
        return sanic_json({'code': 200, 'data': result})
    except Exception as exc:
        logger.error(f'❌ 获取评论列表失败: {exc}')
        return sanic_json({'code': 500, 'message': f'查询失败: {str(exc)}'})


@community.post('/prompts/<prompt_id:int>/comments')
@auth_required
@openapi.summary('创建评论')
@openapi.body({'application/json': CommentCreate})
async def create_comment(request, prompt_id):
    """创建评论"""
    try:
        user_id = request.ctx.user_id
        data = request.json or {}
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')  # 获取parent_id
        
        if not content:
            return sanic_json({'code': 400, 'message': '评论内容不能为空'})
        
        if len(content) > 1000:
            return sanic_json({'code': 400, 'message': '评论内容不能超过1000个字符'})
        
        service = CommunityService(request.app.ctx.db)
        comment_id = await service.create_comment(prompt_id, user_id, content, parent_id)
        
        return sanic_json({'code': 200, 'data': {'id': comment_id}, 'message': '评论成功'})
    except Exception as exc:
        logger.error(f'❌ 创建评论失败: {exc}')
        return sanic_json({'code': 500, 'message': f'操作失败: {str(exc)}'})


@community.put('/comments/<comment_id:int>')
@auth_required
@openapi.summary('更新评论')
@openapi.body({'application/json': CommentUpdate})
async def update_comment(request, comment_id):
    """更新评论"""
    try:
        user_id = request.ctx.user_id
        data = request.json or {}
        content = data.get('content', '').strip()
        
        if not content:
            return sanic_json({'code': 400, 'message': '评论内容不能为空'})
        
        if len(content) > 1000:
            return sanic_json({'code': 400, 'message': '评论内容不能超过1000个字符'})
        
        service = CommunityService(request.app.ctx.db)
        await service.update_comment(comment_id, user_id, content)
        
        return sanic_json({'code': 200, 'message': '更新成功'})
    except ValueError as exc:
        return sanic_json({'code': 404, 'message': str(exc)})
    except PermissionError as exc:
        return sanic_json({'code': 403, 'message': str(exc)})
    except Exception as exc:
        logger.error(f'❌ 更新评论失败: {exc}')
        return sanic_json({'code': 500, 'message': f'操作失败: {str(exc)}'})


@community.delete('/comments/<comment_id:int>')
@auth_required
@openapi.summary('删除评论')
async def delete_comment(request, comment_id):
    """删除评论（评论作者/提示词作者/管理员可删除）"""
    try:
        user_id = request.ctx.user_id
        
        # 检查是否管理员
        user_sql = 'SELECT is_admin FROM users WHERE id = ?'
        user = await request.app.ctx.db.get(user_sql, [user_id])
        is_admin = bool(user.get('is_admin')) if user else False
        
        service = CommunityService(request.app.ctx.db)
        await service.delete_comment(comment_id, user_id, is_admin)
        
        return sanic_json({'code': 200, 'message': '删除成功'})
    except ValueError as exc:
        return sanic_json({'code': 404, 'message': str(exc)})
    except PermissionError as exc:
        return sanic_json({'code': 403, 'message': str(exc)})
    except Exception as exc:
        logger.error(f'❌ 删除评论失败: {exc}')
        return sanic_json({'code': 500, 'message': f'操作失败: {str(exc)}'})


@community.get('/prompts/<prompt_id:int>/author-prompts')
@openapi.summary('获取作者的其他公开提示词')
@openapi.parameter('limit', int, 'query', description='数量限制', required=False)
async def get_author_other_prompts(request, prompt_id):
    """获取作者的其他公开提示词"""
    try:
        limit = int(request.args.get('limit', 10))
        
        # 获取作者ID
        prompt_sql = 'SELECT user_id FROM prompts WHERE id = ?'
        prompt = await request.app.ctx.db.get(prompt_sql, [prompt_id])
        
        if not prompt:
            return sanic_json({'code': 404, 'message': '提示词不存在'})
        
        service = CommunityService(request.app.ctx.db)
        prompts = await service.get_author_other_prompts(prompt['user_id'], prompt_id, limit)
        
        return sanic_json({'code': 200, 'data': prompts})
    except Exception as exc:
        logger.error(f'❌ 获取作者其他提示词失败: {exc}')
        return sanic_json({'code': 500, 'message': f'查询失败: {str(exc)}'})


@community.get('/prompts/<prompt_id:int>/playground-shares')
@openapi.summary('获取相关操练场快照')
@openapi.parameter('limit', int, 'query', description='数量限制', required=False)
async def get_related_playground_shares(request, prompt_id):
    """获取使用该提示词的公开操练场快照"""
    try:
        limit = int(request.args.get('limit', 10))
        
        service = CommunityService(request.app.ctx.db)
        shares = await service.get_related_playground_shares(prompt_id, limit)
        
        return sanic_json({'code': 200, 'data': shares})
    except Exception as exc:
        logger.error(f'❌ 获取相关操练场快照失败: {exc}')
        return sanic_json({'code': 500, 'message': f'查询失败: {str(exc)}'})


@community.get('/prompts/<prompt_id:int>/visitors')
@openapi.summary('获取最近访问者')
@openapi.parameter('limit', int, 'query', description='限制数量', required=False)
async def get_recent_visitors(request, prompt_id):
    """获取提示词的最近访问者列表"""
    try:
        limit = int(request.args.get('limit', 10))
        
        service = CommunityService(request.app.ctx.db)
        visitors = await service.get_recent_visitors(prompt_id, limit)
        
        return sanic_json({'code': 200, 'data': visitors})
    except Exception as exc:
        logger.error(f'❌ 获取访问者列表失败: {exc}')
        return sanic_json({'code': 500, 'message': f'查询失败: {str(exc)}'})
