"""操练场分享 API"""
import json
import datetime

from sanic import Blueprint
from sanic.response import json as sanic_json
from sanic_ext import openapi
from sanic.log import logger

from apps.utils.auth_middleware import auth_required, optional_auth
from apps.utils.password_utils import PasswordUtil
from .models import (
    CreateShareRequest,
    ShareDetailResponse,
    ShareListResponse
)
from .services import PlaygroundShareService

playground_shares = Blueprint('playground_shares', url_prefix='/api/playground/shares')


@playground_shares.post('/')
@auth_required
@openapi.summary('创建操练场分享')
@openapi.body({"application/json": CreateShareRequest})
async def create_share(request):
    try:
        user_id = request.ctx.user_id
        service = PlaygroundShareService(request.app.ctx.db)
        payload = request.json or {}
        result = await service.create_share(user_id, payload)
        return sanic_json({'code': 200, 'data': result})
    except ValueError as exc:
        return sanic_json({'code': 400, 'message': str(exc)})
    except Exception as exc:
        logger.error(f'❌ 创建操练场分享失败: {exc}')
        return sanic_json({'code': 500, 'message': '创建分享失败'})


@playground_shares.get('/')
@auth_required
@openapi.summary('获取我的分享列表')
@openapi.response(200, {"application/json": ShareListResponse})
async def list_shares(request):
    try:
        user_id = request.ctx.user_id
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        if page < 1:
            page = 1
        if limit < 1 or limit > 50:
            limit = 10
        service = PlaygroundShareService(request.app.ctx.db)
        data = await service.list_shares(user_id, page, limit)
        return sanic_json({'code': 200, 'data': data})
    except Exception as exc:
        logger.error(f'❌ 获取分享列表失败: {exc}')
        return sanic_json({'code': 500, 'message': '获取分享列表失败'})


@playground_shares.get('/<share_code:str>')
@optional_auth
@openapi.summary('获取分享详情')
@openapi.response(200, {"application/json": ShareDetailResponse})
async def get_share(request, share_code):
    try:
        service = PlaygroundShareService(request.app.ctx.db)
        share = await service.get_share_for_viewer(share_code)
        if not share or not share.get('is_active'):
            return sanic_json({'code': 404, 'message': '分享不存在或已失效'})

        if not share.get('is_permanent') and share.get('expires_at'):
            try:
                expires = datetime.datetime.strptime(share['expires_at'], '%Y-%m-%d %H:%M:%S')
                if expires <= datetime.datetime.now():
                    return sanic_json({'code': 410, 'message': '分享链接已过期'})
            except ValueError:
                logger.warning('无法解析分享过期时间: %s', share.get('expires_at'))

        viewer_id = getattr(request.ctx, 'user_id', None)
        access_mode = share.get('access_mode') or 'public'
        if access_mode == 'auth_only' and not viewer_id:
            return sanic_json({'code': 401, 'message': '该分享需要登录后访问'})

        password_hash = share.get('password_hash')
        if password_hash:
            provided = request.headers.get('X-Share-Password') or request.args.get('password')
            if not provided:
                return sanic_json({'code': 403, 'message': '该分享已设置访问密码', 'need_password': True})
            if not PasswordUtil.verify_password(provided, password_hash):
                return sanic_json({'code': 403, 'message': '访问密码不正确', 'need_password': True})

        provider = json.loads(share.get('provider_snapshot') or '{}')
        messages = json.loads(share.get('messages_json') or '[]')
        artifact = None
        if share.get('artifact_type'):
            artifact = {
                'type': share.get('artifact_type'),
                'content': share.get('artifact_content')
            }

        await service.record_view(share['id'])

        response = {
            'share_code': share.get('share_code'),
            'title': share.get('title'),
            'system_prompt': share.get('system_prompt'),
            'provider': provider,
            'artifact': artifact,
            'messages': messages,
            'owner': {
                'id': share.get('owner_id'),
                'name': share.get('owner_name'),
                'avatar': share.get('owner_avatar')
            },
            'created_at': share.get('create_time'),
            'view_count': (share.get('view_count') or 0) + 1,
            'access_mode': access_mode,
            'is_permanent': bool(share.get('is_permanent')),
            'expires_at': share.get('expires_at'),
            'has_password': bool(password_hash),
            'can_edit': bool(viewer_id and viewer_id == share.get('user_id'))
        }
        return sanic_json({'code': 200, 'data': response})
    except Exception as exc:
        logger.error(f'❌ 获取操练场分享失败: {exc}')
        return sanic_json({'code': 500, 'message': '获取分享失败'})


@playground_shares.delete('/<share_code:str>')
@auth_required
@openapi.summary('删除分享链接')
async def delete_share(request, share_code):
    try:
        user_id = request.ctx.user_id
        service = PlaygroundShareService(request.app.ctx.db)
        await service.delete_share(user_id, share_code)
        return sanic_json({'code': 200, 'message': '已删除'})
    except Exception as exc:
        logger.error(f'❌ 删除操练场分享失败: {exc}')
        return sanic_json({'code': 500, 'message': '删除失败'})


@playground_shares.patch('/<share_code:str>')
@auth_required
@openapi.summary('更新分享设置')
async def update_share(request, share_code):
    try:
        user_id = request.ctx.user_id
        service = PlaygroundShareService(request.app.ctx.db)
        payload = request.json or {}
        await service.update_share(user_id, share_code, payload)
        return sanic_json({'code': 200, 'message': '更新成功'})
    except ValueError as exc:
        return sanic_json({'code': 400, 'message': str(exc)})
    except Exception as exc:
        logger.error(f'❌ 更新操练场分享失败: {exc}')
        return sanic_json({'code': 500, 'message': '更新失败'})
