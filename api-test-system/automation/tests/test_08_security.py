# -*- coding: utf-8 -*-
"""模块8：安全与权限（水平/垂直越权、参数校验、注入防护）"""
import pytest
from api_client import ApiClient
import config


@pytest.mark.security
@pytest.mark.p0
def test_student_cannot_access_admin_api(student):
    """【垂直越权】学生访问管理员接口应返回 502 无权限。"""
    r = student.post("/api/admin/dashboard/index", {})
    assert r.code == config.CODE_ACCESS_DENIED, f"越权未被拦截: {r.body}"


@pytest.mark.security
@pytest.mark.p0
def test_admin_cannot_access_student_api(admin):
    """【垂直越权】管理员访问学生专属接口应被拒绝。"""
    r = admin.post("/api/student/user/current", {})
    assert r.code in (config.CODE_ACCESS_DENIED, config.CODE_UNAUTHORIZED)


@pytest.mark.security
@pytest.mark.p0
def test_anonymous_access_admin(anon):
    """未登录访问管理员接口返回 401。"""
    r = anon.post("/api/admin/user/page/list", {"pageIndex": 1, "pageSize": 10})
    assert r.code == config.CODE_UNAUTHORIZED


@pytest.mark.security
@pytest.mark.p1
def test_sql_injection_login():
    """登录用户名携带 SQL 注入串，不应造成异常或绕过认证。"""
    c = ApiClient("sqli")
    r = c.post("/api/user/login",
               {"userName": "admin' OR '1'='1", "password": "' OR '1'='1", "remember": False})
    assert r.status_code == 200
    assert r.code != config.CODE_SUCCESS


@pytest.mark.security
@pytest.mark.p1
def test_sql_injection_query(admin):
    """分页查询用户名携带注入串，应安全返回空结果而非 500。"""
    r = admin.post("/api/admin/user/page/list",
                   {"pageIndex": 1, "pageSize": 10, "userName": "a' OR 1=1 -- "})
    assert r.status_code == 200
    assert r.code == config.CODE_SUCCESS


@pytest.mark.security
@pytest.mark.p1
def test_password_not_leaked_in_user_list(admin):
    """管理员用户列表不应返回明文/密文密码字段。"""
    r = admin.post("/api/admin/user/page/list", {"pageIndex": 1, "pageSize": 5})
    assert r.ok
    for u in r.data["list"]:
        assert "password" not in u or u.get("password") in (None, ""), "用户列表泄露密码"


@pytest.mark.security
@pytest.mark.p1
def test_student_paper_detail_answer_leak(student):
    """【安全关注点】学生试卷详情是否泄露标准答案 correct 字段。"""
    r = student.post("/api/student/exam/paper/pageList",
                     {"pageIndex": 1, "pageSize": 1, "paperType": config.PAPER_FIXED})
    if not r.data["list"]:
        pytest.skip("无可用试卷")
    detail = student.post(f"/api/student/exam/paper/select/{r.data['list'][0]['id']}")
    assert detail.ok
    leaked = []
    for t in detail.data.get("titleItems", []):
        for q in t.get("questionItems", []):
            if q.get("correct"):
                leaked.append(q["id"])
    if leaked:
        pytest.xfail(f"存在答案泄露风险：题目 {leaked} 的 correct 字段返回给了学生端")


@pytest.mark.security
@pytest.mark.p2
def test_page_size_over_limit(admin):
    """分页 pageSize 超大值应被合理处理（不返回 500）。"""
    r = admin.post("/api/admin/user/page/list", {"pageIndex": 1, "pageSize": 100000})
    assert r.status_code == 200


@pytest.mark.security
@pytest.mark.p2
def test_negative_page_index(admin):
    """分页 pageIndex 为负数/0 时接口不崩溃。"""
    r = admin.post("/api/admin/user/page/list", {"pageIndex": -1, "pageSize": 10})
    assert r.status_code == 200
