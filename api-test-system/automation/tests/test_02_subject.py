# -*- coding: utf-8 -*-
"""模块2：学科管理（管理员 CRUD + 学生查询）"""
import time
import pytest
import config

PN = "/api/student/education"
AN = "/api/admin/education"


@pytest.mark.subject
@pytest.mark.p0
def test_admin_subject_list(admin):
    """管理员获取全部学科列表，返回数组。"""
    r = admin.post(f"{AN}/subject/list", {})
    assert r.ok
    assert isinstance(r.data, list)
    assert len(r.data) >= 1
    assert "name" in r.data[0]


@pytest.mark.subject
@pytest.mark.p0
def test_admin_subject_page(admin):
    """学科分页查询返回分页结构（total/list/pageNum）。"""
    r = admin.post(f"{AN}/subject/page", {"pageIndex": 1, "pageSize": 5})
    assert r.ok
    assert "list" in r.data and "total" in r.data


@pytest.mark.subject
@pytest.mark.p0
def test_subject_crud_lifecycle(admin):
    """学科全生命周期：新增 → 查询 → 修改 → 删除。"""
    name = f"自动化测试科目_{int(time.time())}"
    # 新增
    r = admin.post(f"{AN}/subject/edit",
                   {"name": name, "level": 900, "levelName": "自动化年级"})
    assert r.ok, f"新增学科失败: {r.body}"
    # 查询列表定位
    lst = admin.post(f"{AN}/subject/list", {}).data
    target = [s for s in lst if s["name"] == name]
    assert target, "新增的学科未出现在列表中"
    sid = target[0]["id"]
    # 修改
    r = admin.post(f"{AN}/subject/edit",
                   {"id": sid, "name": name + "_改", "level": 901, "levelName": "自动化年级2"})
    assert r.ok, f"修改学科失败: {r.body}"
    sel = admin.post(f"{AN}/subject/select/{sid}")
    assert sel.ok and sel.data["name"] == name + "_改"
    # 删除（逻辑删除）
    r = admin.post(f"{AN}/subject/delete/{sid}")
    assert r.ok
    lst2 = admin.post(f"{AN}/subject/list", {}).data
    assert not [s for s in lst2 if s["id"] == sid and s["name"] == name + "_改"], \
        "删除后学科仍出现在列表中"


@pytest.mark.subject
@pytest.mark.p1
def test_subject_edit_missing_required(admin):
    """新增学科缺少必填字段 name 时，应返回参数校验错误而非 500。"""
    r = admin.post(f"{AN}/subject/edit", {"level": 1, "levelName": "x"})
    assert r.status_code == 200
    assert r.code != config.CODE_SUCCESS


@pytest.mark.subject
@pytest.mark.p1
def test_subject_select_not_exist(admin):
    """查询不存在的学科，不抛 500。"""
    r = admin.post(f"{AN}/subject/select/999999")
    assert r.status_code == 200


@pytest.mark.subject
@pytest.mark.p1
def test_student_subject_list(student):
    """学生获取本年级可见学科列表。"""
    r = student.post(f"{PN}/subject/list", {})
    assert r.ok
    assert isinstance(r.data, list)
