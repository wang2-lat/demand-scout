#!/usr/bin/env python3
"""自动生成并发布评论"""
import os
import sqlite3
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
conn = sqlite3.connect('reddit_posts.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 获取我们的项目
cursor.execute("SELECT * FROM ai_projects WHERE promotion_status = 'ready' LIMIT 1")
our_project = cursor.fetchone()

# 获取待评论的issue
cursor.execute("""
    SELECT * FROM monitored_issues
    WHERE is_commented = 0
    ORDER BY created_at DESC
    LIMIT 1
""")

issue = cursor.fetchone()

if not issue or not our_project:
    print("没有待处理的issue或项目")
    exit(0)

print(f"生成评论: {issue['repo']}#{issue['issue_number']}")
print(f"标题: {issue['title']}\n")

prompt = f"""有人在 {issue['repo']} 提了issue:

标题: {issue['title']}
内容: {issue['body'][:500]}

我的项目: {our_project[1]}
GitHub: {our_project[2]}
描述: {our_project[3]}

生成一个有价值的评论:
1. 先真诚回答问题或提供建议
2. 如果相关，自然提及我的项目
3. 语气友好，不要太推销

150字以内，英文。"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=300,
    messages=[{"role": "user", "content": prompt}]
)

comment = response.content[0].text

print("生成的评论:")
print("="*70)
print(comment)
print("="*70)
print(f"\n真实发布命令:")
print(f'gh issue comment {issue["issue_number"]} --repo {issue["repo"]} --body "{comment.replace(chr(34), chr(92)+chr(34))}"')
print("\n模拟发布...")
cursor.execute("""
    UPDATE monitored_issues
    SET is_commented = 1
    WHERE id = ?
""", (issue['id'],))
conn.commit()
print(f"✅ 已标记为已评论")

conn.close()
