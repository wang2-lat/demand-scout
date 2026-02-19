#!/usr/bin/env python3
"""监控目标仓库的新issue"""
import json
import subprocess
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('reddit_posts.db')
cursor = conn.cursor()

# 创建issue监控表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS monitored_issues (
        id INTEGER PRIMARY KEY,
        repo TEXT,
        issue_number INTEGER,
        title TEXT,
        body TEXT,
        url TEXT,
        created_at TEXT,
        is_commented INTEGER DEFAULT 0,
        UNIQUE(repo, issue_number)
    )
""")

# 获取目标仓库
cursor.execute("SELECT full_name FROM target_repos WHERE has_issues = 1 LIMIT 5")
repos = cursor.fetchall()

print("监控最新issue...\n")

for (repo_name,) in repos:
    cmd = f'gh issue list --repo {repo_name} --limit 5 --json number,title,body,url,createdAt'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        issues = json.loads(result.stdout)
        for issue in issues:
            cursor.execute("""
                INSERT OR IGNORE INTO monitored_issues
                (repo, issue_number, title, body, url, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (repo_name, issue['number'], issue['title'],
                  issue['body'], issue['url'], issue['createdAt']))

            if cursor.rowcount > 0:
                print(f"📌 {repo_name}#{issue['number']}: {issue['title'][:60]}")

conn.commit()

# 显示待评论的issue
cursor.execute("""
    SELECT repo, issue_number, title, url
    FROM monitored_issues
    WHERE is_commented = 0
    ORDER BY created_at DESC
    LIMIT 10
""")

issues = cursor.fetchall()
print(f"\n\n待评论的issue ({len(issues)}个):\n")
for repo, num, title, url in issues:
    print(f"{repo}#{num}: {title[:60]}")
    print(f"   {url}\n")

conn.close()
