#!/bin/bash
# 自动化工作流：发现需求 → 推广 → 联系

echo "🔍 步骤1: 查找目标仓库"
python github_find_targets.py

echo -e "\n📊 步骤2: 监控新issue"
python github_monitor_issues.py

echo -e "\n💡 步骤3: 发现需求"
python discover_demands.py

echo -e "\n✍️  步骤4: 生成评论（前3条）"
for i in {1..3}; do
    python github_auto_comment.py
    echo ""
done

echo -e "\n✅ 完成！查看生成的评论，复制gh命令发布"
