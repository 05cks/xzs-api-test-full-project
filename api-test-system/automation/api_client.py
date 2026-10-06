# -*- coding: utf-8 -*-
"""
API 客户端封装：统一处理登录、会话 Cookie、请求发送与响应校验。

学之思接口约定：
  - 所有业务接口均为 POST，请求体 JSON；
  - 统一响应体 {"code":int, "message":str, "response":any}；
  - code==1 表示成功；
  - 鉴权基于 Spring Security 会话 JSESSIONID Cookie。
"""
import json
import logging
import time
import requests

from config import BASE_URL, TIMEOUT

logger = logging.getLogger("xzs.api")

# 单个请求的耗时记录，用于性能类断言
PERF_RECORDS = []


class ApiResponse:
    """统一响应封装。"""

    def __init__(self, status_code, body, elapsed, raw_text=""):
        self.status_code = status_code
        self.body = body if isinstance(body, dict) else {}
        self.raw_text = raw_text
        self.elapsed = elapsed

    @property
    def code(self):
        return self.body.get("code")

    @property
    def message(self):
        return self.body.get("message")

    @property
    def data(self):
        return self.body.get("response")

    @property
    def ok(self):
        return self.status_code == 200 and self.code == 1

    def __repr__(self):
        return f"<ApiResponse http={self.status_code} code={self.code} msg={self.message!r}>"


class ApiClient:
    """基于 requests.Session 的接口客户端。"""

    def __init__(self, name="anonymous", base_url=BASE_URL):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "User-Agent": "XZS-API-AutoTest/1.0",
        })
        self.user = None

    # ---------------------------------------------------------------- 基础 --
    def request(self, method, path, json_body=None, params=None,
                data=None, files=None, raw_body=None, headers=None,
                allow_redirects=False):
        url = path if path.startswith("http") else self.base_url + path
        h = dict(headers or {})
        kwargs = dict(timeout=TIMEOUT, allow_redirects=allow_redirects, headers=h)
        if json_body is not None:
            kwargs["json"] = json_body
        if raw_body is not None:
            kwargs["data"] = raw_body
        if params is not None:
            kwargs["params"] = params
        if data is not None:
            kwargs["data"] = data
        if files is not None:
            kwargs["files"] = files
            kwargs["headers"].pop("Content-Type", None)  # 交给 requests 生成边界

        start = time.time()
        try:
            resp = self.session.request(method, url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"无法连接被测服务 {url}，请确认后端已启动（{e}）") from e
        elapsed = round((time.time() - start) * 1000, 1)

        try:
            body = resp.json()
        except ValueError:
            body = {}
        api_resp = ApiResponse(resp.status_code, body, elapsed, resp.text)
        PERF_RECORDS.append({"name": self.name, "path": path,
                             "elapsed_ms": elapsed, "code": api_resp.code})
        logger.info("[%s] %s %s -> http=%s code=%s (%sms)",
                    self.name, method, path, resp.status_code, api_resp.code, elapsed)
        return api_resp

    def post(self, path, json_body=None, **kw):
        return self.request("POST", path, json_body=json_body, **kw)

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    # ---------------------------------------------------------------- 鉴权 --
    def login(self, user_name, password, remember=False):
        """登录并复用会话 Cookie。返回 ApiResponse。"""
        resp = self.post("/api/user/login",
                         {"userName": user_name, "password": password, "remember": remember})
        if resp.ok:
            self.user = user_name
        return resp

    def logout(self):
        return self.post("/api/user/logout")

    def cookie_names(self):
        return list(self.session.cookies.keys())


def new_client(name="anonymous", login_user=None):
    """便捷构造：可选自动登录。login_user 为 config 中的账号 dict。"""
    c = ApiClient(name=name)
    if login_user:
        r = c.login(login_user["userName"], login_user["password"],
                    login_user.get("remember", False))
        if not r.ok:
            raise AssertionError(f"[{name}] 登录失败: {r}")
    return c
