# 学之思在线考试系统 · API 测试体系

> 为「学之思在线考试系统（xzs-mysql）」建立的完整 API 测试解决方案：
> 覆盖 **需求分析 → 测试计划 → 用例设计 → 测试数据 → 手工测试 → 缺陷管理 → 回归测试 → 自动化测试 → 接口测试** 全流程。

---

## 📁 目录结构

```
api-test-system/
├── README.md                        # 本文件：体系总览与使用指南
├── docs/                            # 测试文档（Markdown）
│   ├── 01-需求分析与测试范围.md        # 需求建模、规则、缺口、风险
│   ├── 02-API接口清单.md              # 40 个接口明细
│   ├── 03-测试计划.md                 # 策略、环境、进度、出入口准则
│   ├── 04-手工测试用例与执行记录.md     # 手工执行记录
│   ├── 05-缺陷记录.md                 # 5 个缺陷（含 1 个严重）
│   ├── 06-回归测试记录.md              # 回归策略与多轮结果
│   └── 07-接口测试报告.md              # ★ 执行结果总报告
├── testcases/
│   ├── 学之思API测试用例.xlsx          # ★ 81 条测试用例（12 列标准格式）
│   └── gen_testcases.py              # 用例生成脚本
├── testdata/
│   ├── init_test_data.sql           # SQL 造数脚本（9000+ ID 段，可回滚）
│   └── test_data.json               # 数据驱动测试数据集
├── automation/                      # ★ 自动化测试框架
│   ├── config.py                    # 配置（地址/账号/枚举/错误码）
│   ├── api_client.py                # 接口客户端封装
│   ├── conftest.py                  # pytest 夹具 + 结果收集
│   ├── pytest.ini                   # 标记与参数
│   ├── run_tests.py                 # 一键运行 + 报告生成
│   ├── requirements.txt
│   └── tests/                       # 9 个模块 57 条自动化用例
│       ├── test_01_auth.py          # 认证鉴权
│       ├── test_02_subject.py       # 学科管理
│       ├── test_03_question.py      # 题库管理
│       ├── test_04_exampaper.py     # 试卷与任务
│       ├── test_05_answer.py        # 学生考试闭环
│       ├── test_06_message.py       # 消息通知
│       ├── test_07_user.py          # 用户管理
│       ├── test_08_security.py      # 安全与权限
│       └── test_09_e2e.py           # 端到端
├── postman/
│   └── 学之思API测试.postman_collection.json  # Postman 接口测试集合
├── scripts/
│   └── decrypt_pwd.py               # 解密库中密码（造数/自动化登录辅助）
└── reports/                         # 执行产物（自动生成）
    ├── API自动化测试报告.html         # ★ HTML 可视化报告
    ├── run_result.json              # 结构化结果
    └── evidence_answer_leak.txt     # DEF-001 证据
```

## 🚀 快速开始

### 1. 前置条件
- 后端服务已启动：`http://localhost:8000`（监听确认）
- MySQL 已运行，库 `exam` 可访问
- Python 3.8+，安装依赖：`D:\python38\python.exe -m pip install -r automation/requirements.txt`

### 2. 运行自动化测试

```bash
cd automation

# 全量运行 + 生成 HTML 报告
D:\python38\python.exe run_tests.py

# 只跑 P0 冒烟
D:\python38\python.exe run_tests.py -m p0

# 只跑安全模块
D:\python38\python.exe run_tests.py -m security

# 按关键字
D:\python38\python.exe run_tests.py -k login
```

### 3. 查看报告
打开 `reports/API自动化测试报告.html`。

## 📊 当前测试结果快照

| 指标 | 数值 |
|------|------|
| 自动化用例 | 57 |
| 通过 | 56（98.2%） |
| 预期失败(已确认缺陷) | 1 |
| 测试用例文档 | 81 条（P0:29 / P1:36 / P2:16） |
| 缺陷 | 5（S1 严重×1、S2 高×1、S3 中×3） |
| 接口平均响应 | 11.4 ms |

## ⚠️ 重要发现

**DEF-001（严重）**：学生端拉卷接口 `POST /api/student/exam/paper/select/{id}`
返回了题目的标准答案字段 `correct`，学生可直接作弊。详见 `docs/05-缺陷记录.md`。

## 🔧 关键测试设计说明

| 设计点 | 说明 |
|--------|------|
| 会话保持 | 系统基于 Spring Security Session(Cookie)，客户端用 `requests.Session()` 复用 Cookie |
| 密码处理 | 库中密码为 RSA 公钥加密密文，`scripts/decrypt_pwd.py` 用私钥还原明文用于登录 |
| 数据隔离 | 自动化用例采用时间戳命名 + 用例内清理，不污染业务数据 |
| 结果收集 | `conftest.py` 钩子收集每条用例结果，自动生成 JSON 与 HTML 报告 |

## 📌 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `XZS_BASE_URL` | `http://localhost:8000` | 被测服务地址，可切换环境 |
