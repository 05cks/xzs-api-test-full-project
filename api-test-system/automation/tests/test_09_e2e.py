# -*- coding: utf-8 -*-
"""模块9：端到端全链路（组卷 → 发卷 → 作答 → 判分 → 管理端复核）"""
import time
import pytest
import config

AN_EDU = "/api/admin/education"
AN_Q = "/api/admin/question"
AN_PAPER = "/api/admin/exam/paper"
S_PAPER = "/api/student/exam/paper"
S_ANS = "/api/student/exampaper/answer"


@pytest.mark.e2e
@pytest.mark.p0
def test_full_exam_lifecycle(admin, student):
    """
    完整业务闭环：
      1) 管理员新建学科
      2) 在该学科下新建单选题目（正确答案 A）
      3) 用该题目组卷（固定试卷，年级=1 便于学生 student 可见）
      4) 学生拉到试卷并提交正确答案
      5) 学生提交后得分应为满分
      6) 管理端可查询到该答卷记录
    自动清理：删除试卷、题目、学科。
    """
    ts = int(time.time())

    # 1) 新建学科
    sub_name = f"E2E学科_{ts}"
    r = admin.post(f"{AN_EDU}/subject/edit",
                   {"name": sub_name, "level": 1, "levelName": "一年级"})
    assert r.ok, f"建学科失败: {r.body}"
    subjects = admin.post(f"{AN_EDU}/subject/list", {}).data
    sid = next(s["id"] for s in subjects if s["name"] == sub_name)

    # 2) 新建单选题目，正确答案=A
    r = admin.post(f"{AN_Q}/edit", {
        "questionType": config.Q_SINGLE,
        "subjectId": sid,
        "title": f"E2E题目_{ts}",
        "analyze": "自动化解析",
        "score": "10",
        "correct": "A",
        "items": [
            {"prefix": "A", "content": "正确选项", "score": "5", "itemUuid": f"{ts}-a"},
            {"prefix": "B", "content": "错误选项", "score": "5", "itemUuid": f"{ts}-b"},
        ],
        "difficult": 1, "gradeLevel": 1,
    })
    assert r.ok, f"建题目失败: {r.body}"
    qlist = admin.post(f"{AN_Q}/page",
                       {"pageIndex": 1, "pageSize": 50, "subjectId": sid}).data["list"]
    qid = next(q["id"] for q in qlist if q["shortTitle"] and f"E2E题目_{ts}" in q["shortTitle"])

    # 3) 组卷
    paper_name = f"E2E试卷_{ts}"
    r = admin.post(f"{AN_PAPER}/edit", {
        "level": 1, "subjectId": sid, "paperType": config.PAPER_FIXED,
        "name": paper_name, "suggestTime": 30, "score": "10",
        "titleItems": [{
            "name": "一、单选题",
            "questionItems": [{
                "id": qid, "questionType": config.Q_SINGLE, "subjectId": sid,
                "title": f"E2E题目_{ts}", "analyze": "自动化解析", "score": "10",
                "correct": "A", "difficult": 1, "itemOrder": 0,
                "items": [
                    {"prefix": "A", "content": "正确选项", "score": "5", "itemUuid": f"{ts}-a"},
                    {"prefix": "B", "content": "错误选项", "score": "5", "itemUuid": f"{ts}-b"},
                ],
            }],
        }],
    })
    assert r.ok, f"组卷失败: {r.body}"
    paper_id = r.data["id"]

    # 4) 学生拉卷并提交正确答案
    detail = student.post(f"{S_PAPER}/select/{paper_id}")
    assert detail.ok
    questions = [q for t in detail.data.get("titleItems", [])
                 for q in t.get("questionItems", [])]
    assert questions, "试卷无题目"
    answer_items = [{"questionId": q["id"], "itemOrder": i,
                     "doRight": None, "score": None, "questionScore": None,
                     "content": q.get("correct") or "A", "contentArray": None}
                    for i, q in enumerate(questions)]
    r = student.post(f"{S_ANS}/answerSubmit",
                     {"id": paper_id, "doTime": 20, "score": "", "answerItems": answer_items})
    assert r.code == config.CODE_SUCCESS, f"提交答卷失败: {r.body}"

    # 5) 校验得分
    score = float(r.data)
    assert score == 10, f"标准答案得分应为10，实际 {score}"

    # 6) 管理端可查询到该答卷
    ans = admin.post("/api/admin/examPaperAnswer/page",
                     {"pageIndex": 1, "pageSize": 20, "subjectId": sid})
    assert ans.ok
    assert any(a.get("paperName") == paper_name for a in ans.data["list"]), \
        "管理端未查询到该答卷"

    # 清理
    assert admin.post(f"{AN_PAPER}/delete/{paper_id}").ok
    assert admin.post(f"{AN_Q}/delete/{qid}").ok
    assert admin.post(f"{AN_EDU}/subject/delete/{sid}").ok
