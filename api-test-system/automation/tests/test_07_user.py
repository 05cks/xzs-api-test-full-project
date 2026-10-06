# -*- coding: utf-8 -*-
"""模块7：用户管理（管理员用户 CRUD + 学生注册/资料/日志）"""
import time
import pytest
from api_client import ApiClient
import config

AU = "/api/admin/user"
SU = "/api/student/user"


@pytest.mark.user
@pytest.mark.p0
def test_admin_user_page(admin):
    """管理员用户分页查询，返回分页结构。"""
    r = admin.post(f"{AU}/page/list", {"pageIndex": 1, "pageSize": 10})
    assert r.ok
    assert "list" in r.data and "total" in r.data


@pytest.mark.user
@pytest.mark.p1
def test_admin_user_page_filter_role(admin):
    """按角色过滤查询用户（管理员 role=3）。"""
    r = admin.post(f"{AU}/page/list", {"pageIndex": 1, "pageSize": 10, "role": config.ROLE_ADMIN})
    assert r.ok
    for u in r.data["list"]:
        assert u["role"] == config.ROLE_ADMIN


@pytest.mark.user
@pytest.mark.p0
def test_student_register_and_cleanup(admin):
    """学生注册全流程：注册 → 登录验证 → 管理员删除。"""
    uname = f"auto_stu_{int(time.time())}"
    reg = ApiClient("register")
    r = reg.post(f"{SU}/register",
                 {"userName": uname, "password": "123456", "userLevel": 1})
    assert r.ok, f"注册失败: {r.body}"
    # 新账号可登录
    c = ApiClient("new-student")
    assert c.login(uname, "123456").code == config.CODE_SUCCESS
    # 清理：管理员按用户名检索后删除
    kvs = admin.post(f"{AU}/selectByUserName", raw_body=uname)
    if kvs.ok and kvs.data:
        uid = kvs.data[0]["value"] if isinstance(kvs.data[0], dict) else None
        if uid:
            assert admin.post(f"{AU}/delete/{uid}").ok


@pytest.mark.user
@pytest.mark.p1
def test_student_register_duplicate(admin):
    """重复用户名注册失败，返回业务错误码。"""
    c = ApiClient("dup-reg")
    r = c.post(f"{SU}/register",
               {"userName": "student", "password": "123456", "userLevel": 1})
    assert r.code != config.CODE_SUCCESS


@pytest.mark.user
@pytest.mark.p1
def test_student_register_blank_username():
    """用户名/密码为空注册失败。"""
    c = ApiClient("blank-reg")
    r = c.post(f"{SU}/register", {"userName": "", "password": "", "userLevel": 1})
    assert r.code != config.CODE_SUCCESS


@pytest.mark.user
@pytest.mark.p0
def test_student_current_profile(student):
    """学生获取当前登录用户资料。"""
    r = student.post(f"{SU}/current", {})
    assert r.ok
    assert r.data["userName"] == "student"
    assert r.data.get("password") is None, "响应泄露了密码字段"


@pytest.mark.user
@pytest.mark.p1
def test_student_event_log(student):
    """学生查询个人操作日志。"""
    r = student.post(f"{SU}/log", {})
    assert r.ok
    assert isinstance(r.data, list)


@pytest.mark.user
@pytest.mark.p1
def test_admin_change_user_status(admin, student2):
    """管理员禁用/启用用户状态切换（对 ki 用户）。"""
    # 查 ki 的 id
    page = admin.post(f"{AU}/page/list", {"pageIndex": 1, "pageSize": 50,
                                          "userName": "ki"})
    assert page.ok and page.data["list"], "未找到用户 ki"
    uid = page.data["list"][0]["id"]
    old_status = page.data["list"][0]["status"]
    r1 = admin.post(f"{AU}/changeStatus/{uid}")
    assert r1.ok
    # 还原状态，避免污染环境
    r2 = admin.post(f"{AU}/changeStatus/{uid}")
    assert r2.ok
    assert r2.data == old_status, "状态未正确还原"


@pytest.mark.user
@pytest.mark.p2
def test_admin_user_select_not_exist(admin):
    """查询不存在用户不返回 500。"""
    r = admin.post(f"{AU}/select/999999")
    assert r.status_code == 200
