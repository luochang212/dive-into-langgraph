#!/bin/bash
# 将 Jupyter notebooks 转换为 markdown 格式

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 需要转换的笔记本文件（按顺序）
NOTEBOOKS=(
    "1.quickstart.ipynb"
    "2.stategraph.ipynb"
    "3.middleware.ipynb"
    "4.human_in_the_loop.ipynb"
    "5.memory.ipynb"
    "6.context.ipynb"
    "7.mcp_server.ipynb"
    "8.supervisor.ipynb"
    "9.parallelization.ipynb"
    "10.rag.ipynb"
    "11.web_search.ipynb"
)

PROJECT_ROOT="$SCRIPT_DIR"
OUTPUT_DIR="$PROJECT_ROOT/skills/dive-into-langgraph/references"

# 安装 mdformat（如未安装）
if ! python -c "import mdformat" 2>/dev/null; then
    echo "安装 mdformat..."
    pip install mdformat
fi

# 确保输出目录存在
mkdir -p "$OUTPUT_DIR"

# 转换每个 notebook
for nb in "${NOTEBOOKS[@]}"; do
    nb_path="$PROJECT_ROOT/$nb"
    filename=$(basename "$nb" .ipynb)

    # 检查文件是否存在
    if [ ! -f "$nb_path" ]; then
        echo "⚠️  $nb 不存在，跳过"
        continue
    fi

    output_file="$OUTPUT_DIR/${filename}.md"

    echo "转换: $(basename "$nb") -> ${filename}.md"

    if python -m jupyter nbconvert \
        --to markdown \
        --output-dir "$OUTPUT_DIR" \
        --output "${filename}.md" \
        "$nb_path" 2>&1; then
        echo "  ✅ 成功"
    else
        echo "  ❌ 失败"
        exit 1
    fi
done

echo "=================================================="
echo "格式化 markdown 文件..."

# 格式化所有生成的 markdown 文件（如有）
shopt -s nullglob
md_files=("$OUTPUT_DIR"/*.md)
shopt -u nullglob
if [ ${#md_files[@]} -gt 0 ]; then
    mdformat "${md_files[@]}"
fi

echo "🎉 全部完成! 输出目录: $OUTPUT_DIR"