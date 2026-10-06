# -*- coding: utf-8 -*-
"""
学之思 API 自动化测试 - 统一入口
用法：
    D:\python38\python.exe run_tests.py                # 运行全部用例并生成报告
    D:\python38\python.exe run_tests.py -m p0          # 只跑 P0 冒烟用例
    D:\python38\python.exe run_tests.py -m security    # 只跑安全模块
    D:\python38\python.exe run_tests.py -k login       # 按关键字
"""
import os
import sys
import json
import time
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
REPORT_DIR = os.path.join(ROOT, "..", "reports")
RESULT_FILE = os.path.join(REPORT_DIR, "run_result.json")


def run_pytest(extra_args):
    os.makedirs(REPORT_DIR, exist_ok=True)
    cmd = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider"] + extra_args
    print(">>", " ".join(cmd))
    return subprocess.call(cmd, cwd=ROOT)


def gen_html_report():
    if not os.path.exists(RESULT_FILE):
        print("未找到结果文件", RESULT_FILE)
        return None
    with open(RESULT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    rows = []
    color = {"passed": "#27ae60", "failed": "#e74c3c",
             "skipped": "#95a5a6", "xfailed": "#e67e22", "xpassed": "#8e44ad"}
    for i, r in enumerate(data["results"], 1):
        c = color.get(r["outcome"], "#333")
        rows.append(
            f"<tr><td>{i}</td><td>{r['name']}</td>"
            f"<td style='color:{c};font-weight:600'>{r['outcome']}</td>"
            f"<td>{r['duration_s']}s</td>"
            f"<td style='font-size:12px;color:#666'>{r['longrepr'][:200]}</td></tr>")

    total = data["total"] or 1
    pass_rate = round(data["passed"] / total * 100, 1)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>学之思在线考试系统 - API自动化测试报告</title>
<style>
 body{{font-family:"Microsoft YaHei",Arial,sans-serif;margin:0;background:#f5f6fa;color:#2c3e50}}
 .wrap{{max-width:1200px;margin:0 auto;padding:24px}}
 h1{{font-size:22px}} .sub{{color:#7f8c8d;font-size:13px;margin-bottom:16px}}
 .cards{{display:flex;gap:14px;flex-wrap:wrap;margin:18px 0}}
 .card{{background:#fff;border-radius:10px;padding:16px 22px;box-shadow:0 1px 4px rgba(0,0,0,.06);min-width:130px}}
 .card .n{{font-size:28px;font-weight:700}} .card .t{{font-size:12px;color:#95a5a6;margin-top:4px}}
 table{{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.06)}}
 th,td{{padding:9px 12px;text-align:left;border-bottom:1px solid #eef0f3;font-size:13px}}
 th{{background:#34495e;color:#fff;font-weight:500}}
</style></head><body><div class="wrap">
<h1>学之思在线考试系统 · API 自动化测试报告</h1>
<div class="sub">被测地址：{data['base_url']} ｜ 生成时间：{data['generated_at']}</div>
<div class="cards">
 <div class="card"><div class="n">{data['total']}</div><div class="t">用例总数</div></div>
 <div class="card"><div class="n" style="color:#27ae60">{data['passed']}</div><div class="t">通过</div></div>
 <div class="card"><div class="n" style="color:#e74c3c">{data['failed']}</div><div class="t">失败</div></div>
 <div class="card"><div class="n" style="color:#e67e22">{data.get('xfailed',0)}</div><div class="t">预期失败(缺陷)</div></div>
 <div class="card"><div class="n" style="color:#95a5a6">{data['skipped']}</div><div class="t">跳过</div></div>
 <div class="card"><div class="n">{pass_rate}%</div><div class="t">通过率</div></div>
</div>
<table><thead><tr><th>#</th><th>用例</th><th>结果</th><th>耗时</th><th>失败/说明</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
</div></body></html>"""

    out = os.path.join(REPORT_DIR, "API自动化测试报告.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("报告已生成:", out)
    return out


if __name__ == "__main__":
    args = sys.argv[1:] or []
    code = run_pytest(args)
    gen_html_report()
    sys.exit(code)
