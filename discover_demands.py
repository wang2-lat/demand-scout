#!/usr/bin/env python3
"""从GitHub issue中发现真实需求"""
import json
import subprocess
import sqlite3
from anthropic import Anthropic
import os

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
conn = sqlite3.connect('reddit_posts.db')
cursor = conn.cursor()

# 创建需求表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS discovered_demands (
        id INTEGER PRIMARY KEY,
        demand_title TEXT,
        demand_description TEXT,
        source_issues TEXT,
        priority_score INTEGER,
        status TEXT DEFAULT 'discovered',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
""")

# 获取所有未评论的issue
cursor.execute("SELECT repo, issue_number, title, body FROM monitored_issues WHERE is_commented = 0")
issues = cursor.fetchall()

if not issues:
    print("没有新issue，先运行 github_monitor_issues.py")
    exit(0)

# 用AI分析需求
issues_text = "\n\n".join([f"[{repo}#{num}] {title}\n{body[:200]}" for repo, num, title, body in issues[:10]])

prompt = f"""分析这些GitHub issue，找出3个最常见的痛点/需求：

{issues_text}

返回JSON格式：
[
  {{"title": "需求标题", "description": "详细描述", "priority": 1-10, "source_issues": "issue1,issue2"}}
]"""

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1000,
    messages=[{"role": "user", "content": prompt}]
)

print("发现的需求:\n")
demands = response.content[0].text
print(demands)

conn.close()
