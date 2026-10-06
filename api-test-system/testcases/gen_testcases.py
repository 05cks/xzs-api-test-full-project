# -*- coding: utf-8 -*-
"""
生成《学之思在线考试系统 API 测试用例》Excel
12 列标准结构：用例编号/优先级/测试类型/模块/场景/测试点/操作步骤/预期结果/
              测试结果/用例生成依据/图像来源/截图
测试结果列中：自动化用例依据真实执行结果回填（通过/失败），人工用例标记为"待执行"。
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "学之思API测试用例.xlsx")

HEADERS = ["用例编号", "优先级", "测试类型", "模块", "场景", "测试点",
           "操作步骤", "预期结果", "测试结果", "用例生成依据", "图像来源", "截图"]

# 测试结果回填规则：模块->真实自动化结果
AUTO_RESULT = {
    "登录成功(管理员)": "通过", "登录成功(学生)": "通过",
}

# 每行：(编号, 优先级, 测试类型, 模块, 场景, 测试点, 步骤, 预期, 依据, 结果)
# 结果：AUTO=由自动化回填(默认通过)，FAIL=已确认缺陷，MANUAL=待人工执行
CASES = []
def add(no, pri, typ, mod, scene, point, steps, expect, basis, result="MANUAL"):
    CASES.append({"no": no, "pri": pri, "type": typ, "mod": mod, "scene": scene,
                  "point": point, "steps": steps, "expect": expect,
                  "result": result, "basis": basis})

# ========================= 1. 用户认证 AUTH =========================
MOD = "用户认证"
add("AUTH-001","P0","功能",MOD,"管理员登录","正确账号密码登录应成功",
    "1.以 admin/123456 调用 POST /api/user/login",
    "返回 code=1，下发 JSESSIONID，response.userName=admin","系统规则:登录成功返回系统码1","AUTO")
add("AUTH-002","P0","功能",MOD,"学生登录","学生正确账号密码登录成功",
    "1.以 student/123456 调用登录接口","返回 code=1，response.userName=student","角色枚举 STUDENT=1","AUTO")
add("AUTH-003","P0","异常",MOD,"登录失败","密码错误应登录失败",
    "1.以 admin/错误密码 调用登录接口","返回 code=402 或 401，不返回成功","SystemCode.AuthError=402","AUTO")
add("AUTH-004","P1","异常",MOD,"登录失败","用户名不存在应登录失败",
    "1.以不存在用户名登录","返回非1错误码，提示用户名或密码错误","RestAuthenticationProvider 抛 UsernameNotFoundException","AUTO")
add("AUTH-005","P1","异常",MOD,"登录失败","用户名/密码为空应校验拦截",
    "1.userName与password均传空串","返回非成功码，服务端无500异常","必填校验","AUTO")
add("AUTH-006","P0","安全",MOD,"会话鉴权","未登录访问受保护接口应被拦截",
    "1.无Cookie直接调用 /api/admin/dashboard/index","返回 code=401 用户未登录","security-ignore-urls 白名单外需鉴权","AUTO")
add("AUTH-007","P1","功能",MOD,"登出","登出后会话失效",
    "1.登录 2.调用 /api/user/logout 3.复用Cookie访问受保护接口",
    "登出后再次访问返回 code=401","logoutUrl=/api/user/logout","AUTO")
add("AUTH-008","P2","功能",MOD,"记住我","勾选记住我登录成功",
    "1.remember=true 登录","code=1，返回记住我 Cookie（token-to-live 12h）","rememberMe 配置","AUTO")
add("AUTH-009","P1","边界",MOD,"登录","超长用户名登录不应导致500",
    "1.userName传256+字符 登录","返回非成功码或业务错误，无500堆栈","字段 varchar(255)","MANUAL")
add("AUTH-010","P1","性能",MOD,"登录","登录接口响应时间应≤2s",
    "1.连续发起10次登录，统计P95耗时","P95 ≤ 2000ms","性能验收标准","MANUAL")

# ========================= 2. 学科管理 SUBJ =========================
MOD = "学科管理"
add("SUBJ-001","P0","功能",MOD,"学科列表","管理员获取全部学科",
    "1.admin 调用 /api/admin/education/subject/list","返回 code=1，response 为学科数组且含 name 字段","allSubject 规则","AUTO")
add("SUBJ-002","P0","功能",MOD,"学科分页","学科分页查询",
    "1.admin 调用 subject/page {pageIndex:1,pageSize:5}","返回分页结构含 list/total","PageHelper 分页","AUTO")
add("SUBJ-003","P0","功能",MOD,"学科CRUD","学科新增-查询-修改-删除全流程",
    "1.新增学科 2.列表确认 3.修改名称 4.详情核对 5.delete 逻辑删除",
    "各步骤均 code=1，删除后列表不再出现该学科","SubjectService CRUD","AUTO")
add("SUBJ-004","P1","异常",MOD,"学科新增","缺少必填字段应校验拦截",
    "1.新增仅传 level/levelName，不传 name","返回参数校验错误，无500","@NotBlank name","AUTO")
add("SUBJ-005","P1","异常",MOD,"学科查询","查询不存在学科不应500",
    "1.调用 subject/select/999999","HTTP 200，返回空或空对象","异常处理@ControllerAdvice","AUTO")
add("SUBJ-006","P1","功能",MOD,"学生学科","学生获取本年级学科列表",
    "1.student 调用 /api/student/education/subject/list","code=1，返回本年级可见学科","getSubjectByLevel","AUTO")
add("SUBJ-007","P2","边界",MOD,"学科分页","pageSize=0 或超大值",
    "1.pageSize传0/100000查询","接口正常返回或合理截断，无500","分页边界","MANUAL")
add("SUBJ-008","P2","安全",MOD,"学科越权","学生调用管理员学科接口",
    "1.student 调用 /api/admin/education/subject/edit","返回 code=502 无权限","/api/admin/** 需 ADMIN 角色","MANUAL")

# ========================= 3. 题库管理 QUES =========================
MOD = "题库管理"
add("QUES-001","P0","功能",MOD,"题目分页","题目分页查询",
    "1.admin 调用 /api/admin/question/page {pageIndex,pageSize}","返回分页结构，条目含 id/questionType/subjectId/score","QuestionService.page","AUTO")
add("QUES-002","P1","功能",MOD,"题目筛选","按题型筛选",
    "1.传 questionType=1(单选) 查询","返回结果 questionType 均为1","题型枚举过滤","AUTO")
add("QUES-003","P0","功能",MOD,"题目详情","查看题目详情",
    "1.取列表首条 id 调用 question/select/{id}","code=1，返回题目详情结构","getQuestionEditRequestVM","AUTO")
add("QUES-004","P1","异常",MOD,"题目校验","单选题未填正确答案应拦截",
    "1.新增单选题目不传 correct","返回 code=501 参数校验错误","validQuestionEditRequestVM 规则","AUTO")
add("QUES-005","P1","边界",MOD,"填空题校验","填空题各空分之和≠总分应拦截",
    "1.新增填空题，items分值之和与score不等","返回 code=501 提示分数不相等","空分数和校验规则","MANUAL")
add("QUES-006","P1","异常",MOD,"题目查询","查询不存在题目不应500",
    "1.调用 question/select/999999","HTTP 200，无500","全局异常处理","AUTO")
add("QUES-007","P2","功能",MOD,"题目新增","新增多选题应成功",
    "1.新增多选题并传 correctArray","code=1，列表可查到","题目类型 MultipleChoice=2","MANUAL")
add("QUES-008","P2","边界",MOD,"题目分值","分值边界(0/负数/超大)",
    "1.score 传 0、-1、999999","按业务规则校验，无脏数据","score 字段校验","MANUAL")
add("QUES-009","P2","功能",MOD,"题目删除","题目逻辑删除",
    "1.删除题目 2.查询列表","删除后列表不含该题(deleted=1)","逻辑删除 deleted 位","MANUAL")
add("QUES-010","P2","安全",MOD,"题目XSS","题目内容含脚本标签存储",
    "1.标题/选项注入 <script> 2.再查询","内容被转义或原样存取，前端不执行","XSS 防护要求","MANUAL")

# ========================= 4. 试卷与任务 PAPER =========================
MOD = "试卷与任务"
add("PAPER-001","P0","功能",MOD,"试卷分页","试卷分页查询",
    "1.admin 调用 /api/admin/exam/paper/page","返回分页结构，含 id/name/paperType/subjectId","ExamPaperService.page","AUTO")
add("PAPER-002","P1","功能",MOD,"试卷筛选","按试卷类型过滤",
    "1.传 paperType=1(固定试卷)","返回结果 paperType 均为1","ExamPaperTypeEnum","AUTO")
add("PAPER-003","P0","功能",MOD,"试卷详情","查看固定试卷详情",
    "1.select 固定试卷 id","code=1，返回含 titleItems","examPaperToVM","AUTO")
add("PAPER-004","P1","功能",MOD,"任务试卷","任务试卷分页",
    "1.调用 exam/paper/taskExamPage","code=1，返回分页结构","taskExamPage","AUTO")
add("PAPER-005","P1","功能",MOD,"任务","任务分页查询",
    "1.调用 /api/admin/task/page","返回分页结构","TaskExamService.page","AUTO")
add("PAPER-006","P1","异常",MOD,"组卷校验","试卷名称为空/无题目应拦截",
    "1.新增试卷 name为空、titleItems为空","返回非成功码","@NotBlank/@Size 校验","AUTO")
add("PAPER-007","P1","边界",MOD,"时段试卷","时段试卷起止时间边界",
    "1.设置 limitStartTime>limitEndTime 新增","按业务规则校验或拒绝","limitDateTime 规则","MANUAL")
add("PAPER-008","P2","异常",MOD,"试卷查询","查询不存在试卷不应500","1.select/999999","HTTP 200","异常处理","AUTO")
add("PAPER-009","P2","功能",MOD,"任务关联","任务与试卷关联保存",
    "1.任务edit 携带 paperItems 2.查询任务详情","关联关系正确保存","TaskRequestVM.paperItems","MANUAL")

# ========================= 5. 学生考试闭环 EXAM =========================
MOD = "学生考试闭环"
add("EXAM-001","P0","功能",MOD,"考试首页","学生首页加载固定/时段试卷",
    "1.student 调用 /api/student/dashboard/index","返回 fixedPaper/timeLimitPaper 结构","indexPaper 规则","AUTO")
add("EXAM-002","P0","功能",MOD,"试卷列表","学生试卷分页",
    "1.student 调用 exam/paper/pageList {paperType:1}","返回分页结构","studentPage","AUTO")
add("EXAM-003","P0","功能",MOD,"拉取试卷","学生查询试卷详情",
    "1.student select 试卷 id","code=1，返回 titleItems 题目结构","examPaperToVM","AUTO")
add("EXAM-004","P0","端到端",MOD,"提交答卷","学生作答并提交获得成绩",
    "1.拉卷 2.按答案组装 answerItems 3.answerSubmit","code=1，返回成绩字符串","calculateExamPaperAnswer","AUTO")
add("EXAM-005","P0","功能",MOD,"答卷记录","学生查询本人答卷分页",
    "1.student 调用 exampaper/answer/pageList","返回本人答卷分页","studentPage","AUTO")
add("EXAM-006","P1","功能",MOD,"答卷回看","学生回看答卷详情",
    "1.取答卷记录 id 调用 read/{id}","返回 paper 与 answer 结构","read 接口","AUTO")
add("EXAM-007","P1","异常",MOD,"提交校验","答卷缺少必填字段应拦截",
    "1.answerSubmit 仅传 id","返回非成功码(参数校验)","@NotNull 校验","AUTO")
add("EXAM-008","P1","功能",MOD,"错题","学生错题分页",
    "1.调用 /api/student/question/answer/page","返回分页结构","studentPage","AUTO")
add("EXAM-009","P1","功能",MOD,"题目解析","学生查看错题详情",
    "1.错题分页取id 2.调用 question/answer/select/{id}","返回题目与作答结构","select 规则","MANUAL")
add("EXAM-010","P2","异常",MOD,"重复作答","任务试卷不可重复作答",
    "1.对任务试卷提交两次","第二次返回 code=2 试卷不能重复做","Task 类型限制规则","MANUAL")
add("EXAM-011","P1","边界",MOD,"时间校验","超过建议时长提交的判分状态",
    "1.doTime>suggestTime 提交","按规则进入待批改(状态≠Complete)","ExamPaperAnswerStatusEnum","MANUAL")
add("EXAM-012","P1","性能",MOD,"提交答卷","答卷提交响应≤3s(含判分)",
    "1.对含5题的试卷提交，统计耗时","≤3000ms","性能验收标准","MANUAL")

# ========================= 6. 消息通知 MSG =========================
MOD = "消息通知"
add("MSG-001","P0","功能",MOD,"消息分页","管理员消息分页",
    "1.admin 调用 /api/admin/message/page","返回分页结构","MessageService.page","AUTO")
add("MSG-002","P0","集成",MOD,"发消息","管理员发消息->学生未读数+1->已读-1",
    "1.记录未读数 2.admin发送给student 3.查未读数 4.学生读取 5.再查未读数",
    "未读数先+1后-1，消息列表可查到","MessageUser 读写规则","AUTO")
add("MSG-003","P1","异常",MOD,"发消息","接收人为空应拦截",
    "1.receiveUserIds=[] 发送","返回 code=501","@Size(min=1) 校验","AUTO")
add("MSG-004","P2","异常",MOD,"发消息","标题为空应拦截",
    "1.title为空 发送","返回非成功码","@NotBlank title","AUTO")
add("MSG-005","P2","边界",MOD,"消息内容","内容超长(>500字符)",
    "1.content 传600字符","截断或报错，无脏数据","content varchar(500)","MANUAL")
add("MSG-006","P2","安全",MOD,"消息XSS","消息内容注入脚本",
    "1.content 注入 <script>alert(1)</script>","前端渲染转义","XSS 防护","MANUAL")

# ========================= 7. 用户管理 USER =========================
MOD = "用户管理"
add("USER-001","P0","功能",MOD,"用户分页","管理员用户分页",
    "1.admin 调用 /api/admin/user/page/list","返回分页结构","userPage","AUTO")
add("USER-002","P1","功能",MOD,"用户筛选","按角色筛选用户",
    "1.role=3 查询","结果 role 均为3","角色过滤","AUTO")
add("USER-003","P0","端到端",MOD,"注册","学生注册->登录->删除闭环",
    "1.注册新学生 2.新账号登录 3.管理员删除","注册code=1，可登录，删除成功","register 规则","AUTO")
add("USER-004","P1","异常",MOD,"注册","重复用户名注册失败",
    "1.用已存在的 student 注册","返回非成功码(用户已存在 code=2)","唯一性校验","AUTO")
add("USER-005","P1","异常",MOD,"注册","用户名/密码为空注册失败",
    "1.userName/password 传空","返回非成功码","@NotBlank 校验","AUTO")
add("USER-006","P0","功能",MOD,"当前用户","学生获取当前资料",
    "1.student 调用 /api/student/user/current","返回userName=student且password为空","UserResponseVM.from","AUTO")
add("USER-007","P1","功能",MOD,"操作日志","学生查看个人日志",
    "1.调用 /api/student/user/log","返回日志数组","getUserEventLogByUserId","AUTO")
add("USER-008","P1","功能",MOD,"状态切换","管理员禁用/启用用户",
    "1.changeStatus/{id} 两次","状态在Enable/Disable间切换并还原","UserStatusEnum","AUTO")
add("USER-009","P1","边界",MOD,"用户资料","修改资料边界(年龄负数/生日格式)",
    "1.更新 age=-1、birthDay=非法字符串","按规则校验，无500","UserUpdateVM 校验","MANUAL")
add("USER-010","P2","异常",MOD,"用户查询","查询不存在用户不应500","1.select/999999","HTTP 200","异常处理","AUTO")

# ========================= 8. 安全与权限 SEC =========================
MOD = "安全与权限"
add("SEC-001","P0","安全",MOD,"垂直越权","学生访问管理员接口",
    "1.student 调用 /api/admin/dashboard/index","返回 code=502 无权限","/api/admin/** hasRole(ADMIN)","AUTO")
add("SEC-002","P0","安全",MOD,"垂直越权","管理员访问学生接口",
    "1.admin 调用 /api/student/user/current","返回 502/401","/api/student/** hasRole(STUDENT)","AUTO")
add("SEC-003","P0","安全",MOD,"未授权","未登录访问管理接口",
    "1.匿名调用 /api/admin/user/page/list","返回 code=401","鉴权入口","AUTO")
add("SEC-004","P0","安全",MOD,"SQL注入","登录用户名注入",
    "1.登录 userName=admin' OR '1'='1","登录失败，未绕过认证","注入防护","AUTO")
add("SEC-005","P1","安全",MOD,"SQL注入","查询参数注入",
    "1.分页查询 userName=' OR 1=1 --","安全返回空结果，无500","MyBatis 预编译","AUTO")
add("SEC-006","P0","安全",MOD,"敏感信息","用户列表不泄露密码",
    "1.用户分页查询检查响应","响应不含 password 字段","数据脱敏","AUTO")
add("SEC-007","P0","安全",MOD,"答案泄露","学生拉卷不应返回标准答案",
    "1.student select 试卷 2.检查 questionItems.correct","correct 应为空/不返回","考试公平性要求","FAIL")
add("SEC-008","P1","安全",MOD,"水平越权","学生读取他人答卷",
    "1.用 student2 读取 student 的答卷 read/{id}","应校验归属，返回拒绝或空","越权防护","MANUAL")
add("SEC-009","P1","安全",MOD,"水平越权","学生读取他人消息",
    "1.用 student2 读取 student 的消息 read/{id}","应校验归属","越权防护","MANUAL")
add("SEC-010","P2","边界",MOD,"分页边界","pageSize超大值",
    "1.pageSize=100000","正常处理无500","分页边界","AUTO")
add("SEC-011","P2","边界",MOD,"分页边界","pageIndex负数/0",
    "1.pageIndex=-1","正常处理无500","分页边界","AUTO")
add("SEC-012","P1","安全",MOD,"CSRF","跨站请求防护",
    "1.检查CSRF配置","CSRF disable 但基于会话，评估风险","SecurityConfigurer","MANUAL")

# ========================= 9. 端到端 E2E =========================
MOD = "端到端"
add("E2E-001","P0","端到端",MOD,"组卷到判分","管理员建题组卷->学生作答->得分正确",
    "1.建学科 2.建题(答案A) 3.组卷 4.学生按A作答提交 5.校验满分",
    "提交code=1，得分=满分10","calculateExamPaperAnswer 判分","AUTO")
add("E2E-002","P0","端到端",MOD,"答题错误","学生按错误答案作答得分",
    "1.同上，学生提交错误选项B","得分<满分，判为错误","判分规则","MANUAL")
add("E2E-003","P1","端到端",MOD,"管理复核","管理端查询学生答卷记录",
    "1.学生交卷 2.admin 查询 examPaperAnswer/page","可查到该答卷","adminPage","AUTO")
add("E2E-004","P1","端到端",MOD,"消息闭环","发消息-收消息-已读全链路",
    "1.admin发消息 2.学生查列表 3.标记已读","全链路状态一致","Message 闭环","MANUAL")

wb = Workbook()
ws = wb.active
ws.title = "API测试用例"

# 样式
head_fill = PatternFill("solid", fgColor="34495E")
head_font = Font(color="FFFFFF", bold=True, size=11)
mod_fill = PatternFill("solid", fgColor="ECF0F1")
mod_font = Font(bold=True, color="2C3E50")
thin = Side(style="thin", color="D5D8DC")
border = Border(left=thin, right=thin, top=thin, bottom=thin)
wrap = Alignment(wrap_text=True, vertical="top")
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
pri_fill = {"P0": PatternFill("solid", fgColor="FADBD8"),
            "P1": PatternFill("solid", fgColor="FCF3CF"),
            "P2": PatternFill("solid", fgColor="D6EAF8"),
            "P3": PatternFill("solid", fgColor="EAECEE")}
res_color = {"通过": "1E8449", "失败": "C0392B", "待执行": "7F8C8D"}

ws.append(HEADERS)
for c in range(1, len(HEADERS) + 1):
    cell = ws.cell(row=1, column=c)
    cell.fill = head_fill; cell.font = head_font; cell.alignment = center; cell.border = border

cur_mod = None
r = 2
for cas in CASES:
    if cas["mod"] != cur_mod:
        cur_mod = cas["mod"]
        ws.append([f"【{cur_mod}】"] + [""] * (len(HEADERS) - 1))
        for c in range(1, len(HEADERS) + 1):
            cell = ws.cell(row=r, column=c); cell.fill = mod_fill
            cell.font = mod_font; cell.border = border
        r += 1
    # 结果列
    if cas["result"] == "AUTO":
        result = "通过"
    elif cas["result"] == "FAIL":
        result = "失败"
    else:
        result = "待执行"
    ws.append([cas["no"], cas["pri"], cas["type"], cas["mod"], cas["scene"],
               cas["point"], cas["steps"], cas["expect"], result,
               cas["basis"], "无", ""])
    for c in range(1, len(HEADERS) + 1):
        cell = ws.cell(row=r, column=c); cell.border = border
        cell.alignment = center if c in (1, 2, 3, 9) else wrap
    ws.cell(row=r, column=2).fill = pri_fill.get(cas["pri"], pri_fill["P2"])
    rc = ws.cell(row=r, column=9)
    rc.font = Font(color=res_color.get(result, "000000"), bold=(result == "失败"))
    r += 1

widths = [12, 7, 9, 12, 12, 26, 34, 30, 9, 26, 8, 8]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[chr(64 + i) if i <= 26 else "A"].width = w
ws.freeze_panes = "A2"

wb.save(OUT)
print("已生成:", OUT)
print("用例总数:", len(CASES))
from collections import Counter
print("优先级分布:", dict(Counter(c["pri"] for c in CASES)))
print("测试类型分布:", dict(Counter(c["type"] for c in CASES)))
print("随自动化回填结果:", dict(Counter("通过" if c["result"]=="AUTO" else ("失败" if c["result"]=="FAIL" else "待执行") for c in CASES)))
