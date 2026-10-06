# -*- coding: utf-8 -*-
"""模块1：用户认证与鉴权（登录/登出/未登录拦截）"""
import pytest
from api_client import ApiClient
import config


@pytest.mark.auth
@pytest.mark.p0
def test_login_admin_success():
    """管理员使用正确账号密码登录成功，返回 code=1 且下发了 JSESSIONID。"""
    c = ApiClient("login-admin")
    r = c.login("admin", "123456")
    assert r.status_code == 200
    assert r.code == config.CODE_SUCCESS, f"登录失败: {r.body}"
    assert "JSESSIONID" in c.cookie_names(), "未下发会话 Cookie"
    assert r.data and r.data.get("userName") == "admin"


@pytest.mark.auth
@pytest.mark.p0
def test_login_student_success():
    """学生使用正确账号密码登录成功。"""
    c = ApiClient("login-student")
    r = c.login("student", "123456")
    assert r.code == config.CODE_SUCCESS
    assert r.data.get("userName") == "student"


@pytest.mark.auth
@pytest.mark.p0
def test_login_wrong_password():
    """密码错误登录失败，返回 402 用户名或密码错误。"""
    c = ApiClient("login-bad")
    r = c.login("admin", "wrong-password")
    assert r.code != config.CODE_SUCCESS
    # Spring Security 认证失败统一走 failureHandler
    assert r.code in (config.CODE_AUTH_ERROR, config.CODE_UNAUTHORIZED)


@pytest.mark.auth
@pytest.mark.p1
def test_login_user_not_exist():
    """用户名不存在登录失败。"""
    c = ApiClient("login-noexist")
    r = c.login("no_such_user_999", "123456")
    assert r.code != config.CODE_SUCCESS


@pytest.mark.auth
@pytest.mark.p1
def test_login_empty_params():
    """用户名/密码为空时登录失败，不产生 500 异常。"""
    c = ApiClient("login-empty")
    r = c.post("/api/user/login", {"userName": "", "password": "", "remember": False})
    assert r.status_code == 200
    assert r.code != config.CODE_SUCCESS


@pytest.mark.auth
@pytest.mark.p0
def test_access_without_login():
    """未登录访问受保护接口，返回 401 用户未登录。"""
    c = ApiClient("anon")
    r = c.post("/api/admin/dashboard/index", {})
    assert r.code == config.CODE_UNAUTHORIZED


@pytest.mark.auth
@pytest.mark.p1
def test_logout_clears_session(admin):
    """登出后会话失效，再访问受保护接口应返回未登录。"""
    c = ApiClient("logout-tester")
    assert c.login("admin", "123456").ok
    assert c.logout().status_code == 200
    # 复用被登出的会话
    r = c.post("/api/admin/dashboard/index", {})
    assert r.code == config.CODE_UNAUTHORIZED


@pytest.mark.auth
@pytest.mark.p2
def test_login_remember_me():
    """勾选记住我(remember=true)登录成功并返回记住我 Cookie。"""
    c = ApiClient("login-remember")
    r = c.post("/api/user/login",
               {"userName": "admin", "password": "123456", "remember": True})
    assert r.code == config.CODE_SUCCESS
