#!/usr/bin/env python3
"""初始化数据库结构"""
import sqlite3

conn = sqlite3.connect('reddit_posts.db')
cursor = conn.cursor()

# Reddit帖子表
cursor.execute("""
CREATE TABLE IF NOT EXISTS reddit_posts (
    id TEXT PRIMARY KEY,
    title TEXT,
    selftext TEXT,
    score INTEGER,
    url TEXT,
    created_utc INTEGER,
    subreddit TEXT
)
""")

# AI生成项目表
cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT,
    project_name TEXT,
    github_url TEXT,
    local_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    promotion_comment TEXT,
    promotion_status TEXT DEFAULT 'pending',
    FOREIGN KEY (post_id) REFERENCES reddit_posts(id)
)
""")

conn.commit()
conn.close()
print("✅ 数据库初始化完成")
