#!/usr/bin/env python3
"""追踪评论效果"""
import json
import subprocess
import sqlite3

conn = sqlite3.connect('reddit_posts.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS comment_results (
        id INTEGER PRIMARY KEY,
        issue_id INTEGER,
        thumbs_up INTEGER DEFAULT 0,
        replies INTEGER DEFAULT 0,
        checked_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("SELECT id, repo, issue_number, url FROM monitored_issues WHERE is_commented = 1")
commented = cursor.fetchall()

print(f"追踪 {len(commented)} 条已发布评论的效果:\n")

for issue_id, repo, num, url in commented[:5]:
    cmd = f'gh api repos/{repo}/issues/{num}/comments --jq ".[].reactions"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"{repo}#{num}")
        print(f"  反馈: {result.stdout[:100]}")

conn.close()
