#!/usr/bin/env python3
"""对比竞品的自动化推广策略"""
import subprocess
import json

competitors = [
    "vercel/next.js",
    "supabase/supabase",
    "trpc/trpc"
]

print("分析竞品的推广策略:\n")

for repo in competitors:
    # 查看他们在哪些issue下评论
    cmd = f'gh search issues "commenter:owner({repo.split("/")[0]})" --limit 5 --json title,url,repository'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        data = json.loads(result.stdout)
        print(f"\n{repo} 的推广策略:")
        print(f"  活跃度: {len(data)} 条评论")
        if data:
            print(f"  目标仓库: {data[0]['repository']['nameWithOwner']}")
