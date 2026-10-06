# -*- coding: utf-8 -*-
"""模块6：消息通知（管理员发送 → 学生接收/未读数/已读）"""
import time
import pytest
import config

AMSG = "/api/admin/message"
SMSG = "/api/student/user/message"


@pytest.mark.message
@pytest.mark.p0
def test_admin_message_page(admin):
    """管理员消息分页查询。"""
    r = admin.post(f"{AMSG}/page", {"pageIndex": 1, "pageSize": 10})
    assert r.ok
    assert "list" in r.data


@pytest.mark.message
@pytest.mark.p0
def test_send_message_to_student(admin, student):
    """管理员向学生发送消息，学生未读数增加，读取后已读。"""
    # 发送前未读数
    before = student.post(f"{SMSG}/unreadCount", {}).data or 0
    title = f"自动化通知_{int(time.time())}"
    r = admin.post(f"{AMSG}/send",
                   {"title": title, "content": "这是一条自动化测试消息",
                    "receiveUserIds": [1]})       # 1 = student
    assert r.ok, f"发送消息失败: {r.body}"

    after = student.post(f"{SMSG}/unreadCount", {}).data or 0
    assert after == before + 1, f"未读数未增加: {before} -> {after}"

    # 查询学生消息列表，找到该消息并标记已读
    page = student.post(f"{SMSG}/page", {"pageIndex": 1, "pageSize": 20})
    assert page.ok
    msg = next((m for m in page.data["list"] if m.get("title") == title), None)
    assert msg is not None, "学生未收到刚发送的消息"
    read = student.post(f"{SMSG}/read/{msg['id']}")
    assert read.ok
    after_read = student.post(f"{SMSG}/unreadCount", {}).data or 0
    assert after_read == after - 1, "读取后未读数未减少"


@pytest.mark.message
@pytest.mark.p1
def test_send_message_missing_receiver(admin):
    """发送消息接收人为空时返回参数校验错误。"""
    r = admin.post(f"{AMSG}/send",
                   {"title": "t", "content": "c", "receiveUserIds": []})
    assert r.code == config.CODE_PARAM_ERROR


@pytest.mark.message
@pytest.mark.p2
def test_send_message_blank_title(admin):
    """发送消息标题为空时返回参数校验错误。"""
    r = admin.post(f"{AMSG}/send",
                   {"title": "", "content": "c", "receiveUserIds": [1]})
    assert r.code != config.CODE_SUCCESS
