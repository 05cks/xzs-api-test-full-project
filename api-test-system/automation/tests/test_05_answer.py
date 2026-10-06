# -*- coding: utf-8 -*-
"""模块5：学生考试闭环（首页试卷 → 试卷详情 → 提交答卷 → 成绩查询 → 错题）"""
import pytest
import config

EP = "/api/student/exam/paper"
ANS = "/api/student/exampaper/answer"
DASH = "/api/student/dashboard"


def _first_fixed_paper(student):
    r = student.post(f"{DASH}/index", {})
    assert r.ok, f"首页加载失败: {r.body}"
    papers = r.data.get("fixedPaper") or []
    if not papers:
        pytest.skip("当前学生年级下无固定试卷")
    return papers[0]


@pytest.mark.exam
@pytest.mark.p0
def test_student_dashboard_index(student):
    """学生首页返回固定试卷/时段试卷列表结构。"""
    r = student.post(f"{DASH}/index", {})
    assert r.ok
    assert "fixedPaper" in r.data
    assert "timeLimitPaper" in r.data


@pytest.mark.exam
@pytest.mark.p0
def test_student_paper_page(student):
    """学生试卷分页查询（固定试卷）。"""
    r = student.post(f"{EP}/pageList",
                     {"pageIndex": 1, "pageSize": 10, "paperType": config.PAPER_FIXED})
    assert r.ok
    assert "list" in r.data


@pytest.mark.exam
@pytest.mark.p0
def test_student_paper_select(student):
    """学生查询试卷详情，返回题目结构。"""
    paper = _first_fixed_paper(student)
    r = student.post(f"{EP}/select/{paper['id']}")
    assert r.ok
    assert "titleItems" in r.data


@pytest.mark.exam
@pytest.mark.p0
def test_answer_submit_and_score(student):
    """【端到端核心】学生取卷 → 按标准答案作答 → 提交 → 返回成绩。"""
    paper = _first_fixed_paper(student)
    detail = student.post(f"{EP}/select/{paper['id']}")
    assert detail.ok
    title_items = detail.data.get("titleItems") or []
    questions = [q for t in title_items for q in (t.get("questionItems") or [])]
    if not questions:
        pytest.skip("试卷无题目")

    answer_items = []
    for idx, q in enumerate(questions):
        item = {"questionId": q["id"], "itemOrder": idx,
                "doRight": None, "score": None, "questionScore": None,
                "content": None, "contentArray": None}
        qtype = q.get("questionType")
        if qtype in (config.Q_SINGLE, config.Q_TF):
            item["content"] = q.get("correct")
        elif qtype == config.Q_MULTI:
            correct = q.get("correct") or ""
            item["contentArray"] = list(correct)
        answer_items.append(item)

    payload = {"id": paper["id"], "doTime": 30, "score": "", "answerItems": answer_items}
    r = student.post(f"{ANS}/answerSubmit", payload)
    # code=1 提交成功并返回成绩；code=2 表示任务试卷不可重复作答
    assert r.code in (config.CODE_SUCCESS, 2), f"提交答卷异常: {r.body}"
    if r.code == config.CODE_SUCCESS:
        assert r.data is not None, "未返回成绩"
        assert float(r.data) >= 0


@pytest.mark.exam
@pytest.mark.p1
def test_answer_page_list(student):
    """学生查询自己的答卷记录分页。"""
    r = student.post(f"{ANS}/pageList", {"pageIndex": 1, "pageSize": 10})
    assert r.ok
    assert "list" in r.data


@pytest.mark.exam
@pytest.mark.p1
def test_answer_read_detail(student):
    """学生回看答卷详情（取答卷记录第一条 id）。"""
    page = student.post(f"{ANS}/pageList", {"pageIndex": 1, "pageSize": 1})
    lst = page.data.get("list") or []
    if not lst:
        pytest.skip("无答卷记录")
    r = student.post(f"{ANS}/read/{lst[0]['id']}")
    assert r.ok
    assert "paper" in r.data and "answer" in r.data


@pytest.mark.exam
@pytest.mark.p1
def test_answer_submit_missing_required(student):
    """提交答卷缺少必填字段(id/doTime/answerItems)时返回参数校验错误。"""
    r = student.post(f"{ANS}/answerSubmit", {"id": None})
    assert r.status_code == 200
    assert r.code != config.CODE_SUCCESS


@pytest.mark.exam
@pytest.mark.p1
def test_student_wrong_question_page(student):
    """学生错题分页查询。"""
    r = student.post("/api/student/question/answer/page", {"pageIndex": 1, "pageSize": 10})
    assert r.ok
    assert "list" in r.data
