#!/usr/bin/env python3
"""查找目标GitHub仓库"""
import json
import subprocess
import sqlite3

conn = sqlite3.connect('reddit_posts.db')
cursor = conn.cursor()

# 创建目标仓库表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS target_repos (
        id INTEGER PRIMARY KEY,
        full_name TEXT UNIQUE,
        description TEXT,
        stars INTEGER,
        url TEXT,
        has_issues INTEGER,
        created_at TEXT
    )
""")

# 搜索关键词列表
keywords = [
    "saas boilerplate",
    "saas starter",
    "mvp validation",
    "indie hacker tools"
]

for keyword in keywords:
    cmd = f'gh search repos "{keyword}" --sort stars --limit 10 --json fullName,description,stargazersCount,url,hasIssues'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        repos = json.loads(result.stdout)
        for repo in repos:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO target_repos
                    (full_name, description, stars, url, has_issues, created_at)
                    VALUES (?, ?, ?, ?, ?, datetime('now'))
                """, (repo['fullName'], repo['description'],
                      repo['stargazersCount'], repo['url'], repo['hasIssues']))
            except:
                pass

conn.commit()

# 显示结果
cursor.execute("SELECT * FROM target_repos ORDER BY stars DESC")
repos = cursor.fetchall()

print(f"\n找到 {len(repos)} 个目标仓库:\n")
for repo in repos[:10]:
    print(f"⭐ {repo[3]:5d} - {repo[1]}")
    print(f"   {repo[4][:80]}")
    print()

conn.close()
