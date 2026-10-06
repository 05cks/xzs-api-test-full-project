# -*- coding: utf-8 -*-
"""模块3：题库管理（题目分页/查询/删除/编辑校验）"""
import pytest
import config

QN = "/api/admin/question"


@pytest.mark.question
@pytest.mark.p0
def test_question_page(admin):
    """题目分页查询返回分页结构，且含题目类型/分值等字段。"""
    r = admin.post(f"{QN}/page", {"pageIndex": 1, "pageSize": 10})
    assert r.ok
    assert "list" in r.data and "total" in r.data
    if r.data["list"]:
        item = r.data["list"][0]
        for f in ("id", "questionType", "subjectId", "score"):
            assert f in item, f"题目列表缺少字段 {f}"


@pytest.mark.question
@pytest.mark.p1
def test_question_page_filter_by_type(admin):
    """按题型过滤查询（单选=1）。"""
    r = admin.post(f"{QN}/page", {"pageIndex": 1, "pageSize": 10, "questionType": config.Q_SINGLE})
    assert r.ok
    for item in r.data["list"]:
        assert item["questionType"] == config.Q_SINGLE


@pytest.mark.question
@pytest.mark.p0
def test_question_select_exist(admin):
    """查询已存在的题目详情（取列表第一条 id）。"""
    lst = admin.post(f"{QN}/page", {"pageIndex": 1, "pageSize": 1}).data["list"]
    if not lst:
        pytest.skip("题库为空，跳过详情查询")
    r = admin.post(f"{QN}/select/{lst[0]['id']}")
    assert r.ok
    assert "title" in r.data or "id" in r.data


@pytest.mark.question
@pytest.mark.p1
def test_question_edit_blank_correct_rejected(admin):
    """单选题未填写正确答案 correct 时，应返回参数校验错误(501)。"""
    r = admin.post(f"{QN}/edit", {
        "questionType": config.Q_SINGLE,
        "subjectId": 5,
        "title": "自动化-单选题无答案",
        "analyze": "解析",
        "score": "10",
        "items": [{"prefix": "A", "content": "选项A", "score": "5", "itemUuid": "u1"},
                  {"prefix": "B", "content": "选项B", "score": "5", "itemUuid": "u2"}],
    })
    assert r.code == config.CODE_PARAM_ERROR, f"未拦截空正确答案: {r.body}"


@pytest.mark.question
@pytest.mark.p2
def test_question_select_not_exist(admin):
    """查询不存在的题目，接口不返回 500。"""
    r = admin.post(f"{QN}/select/999999")
    assert r.status_code == 200
