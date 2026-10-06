# 二、API 接口清单

> 提取自源码 `controller/admin`、`controller/student`、`controller/wx`
> 约定：除登录/登出外均为 **POST**；请求体 JSON；响应体统一 `{code,message,response}`

## 1. 认证与登出（免角色，登录接口在白名单外需开放）

| # | 接口 | 方法 | 入参 | 说明 |
|---|------|------|------|------|
| 1 | `/api/user/login` | POST | `{userName,password,remember}` | 登录，下发 JSESSIONID |
| 2 | `/api/user/logout` | POST | - | 登出，销毁会话 |

## 2. 管理端接口 `/api/admin/**`（需 ADMIN 角色）

| # | 接口 | 入参（Body/Path） | 说明 |
|---|------|-------------------|------|
| 3 | `/api/admin/dashboard/index` | `{}` | 仪表盘统计 |
| 4 | `/api/admin/education/subject/list` | `{}` | 学科全量列表 |
| 5 | `/api/admin/education/subject/page` | `{pageIndex,pageSize,id,level}` | 学科分页 |
| 6 | `/api/admin/education/subject/edit` | `{id?,name,level,levelName}` | 新增/修改学科 |
| 7 | `/api/admin/education/subject/select/{id}` | path id | 学科详情 |
| 8 | `/api/admin/education/subject/delete/{id}` | path id | 逻辑删除学科 |
| 9 | `/api/admin/question/page` | `{pageIndex,pageSize,id,level,subjectId,questionType}` | 题目分页 |
| 10 | `/api/admin/question/edit` | `{id?,questionType,subjectId,title,analyze,score,correct,correctArray,items[],difficult,gradeLevel,itemOrder}` | 新增/修改题目 |
| 11 | `/api/admin/question/select/{id}` | path id | 题目详情 |
| 12 | `/api/admin/question/delete/{id}` | path id | 逻辑删除题目 |
| 13 | `/api/admin/exam/paper/page` | `{pageIndex,pageSize,id,subjectId,level,paperType,taskExamId}` | 试卷分页 |
| 14 | `/api/admin/exam/paper/taskExamPage` | 同上 | 任务试卷分页 |
| 15 | `/api/admin/exam/paper/edit` | `{id?,level,subjectId,paperType,name,suggestTime,limitDateTime[],score,titleItems[]}` | 新增/修改试卷 |
| 16 | `/api/admin/exam/paper/select/{id}` | path id | 试卷详情 |
| 17 | `/api/admin/exam/paper/delete/{id}` | path id | 逻辑删除试卷 |
| 18 | `/api/admin/examPaperAnswer/page` | `{pageIndex,pageSize,subjectId}` | 答卷分页（批改） |
| 19 | `/api/admin/message/page` | `{pageIndex,pageSize,sendUserName}` | 消息分页 |
| 20 | `/api/admin/message/send` | `{title,content,receiveUserIds[]}` | 发送消息 |
| 21 | `/api/admin/task/page` | `{pageIndex,pageSize,gradeLevel}` | 任务分页 |
| 22 | `/api/admin/task/edit` | `{id?,gradeLevel,title,paperItems[]}` | 新增/修改任务 |
| 23 | `/api/admin/task/select/{id}` | path id | 任务详情 |
| 24 | `/api/admin/task/delete/{id}` | path id | 逻辑删除任务 |
| 25 | `/api/admin/user/page/list` | `{pageIndex,pageSize,userName,role}` | 用户分页 |
| 26 | `/api/admin/user/event/page/list` | `{pageIndex,pageSize,userId,userName}` | 用户日志分页 |
| 27 | `/api/admin/user/select/{id}` | path id | 用户详情 |
| 28 | `/api/admin/user/current` | `{}` | 当前管理员 |
| 29 | `/api/admin/user/edit` | `{id?,userName,password,realName,age,sex,birthDay,phone,role,status,userLevel}` | 新增/修改用户 |
| 30 | `/api/admin/user/update` | `{realName,age,sex,birthDay,phone,userLevel}` | 修改资料 |
| 31 | `/api/admin/user/changeStatus/{id}` | path id | 启用/禁用切换 |
| 32 | `/api/admin/user/delete/{id}` | path id | 逻辑删除用户 |
| 33 | `/api/admin/user/selectByUserName` | 原始字符串 userName | 按名检索（下拉） |
| 34 | `/api/admin/upload/configAndUpload` | multipart/action | UEditor 配置/上传（白名单） |
| 35 | `/api/admin/upload/image` | multipart `file` | 头像上传 |

## 3. 学生端接口 `/api/student/**`（需 STUDENT 角色）

| # | 接口 | 入参 | 说明 |
|---|------|------|------|
| 36 | `/api/student/user/current` | `{}` | 当前学生资料 |
| 37 | `/api/student/user/register` | `{userName,password,userLevel}` | 注册（白名单） |
| 38 | `/api/student/user/update` | `{realName,age,sex,birthDay,phone,userLevel}` | 修改资料 |
| 39 | `/api/student/user/log` | `{}` | 操作日志 |
| 40 | `/api/student/user/message/page` | `{pageIndex,pageSize,receiveUserId}` | 消息分页 |
| 41 | `/api/student/user/message/unreadCount` | `{}` | 未读数 |
| 42 | `/api/student/user/message/read/{id}` | path id | 标记已读 |
| 43 | `/api/student/dashboard/index` | `{}` | 考试首页（固定/时段试卷） |
| 44 | `/api/student/dashboard/task` | `{}` | 任务列表 |
| 45 | `/api/student/education/subject/list` | `{}` | 本年级学科 |
| 46 | `/api/student/education/subject/select/{id}` | path id | 学科详情 |
| 47 | `/api/student/exam/paper/select/{id}` | path id | 试卷详情（拉卷） |
| 48 | `/api/student/exam/paper/pageList` | `{pageIndex,pageSize,paperType,subjectId,levelId}` | 试卷分页 |
| 49 | `/api/student/exampaper/answer/pageList` | `{pageIndex,pageSize,subjectId}` | 我的答卷分页 |
| 50 | `/api/student/exampaper/answer/answerSubmit` | `{id,doTime,score,answerItems[{questionId,itemOrder,doRight,content,contentArray,score,questionScore}]}` | 提交答卷 |
| 51 | `/api/student/exampaper/answer/edit` | 同上 | 教师批改提交 |
| 52 | `/api/student/exampaper/answer/read/{id}` | path id | 回看答卷 |
| 53 | `/api/student/question/answer/page` | `{pageIndex,pageSize}` | 错题分页 |
| 54 | `/api/student/question/answer/select/{id}` | path id | 错题详情 |
| 55 | `/api/student/upload/image` | multipart `file` | 头像上传 |

## 4. 微信小程序端 `/api/wx/student/**`（Zone 2，抽测）

| # | 接口 | 入参 |
|---|------|------|
| 56 | `/api/wx/student/auth/bind` | `{userName,password,wxOpenId}` |
| 57 | `/api/wx/student/auth/checkBind` | 参数 |
| 58 | `/api/wx/student/auth/unBind` | 参数 |
| 59 | `/api/wx/student/dashboard/index` | `{}` |
| 60 | `/api/wx/student/exampaper/answer/answerSubmit` | 同学生端 |
| 61 | `/api/wx/student/user/current` 等 | 同学生端 |

---

## 5. 接口规模统计

| 分类 | 数量 | 测试覆盖 |
|------|------|----------|
| 管理端 | 22 | ✅ 全覆盖 |
| 学生端 | 18 | ✅ 核心覆盖 |
| 微信端(Zone2) | — | 🔸 抽测 |
| **合计（Zone1）** | **40** | 自动化覆盖 33 个接口路径 |
