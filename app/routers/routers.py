from fastapi import APIRouter,Form, Request, Depends, UploadFile, File
from app.api.index import IndexAPI
from app.api.sys import SysAPI
from app.api.user import UserAPI, UserItem
from app.api.url import *
from app.middleware.auth import get_current_session
from app.models.sessions import Sessions
from app.middleware.click import update_click_counts
from app.middleware.deny import deny_uas
from app.config import templates

# 创建 APIRouter 实例
router = APIRouter()

indexAPI = IndexAPI()
userAPI = UserAPI()
urlAPI = UrlAPI()
sysAPI = SysAPI()

# 首页
@router.get("/")
async def index(request: Request):
    return await indexAPI.index(request=request)

# 短链接跳转
@router.get("/{short_url}")
async def redirect_to_long_url(
    short_url: str, 
    request: Request = None
):
    # print(f"收到短链接请求: {short_url}")  # 添加这行调试
    return await urlAPI.redirect(short_url=short_url, request=request)

# 登录接口
@router.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...), request: Request = None):
    return userAPI.login(username=username, password=password, request=request)

# 短链接接口
@router.post("/api/shorten_url")
async def shorten_url(item: UrlItem, request: Request,session = Depends(get_current_session)):
    return await urlAPI.shorten_url(item=item, request=request)

# 导入接口
@router.post("/api/import")
async def import_urls(file: UploadFile = File(...), session = Depends(get_current_session)):
    return await urlAPI.import_data(file=file)

# 获取链接列表
@router.get("/api/urls")
async def get_urls(request: Request, session = Depends(get_current_session),page: int = 1, limit: int = 10):
    return urlAPI.get_list(page=page, limit=limit)

# 清空所有链接
@router.post("/api/urls/clear")
async def clear_urls(session = Depends(get_current_session)):
    return urlAPI.clear_all()

# 删除单个链接
@router.post("/api/delete/url")
async def delete_url(short_url: str = Form(...), session = Depends(get_current_session)):
    return urlAPI.delete_by_short_url(short_url=short_url)

# 获取链接的标题和描述
@router.post("/api/get_url_metadata")
async def get_url_metadata(url: str = Form(...), session = Depends(get_current_session)):
    return await urlAPI.get_url_metadata(url=url)

# 获取单个链接信息
@router.post("/api/get_url_info")
async def get_url_info(short_url: str = Form(...), session = Depends(get_current_session)):
    return await urlAPI.get_by_shorten_url(short_url=short_url)

# 更新链接信息
@router.post("/api/update_url/{id}")
async def update_url(id: int, item: UrlItem, session = Depends(get_current_session)):
    return urlAPI.update_url(id=id, item=item)

# 搜索链接
@router.post("/api/search")
async def search_urls(item: UrlSearchItem, session = Depends(get_current_session)):
    return urlAPI.search_urls(item=item)

# 获取用户登录状态
@router.get("/api/user/is_login")
async def is_login(session = Depends(get_current_session)):
    return userAPI.is_login()

# 用户初始化
@router.post("/api/user/init")
async def init_user(item: UserItem):
    return userAPI.init(item=item)

# 获取app信息
@router.get("/api/get/appinfo")
async def get_app_info(session = Depends(get_current_session)):
    return sysAPI.app_info()

# 获取站点状态等信息
@router.get("/api/get/siteinfo")
async def get_siteinfo():
    return await sysAPI.siteInfo()