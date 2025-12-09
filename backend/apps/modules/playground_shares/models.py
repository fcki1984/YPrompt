"""OpenAPI 模型定义"""
from sanic_ext import openapi


@openapi.component
class ShareProviderModel:
    id: str = openapi.String(description="提供商ID")
    name: str = openapi.String(description="提供商名称")
    modelId: str = openapi.String(description="模型ID")
    modelName: str = openapi.String(description="模型名称")
    streamMode: bool = openapi.Boolean(description="是否启用流式模式", default=True)


@openapi.component
class ShareArtifactModel:
    type: str = openapi.String(description="Artifact 类型")
    content: str = openapi.String(description="Artifact 内容")


@openapi.component
class ShareMessageModel:
    id: str = openapi.String(description="消息ID")
    role: str = openapi.String(description="角色 user/model")
    text: str = openapi.String(description="内容")
    displayText: str = openapi.String(description="渲染内容")
    timestamp: int = openapi.Integer(description="时间戳")


@openapi.component
class CreateShareRequest:
    title: str = openapi.String(description="分享标题")
    systemPrompt: str = openapi.String(description="系统提示词")
    provider: ShareProviderModel = openapi.Object(ShareProviderModel)
    artifact: ShareArtifactModel = openapi.Object(ShareArtifactModel)
    messages: list = openapi.Array(ShareMessageModel, description="消息列表")
    is_permanent: bool = openapi.Boolean(description="是否永久有效", default=False)
    expires_at: str = openapi.String(description="自定义到期时间", example="2024-12-31T23:59:59")
    access_mode: str = openapi.String(description="访问模式 public/auth_only", default='public')
    password: str = openapi.String(description="访问密码", required=False)


@openapi.component
class ShareListItem:
    share_code: str = openapi.String(description="分享编码")
    title: str = openapi.String(description="标题")
    access_mode: str = openapi.String(description="访问模式")
    is_permanent: bool = openapi.Boolean(description="是否永久")
    expires_at: str = openapi.String(description="过期时间")
    view_count: int = openapi.Integer(description="访问次数")
    has_password: bool = openapi.Boolean(description="是否设置密码")
    is_active: bool = openapi.Boolean(description="是否有效")
    create_time: str = openapi.String(description="创建时间")


@openapi.component
class ShareListResponse:
    total: int = openapi.Integer(description="总数")
    page: int = openapi.Integer(description="页码")
    limit: int = openapi.Integer(description="每页大小")
    items: list = openapi.Array(ShareListItem, description="分享列表")


@openapi.component
class ShareDetailResponse:
    share_code: str = openapi.String(description="分享编码")
    title: str = openapi.String(description="标题")
    system_prompt: str = openapi.String(description="系统提示词")
    provider: ShareProviderModel = openapi.Object(ShareProviderModel)
    artifact: ShareArtifactModel = openapi.Object(ShareArtifactModel)
    messages: list = openapi.Array(ShareMessageModel)
    owner: dict = openapi.Object(description="分享者信息")
    created_at: str = openapi.String(description="创建时间")
    view_count: int = openapi.Integer(description="访问次数")
    access_mode: str = openapi.String(description="访问模式")
    is_permanent: bool = openapi.Boolean(description="是否永久")
    expires_at: str = openapi.String(description="到期时间")
    has_password: bool = openapi.Boolean(description="是否设置密码")
