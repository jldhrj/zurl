from app.api.sys import *
from app.config import templates
from app.middleware.deny import deny_uas

class IndexAPI:
    async def index(self, request: Request):
        # 调用deny_uas中间件检查User-Agent
        if await deny_uas(request):
            return templates.TemplateResponse("error_pages/deny.html", {"request": request})
        
        # 获取版本号和版本日期
        versionInfo = {
            "version": VERSION,
            "version_date": VERSION_DATE
        }
        
        # 渲染index.html模板
        return templates.TemplateResponse("index.html", {"request": request, "versionInfo": versionInfo})
