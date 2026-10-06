-- =============================================================================
-- 学之思在线考试系统 · API 测试数据初始化脚本
-- 数据库：exam (MySQL 8.0)  字符集：utf8mb4
-- 说明：
--   * 本脚本仅用于测试环境造数，生产环境禁止执行！
--   * 采用固定 ID 段（9000+）避免与业务数据冲突，可重复执行（先删后插）。
--   * 密码字段为 RSA 公钥加密后的密文；这里统一使用明文 123456 对应的密文。
--   * 回滚见文件末尾 CLEANUP 段。
-- 执行：mysql -uroot -p exam < init_test_data.sql
-- =============================================================================
SET NAMES utf8mb4;

-- ---------------------------------------------------------------------------
-- 1. 测试用户（密码明文均为 123456）
--    role: 1=学生 3=管理员；status: 1=启用 2=禁用
-- ---------------------------------------------------------------------------
DELETE FROM t_user WHERE id BETWEEN 9000 AND 9099;
INSERT INTO t_user
 (id, user_uuid, user_name, password, real_name, age, sex, user_level, phone, role, status, create_time, deleted)
VALUES
 (9001, UUID(), 'apitest_stu',   'D1AGFL+Gx37t0NPG4d6biYP5Z31cNbwhK5w1lUeiHB2zagqbk8efYfSjYoh1Z/j1dkiRjHU+b0EpwzCh8IGsksJjzD65ci5LsnodQVf4Uj6D3pwoscXGqmkjjpzvSJbx42swwNTA+QoDU8YLo7JhtbUK2X0qCjFGpd+8eJ5BGvk=', '接口测试学生', 20, 1, 1, '13800000001', 1, 1, NOW(), 0),
 (9002, UUID(), 'apitest_admin', 'D1AGFL+Gx37t0NPG4d6biYP5Z31cNbwhK5w1lUeiHB2zagqbk8efYfSjYoh1Z/j1dkiRjHU+b0EpwzCh8IGsksJjzD65ci5LsnodQVf4Uj6D3pwoscXGqmkjjpzvSJbx42swwNTA+QoDU8YLo7JhtbUK2X0qCjFGpd+8eJ5BGvk=', '接口测试管理员', 30, 1, NULL, '13800000002', 3, 1, NOW(), 0);

-- ---------------------------------------------------------------------------
-- 2. 测试学科（等级=900，隔离于真实年级）
-- ---------------------------------------------------------------------------
DELETE FROM t_subject WHERE id BETWEEN 9000 AND 9099;
INSERT INTO t_subject (id, name, level, level_name, item_order, deleted) VALUES
 (9001, '接口测试学科-数学', 900, '接口测试年级', 900, 0),
 (9002, '接口测试学科-语文', 900, '接口测试年级', 901, 0);

-- ---------------------------------------------------------------------------
-- 3. 测试题目（覆盖 单选/多选/判断/填空/简答 五种题型）
--    题目内容载体 t_text_content 使用 9000+ ID 段
-- ---------------------------------------------------------------------------
DELETE FROM t_question WHERE id BETWEEN 9000 AND 9099;
DELETE FROM t_text_content WHERE id BETWEEN 9000 AND 9099;

INSERT INTO t_text_content (id, content, create_time) VALUES
 (9001, '{"titleContent":"<p>1+1=? 接口测试单选题</p>","content":null,"analyze":"基础运算","questionItemObjects":[{"prefix":"A","content":"2","score":"10","itemUuid":"t9001a"},{"prefix":"B","content":"3","score":"0","itemUuid":"t9001b"}]}', NOW()),
 (9002, '{"titleContent":"<p>以下属于水果的有? 接口测试多选题</p>","content":null,"analyze":"常识","questionItemObjects":[{"prefix":"A","content":"苹果","score":"5","itemUuid":"t9002a"},{"prefix":"B","content":"香蕉","score":"5","itemUuid":"t9002b"},{"prefix":"C","content":"桌子","score":"0","itemUuid":"t9002c"}]}', NOW()),
 (9003, '{"titleContent":"<p>地球是圆的。接口测试判断题</p>","content":null,"analyze":"常识","questionItemObjects":[{"prefix":"A","content":"正确","score":"10","itemUuid":"t9003a"},{"prefix":"B","content":"错误","score":"0","itemUuid":"t9003b"}]}', NOW());

INSERT INTO t_question
 (id, question_type, subject_id, score, grade_level, difficult, correct, info_text_content_id, create_user, status, create_time, deleted)
VALUES
 (9001, 1, 9001, 10,  900, 1, 'A',   9001, 9002, 1, NOW(), 0),  -- 单选
 (9002, 2, 9001, 10,  900, 2, 'A,B', 9002, 9002, 1, NOW(), 0),  -- 多选
 (9003, 3, 9001, 10,  900, 1, 'A',   9003, 9002, 1, NOW(), 0);  -- 判断

-- ---------------------------------------------------------------------------
-- 4. 测试试卷（固定试卷，含上面三题，总分 30）
--    试卷框架内容载体 t_text_content 9000
-- ---------------------------------------------------------------------------
DELETE FROM t_exam_paper WHERE id BETWEEN 9000 AND 9099;
INSERT INTO t_text_content (id, content, create_time) VALUES
 (9000, '[{"name":"一、客观题","questionItems":[{"id":9001,"itemOrder":0},{"id":9002,"itemOrder":1},{"id":9003,"itemOrder":2}]}]', NOW());

INSERT INTO t_exam_paper
 (id, name, subject_id, paper_type, grade_level, score, question_count, suggest_time, create_user, create_time, deleted)
VALUES
 (9001, '接口测试固定试卷', 9001, 1, 900, 30, 3, 30, 9002, NOW(), 0);

-- =============================================================================
-- CLEANUP（测试完成后清理，按需执行）
-- =============================================================================
-- DELETE FROM t_exam_paper_answer WHERE exam_paper_id BETWEEN 9000 AND 9099;
-- DELETE FROM t_exam_paper_question_customer_answer WHERE exam_paper_id BETWEEN 9000 AND 9099;
-- DELETE FROM t_exam_paper WHERE id BETWEEN 9000 AND 9099;
-- DELETE FROM t_question WHERE id BETWEEN 9000 AND 9099;
-- DELETE FROM t_subject WHERE id BETWEEN 9000 AND 9099;
-- DELETE FROM t_text_content WHERE id BETWEEN 9000 AND 9099;
-- DELETE FROM t_user WHERE id BETWEEN 9000 AND 9099;
-- DELETE FROM t_user_event_log WHERE user_id BETWEEN 9000 AND 9099;
