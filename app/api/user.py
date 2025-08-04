from fastapi import FastAPI, Form,Request

from app.utils.helper import *
import time
from app.models.sessions import Sessions
from app.models.conn import get_db
from pydantic import BaseModel,EmailStr
import re
from app.config import get_config,save_config

class UserItem(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserAPI:
    # 用户初始化
    def init(self,item:UserItem):
        username = item.username.strip().lower()
        passwort = item.password.strip()

        # 获取环境变量里面的用户名和密码
        env_username = get_config()["user"]["USERNAME"]
        env_password = get_config()["user"]["PASSWORD"]

        # 如果其中一个不为空，则视为已经初始化过了
        if env_username or env_password:
            return show_json(400, "请勿重复初始化！")

        # 正则限制用户名只能是字母或数字组合，且长度大于3
        if not re.match(r"^[a-z0-9]{3,}$", username):
            return show_json(400, "用户名只能是字母或数字组合，且长度大于3")
        # 正则限制密码只能是字母或数字或部分特殊字符，且长度大于6
        if not re.match(r"^[a-zA-Z0-9!@#$%^&*()_+={}\[\]:;\"'<>,.?/\\-]{6,}$", passwort):
            return show_json(400, "密码只能是字母或数字或部分特殊字符，且长度大于6")
        
        # 加密后的密码
        en_password = md5(username + passwort)
        
        # 写入环境变量
        get_config()["user"]["USERNAME"] = username
        get_config()["user"]["PASSWORD"] = en_password
        get_config()["user"]["EMAIL"] = item.email
        # 保存配置文件
        save_config()
        # 返回初始化成功信息
        return show_json(200, "success", {
            "username": username,
            "email": item.email
        })

    # 用户登录
    def login(self,username: str, password: str,request: Request):
        # 获取配置文件中的用户名和密码
        env_username = get_config()["user"]["USERNAME"]
        env_password = get_config()["user"]["PASSWORD"]

        # 如果用户名不正确
        if username != env_username:
            return show_json(400, "用户名错误")
        
        # 如果密码是空的
        if not password:
            return show_json(400, "密码不能为空")
        
        # 加密密码
        md5_password = md5(username + password)

        # 判断密码是否正确
        if env_password != md5_password:
            return show_json(400, "密码错误")
        
        # 登录成功
        token = "web-" + random_string(28)
        # 获取客户端 IP 地址
        ip = get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        # 获取当前时间戳
        current_time = int(time.time())
        created_at = current_time
        updated_at = current_time
        expires_at = current_time + 3600 * 24 * 30  # 设置过期时间为30天
        is_active = 1  # 设置为1表示活跃状态
        # 写入数据库中
        db = next(get_db())
        session = Sessions(
            username=username,
            token=token,
            ip=ip,
            user_agent=user_agent,
            created_at=created_at,
            updated_at=updated_at,
            expires_at=expires_at,
            is_active=is_active
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        # 返回登录成功信息
        return show_json(200, "登录成功", {
            "token": session.token,
            "expires_at": session.expires_at,
            "username": session.username,
            "ip": session.ip,
            "user_agent": session.user_agent
        })
    
    # 用户登录状态
    def is_login(self):
        return show_json(200,"success","")


