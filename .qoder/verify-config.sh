#!/bin/bash

# Lingma 配置验证脚本
# 用于检查 .qoder/ 目录下的 rules 和 agents 是否正确配置

echo "======================================"
echo "Lingma 配置验证报告"
echo "======================================"
echo ""

PROJECT_ROOT="/Users/snow-sakura/sakura/qoder_one"
QODER_DIR="$PROJECT_ROOT/.qoder"

# 检查 .qoder 目录是否存在
if [ ! -d "$QODER_DIR" ]; then
    echo "❌ .qoder 目录不存在"
    exit 1
fi

echo "✅ .qoder 目录存在"
echo ""

# 检查 agents 目录
echo "📦 智能体 (Agents):"
echo "--------------------------------------"
if [ -d "$QODER_DIR/agents" ]; then
    for file in "$QODER_DIR/agents"/*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            # 提取 name 和 description
            name=$(grep "^name:" "$file" | head -1 | sed 's/name: //')
            desc=$(grep "^description:" "$file" | head -1 | sed 's/description: //' | cut -c1-60)
            echo "  ✅ $filename"
            echo "     名称: $name"
            echo "     描述: ${desc}..."
        fi
    done
else
    echo "  ❌ agents 目录不存在"
fi
echo ""

# 检查 rules 目录
echo "📜 规则 (Rules):"
echo "--------------------------------------"
if [ -d "$QODER_DIR/rules" ]; then
    for file in "$QODER_DIR/rules"/*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            # 检查是否有 trigger
            trigger=$(grep "^trigger:" "$file" | head -1 | sed 's/trigger: //')
            if [ -n "$trigger" ]; then
                echo "  ✅ $filename (trigger: $trigger)"
            else
                echo "  ⚠️  $filename (无 trigger，可能不会自动生效)"
            fi
        fi
    done
else
    echo "  ❌ rules 目录不存在"
fi
echo ""

# 统计
agent_count=$(ls -1 "$QODER_DIR/agents"/*.md 2>/dev/null | wc -l | tr -d ' ')
rule_count=$(ls -1 "$QODER_DIR/rules"/*.md 2>/dev/null | wc -l | tr -d ' ')

echo "======================================"
echo "总计: $agent_count 个智能体, $rule_count 条规则"
echo "======================================"
echo ""

echo "💡 提示："
echo "  如果 Lingma IDE 未识别这些配置，请："
echo "  1. 关闭并重新打开项目"
echo "  2. 或完全重启 Lingma IDE"
echo "  3. 清除缓存: rm -rf ~/Library/Application\\ Support/Lingma/SharedClientCache/cli/projects/*"
