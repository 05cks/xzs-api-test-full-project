# -*- coding: utf-8 -*-
"""
学之思在线考试系统 - API 自动化测试配置
被测试系统：http://localhost:8000  (Spring Boot 2.1.6 + MySQL)
鉴权方式：Spring Security 会话（JSESSIONID Cookie），登录接口 POST /api/user/login
"""
import os

# ---------------------------------------------------------------------------
# 被测服务地址（按环境覆盖：XZS_BASE_URL）
# ---------------------------------------------------------------------------
BASE_URL = os.getenv("XZS_BASE_URL", "http://localhost:8000")

# ---------------------------------------------------------------------------
# 测试账号（密码已通过 RSA 私钥从库中密文还原，见 scripts/decrypt_pwd.py）
# ---------------------------------------------------------------------------
ADMIN = {"userName": "admin",  "password": "123456", "remember": False}
STUDENT = {"userName": "student", "password": "123456", "remember": False}
STUDENT2 = {"userName": "ki", "password": "123", "remember": False}

# ---------------------------------------------------------------------------
# 业务常量（与后端枚举保持一致）
# ---------------------------------------------------------------------------
CODE_SUCCESS = 1              # SystemCode.OK
CODE_TOKEN_ERROR = 400        # 登录令牌失效
CODE_UNAUTHORIZED = 401       # 未登录
CODE_AUTH_ERROR = 402         # 用户名或密码错误
CODE_INNER_ERROR = 500        # 系统内部错误
CODE_PARAM_ERROR = 501        # 参数验证错误
CODE_ACCESS_DENIED = 502      # 无权限

ROLE_STUDENT = 1
ROLE_ADMIN = 3
STATUS_ENABLE = 1
STATUS_DISABLE = 2

# QuestionTypeEnum
Q_SINGLE, Q_MULTI, Q_TF, Q_GAP, Q_SHORT = 1, 2, 3, 4, 5
# ExamPaperTypeEnum
PAPER_FIXED, PAPER_TIME_LIMIT, PAPER_TASK = 1, 4, 6

# ---------------------------------------------------------------------------
# 超时与路径
# ---------------------------------------------------------------------------
TIMEOUT = 15
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(ROOT_DIR, "..", "reports")
