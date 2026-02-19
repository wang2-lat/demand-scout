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

print(f"生成评论: {issue['repo']}#{issue['issue_number']}")
print(f"标题: {issue['title']}\n")

# 生成3个版本
styles = [
    "技术深度型：先提供技术见解，再自然提及项目",
    "问题解决型：直接给出解决方案，项目作为工具推荐",
    "社区贡献型：分享经验，顺带提及相关项目"
]

versions = []
for i, style in enumerate(styles, 1):
    prompt = f"""Issue: {issue['title']}
内容: {issue['body'][:400]}

我的项目: {our_project[1]}
GitHub: {our_project[2]}

用"{style}"风格生成评论。要求：
1. 先提供真实价值
2. 自然提及项目（不强推）
3. 120字内，英文
4. 不要过度热情

只返回评论内容。"""

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=250,
        messages=[{"role": "user", "content": prompt}]
    )

    comment = response.content[0].text.strip()
    versions.append((i, style.split('：')[0], comment))

    print(f"\n版本{i} - {style.split('：')[0]}")
    print("="*70)
    print(comment)
    print("="*70)

# AI评分
scoring_prompt = f"""评估这3条GitHub评论的质量（针对issue: {issue['title']}）：

版本1: {versions[0][2]}

版本2: {versions[1][2]}

版本3: {versions[2][2]}

评分标准（1-10分）：
- 提供真实价值（不是空话）
- 自然度（不像广告）
- 相关性（切题）
- 被接受概率

返回JSON: {{"best": 1-3, "scores": [分数1, 分数2, 分数3], "reason": "推荐理由"}}"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=200,
    messages=[{"role": "user", "content": scoring_prompt}]
)

print(f"\n\nAI推荐:\n{response.content[0].text}")

conn.close()
