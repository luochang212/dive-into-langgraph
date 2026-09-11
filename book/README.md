# MyST 电子书

[MyST](https://mystmd.org/) 直接使用根目录的 `myst.yml` 和 Jupyter Notebook 构建本教程。

同步仓库环境：

```bash
uv sync
```

构建 HTML 并执行 CI 校验：

```bash
npx --yes mystmd build --html --ci
```

本地预览：

```bash
npx --yes mystmd start
```

构建并预览静态页面：

```bash
npx --yes mystmd build --html

uv run python -m http.server 8000 --directory _build/html
```
