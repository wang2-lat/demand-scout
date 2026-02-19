#!/usr/bin/env python3
"""智能评论生成 - 多版本 + 质量评分"""
import os
import sqlite3
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
conn = sqlite3.connect('reddit_posts.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT * FROM ai_projects WHERE promotion_status = 'ready' LIMIT 1")
our_project = cursor.fetchone()

cursor.execute("SELECT * FROM monitored_issues WHERE is_commented = 0 ORDER BY created_at DESC LIMIT 1")
issue = cursor.fetchone()

if not issue or not our_project:
    print("没有待处理的issue")
    exit(0)

# 获取issue完整内容
import subprocess
result = subprocess.run(
    f'gh issue view {issue["issue_number"]} --repo {issue["repo"]} --json body --jq .body',
    shell=True, capture_output=True, text=True
)
full_body = result.stdout.strip() if result.returncode == 0 else issue['body']

# 跳过空内容的issue
if not full_body or len(full_body) < 50:
    print(f"跳过空内容issue: {issue['repo']}#{issue['issue_number']}")
    cursor.execute("UPDATE monitored_issues SET is_commented = 1 WHERE issue_number = ? AND repo = ?",
                   (issue['issue_number'], issue['repo']))
    conn.commit()
    conn.close()
    exit(0)

print(f"生成评论: {issue['repo']}#{issue['issue_number']}")
print(f"标题: {issue['title']}\n")

# 生成3个版本
styles = [
    "补充作者未提及的边界情况或生产环境经验",
    "提供替代方案或权衡分析",
    "分享相关工具或最佳实践"
]

versions = []
for i, style in enumerate(styles, 1):
    prompt = f"""Issue: {issue['title']}
完整内容: {full_body[:1000]}

作者已经提供了详细的解决方案。你的评论应该提供**额外价值**，不要重复作者的方案。

用"{style}"风格生成评论。要求：
1. 提供作者未提及的见解
2. 如果提及工具，必须自然且有价值
3. 100字内，英文
4. 不要过度热情

只返回评论内容。"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    comment = response.content[0].text.strip()
    versions.append((i, style, comment))

    print(f"\n版本{i} - {style}")
    print("="*70)
    print(comment)
    print("="*70)

# AI评分
scoring_prompt = f"""评估这3条评论的质量（针对已有详细解决方案的issue）：

版本1: {versions[0][2]}

版本2: {versions[1][2]}

版本3: {versions[2][2]}

评分标准（1-10分）：
- 提供新价值（不重复作者）
- 自然度（不像广告）
- 实用性
- 被接受概率

返回JSON: {{"best": 1-3, "scores": [分数1, 分数2, 分数3], "reason": "推荐理由"}}"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=200,
    messages=[{"role": "user", "content": scoring_prompt}]
)

print(f"\n\nAI推荐:\n{response.content[0].text}")

# 生成发布命令
best = int(response.content[0].text.split('"best": ')[1].split(',')[0])
best_comment = versions[best-1][2]

print(f"\n\n发布命令:")
print(f"gh issue comment {issue['issue_number']} --repo {issue['repo']} --body '{best_comment}'")

conn.close()
