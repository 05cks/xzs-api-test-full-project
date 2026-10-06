# -*- coding: utf-8 -*-
"""pytest 全局夹具：会话级客户端 + 用例结果收集（供报告/缺陷文档使用）。"""
import json
import os
import time
import pytest

from api_client import ApiClient, new_client, PERF_RECORDS
import config as cfg

# ---------------------------------------------------------------------------
# 结果收集器：所有用例结果写入 reports/run_result.json
# ---------------------------------------------------------------------------
RESULT_FILE = os.path.join(cfg.REPORT_DIR, "run_result.json")
COLLECTED = []


def pytest_configure(config):
    os.makedirs(cfg.REPORT_DIR, exist_ok=True)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """收集每条用例的执行结果。"""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        result = rep.outcome
        if hasattr(rep, "wasxfail"):
            result = "xfailed" if rep.outcome == "skipped" else "xpassed"
        COLLECTED.append({
            "nodeid": item.nodeid,
            "name": item.name,
            "outcome": result,
            "duration_s": round(rep.duration, 3),
            "longrepr": str(rep.longrepr)[:800] if rep.longrepr else "",
            "markers": [m.name for m in item.iter_markers()],
        })


def pytest_sessionfinish(session, exitstatus):
    os.makedirs(cfg.REPORT_DIR, exist_ok=True)
    summary = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "base_url": cfg.BASE_URL,
        "total": len(COLLECTED),
        "passed": sum(1 for r in COLLECTED if r["outcome"] == "passed"),
        "failed": sum(1 for r in COLLECTED if r["outcome"] == "failed"),
        "skipped": sum(1 for r in COLLECTED if r["outcome"] == "skipped"),
        "xfailed": sum(1 for r in COLLECTED if r["outcome"] == "xfailed"),
        "results": COLLECTED,
        "perf": PERF_RECORDS,
    }
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 夹具
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def admin():
    """管理员会话（role=ADMIN，可访问 /api/admin/**）。"""
    return new_client("admin", cfg.ADMIN)


@pytest.fixture(scope="session")
def student():
    """学生会话（role=STUDENT，可访问 /api/student/**）。"""
    return new_client("student", cfg.STUDENT)


@pytest.fixture(scope="session")
def student2():
    """第二学生会话（用于多用户隔离/越权测试）。"""
    return new_client("student2", cfg.STUDENT2)


@pytest.fixture()
def anon():
    """未登录会话。"""
    return ApiClient("anonymous")
