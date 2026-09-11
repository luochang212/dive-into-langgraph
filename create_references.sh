#!/bin/bash
# 将 Jupyter notebooks 转换为 markdown 格式

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# 默认转换的笔记本文件（按顺序）
DEFAULT_NOTEBOOKS=(
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

if [ "$#" -gt 0 ]; then
    NOTEBOOKS=("$@")
else
    NOTEBOOKS=("${DEFAULT_NOTEBOOKS[@]}")
fi

PROJECT_ROOT="$SCRIPT_DIR"
OUTPUT_DIR="$PROJECT_ROOT/skills/dive-into-langgraph/references"

# 清理旧的输出（可选）
# rm -rf "$OUTPUT_DIR"/*.md "$OUTPUT_DIR"/*_files 2>/dev/null

# 转换单个 notebook 并处理图片引用
convert_notebook() {
    local nb_path="$1"
    local filename
    filename=$(basename "$nb_path" .ipynb)
    local output_file="$OUTPUT_DIR/${filename}.md"

    echo "转换: $(basename "$nb_path") -> ${filename}.md"

    # 先用默认方式转换（会生成 *_files 文件夹）
    if uv run jupyter nbconvert \
        --to markdown \
        --output-dir "$OUTPUT_DIR" \
        --output "${filename}.md" \
        "$nb_path" 2>&1; then
        echo "  ✅ 成功"
    else
        echo "  ❌ 失败"
        return 1
    fi

    # 将图片引用替换为注释（Bash 实现）
    if [ -f "$output_file" ]; then
        # 匹配 ![alt](xxx_files/image.png) 格式，替换为 <!-- IMAGE: xxx/image.png -->
        perl -pi -e 's/!\[[^]]*\]\((.+?)_files\/([^)]+)\)/<!-- IMAGE: $1\/$2 -->/g' "$output_file"
        # 只清理行尾和 EOF，不对脱离 notebook 单元格的代码块重新格式化
        perl -0777 -pi -e 's/[ \t]+$//mg; s/\n+\z/\n/' "$output_file"
    fi
}

# 主流程
main() {
    # 确保输出目录存在
    mkdir -p "$OUTPUT_DIR"

    # 转换每个 notebook
    for nb in "${NOTEBOOKS[@]}"; do
        nb_path="$PROJECT_ROOT/$nb"

        # 检查文件是否存在
        if [ ! -f "$nb_path" ]; then
            echo "⚠️  $nb 不存在，跳过"
            continue
        fi

        convert_notebook "$nb_path" || exit 1
    done

    # 删除转换时生成的 *_files 文件夹
    echo
    echo "清理 *_files 文件夹..."
    find "$OUTPUT_DIR" -maxdepth 1 -type d -name '*_files' -exec rm -rf -- {} +
    echo "  ✅ 已删除所有 *_files 文件夹"

    echo "🎉 全部完成! 输出目录: $OUTPUT_DIR"
}

main "$@"
