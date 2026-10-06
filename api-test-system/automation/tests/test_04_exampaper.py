# -*- coding: utf-8 -*-
"""模块4：试卷与任务管理（管理员试卷分页/详情/删除、任务分页）"""
import pytest
import config

EP = "/api/admin/exam/paper"
TK = "/api/admin/task"


@pytest.mark.paper
@pytest.mark.p0
def test_exam_paper_page(admin):
    """试卷分页查询返回分页结构。"""
    r = admin.post(f"{EP}/page", {"pageIndex": 1, "pageSize": 10})
    assert r.ok
    assert "list" in r.data and "total" in r.data
    if r.data["list"]:
        item = r.data["list"][0]
        for f in ("id", "name", "paperType", "subjectId"):
            assert f in item, f"试卷列表缺少字段 {f}"


@pytest.mark.paper
@pytest.mark.p1
def test_exam_paper_page_filter_type(admin):
    """按试卷类型过滤（固定试卷=1）。"""
    r = admin.post(f"{EP}/page", {"pageIndex": 1, "pageSize": 10, "paperType": config.PAPER_FIXED})
    assert r.ok
    for item in r.data["list"]:
        assert item["paperType"] == config.PAPER_FIXED


@pytest.mark.paper
@pytest.mark.p0
def test_exam_paper_select(admin):
    """查询固定试卷详情，返回含 titleItems 的结构。"""
    lst = admin.post(f"{EP}/page",
                     {"pageIndex": 1, "pageSize": 1, "paperType": config.PAPER_FIXED}).data["list"]
    if not lst:
        pytest.skip("无固定试卷")
    r = admin.post(f"{EP}/select/{lst[0]['id']}")
    assert r.ok
    assert "titleItems" in r.data


@pytest.mark.paper
@pytest.mark.p1
def test_exam_paper_task_page(admin):
    """任务试卷分页查询。"""
    r = admin.post(f"{EP}/taskExamPage", {"pageIndex": 1, "pageSize": 10})
    assert r.ok
    assert "list" in r.data


@pytest.mark.paper
@pytest.mark.p1
def test_task_page(admin):
    """任务分页查询返回分页结构。"""
    r = admin.post(f"{TK}/page", {"pageIndex": 1, "pageSize": 10})
    assert r.ok
    assert "list" in r.data and "total" in r.data


@pytest.mark.paper
@pytest.mark.p2
def test_exam_paper_select_not_exist(admin):
    """查询不存在试卷不返回 500。"""
    r = admin.post(f"{EP}/select/999999")
    assert r.status_code == 200


@pytest.mark.paper
@pytest.mark.p1
def test_exam_paper_edit_blank_name(admin):
    """新增试卷缺少名称/标题项时返回参数校验错误。"""
    r = admin.post(f"{EP}/edit", {
        "level": 1, "subjectId": 1, "paperType": config.PAPER_FIXED,
        "name": "", "suggestTime": 10, "score": "0", "titleItems": []
    })
    assert r.status_code == 200
    assert r.code != config.CODE_SUCCESS
