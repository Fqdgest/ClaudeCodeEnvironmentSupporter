# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 本工作区的用途

这是一个 **Claude Code 全局环境配置器**。当你在新电脑上安装好 Claude Code 后，将此工作区作为起始目录打开，Claude Code 读取本文档后将按照以下步骤逐项配置全局环境，使新电脑具备完整的开发能力。

**前置条件**：新电脑已安装 Claude Code CLI、Python（`py` 启动器）、Git、Node.js。

### ⚠️ 给新电脑上 Claude Code 实例的行动指令

**收到此文档后，不要只是阅读——请按顺序执行每个步骤中的命令，逐一完成全局环境配置。** 每完成一步，运行该步骤提供的验证命令确认配置生效。如遇到下载/安装类操作需要用户手动确认，提示用户操作后继续下一步。

---

## 第0步：读取个人信息配置

本工作区根目录下有一个 `personal_info.md` 文件（由 `personal_info_TEMPLATE.md` 复制而来），包含本机用户的个人信息。

**立即执行**：读取 `personal_info.md`，提取其中所有 `KEY: value` 格式的字段值。这些值将在后续所有步骤中使用：

| 字段 | 用途 | 必填 |
|------|------|------|
| `WINDOWS_USERNAME` | 构造绝对路径（Hook 命令等） | ✅ |
| `MATLAB_INSTALL_DIR` | MATLAB MCP 注册路径 | 可选 |
| `GIT_INSTALL_DIR` | Git 工具链路径（pdftotext 等） | 可选 |
| `API_BASE_URL` | 第三方 API 地址 | 可选 |
| `API_KEY` | API 密钥 | 可选 |
| `DEFAULT_MODEL` | 默认模型名称 | 可选 |
| `PROXY_HOST` / `PROXY_PORT` | HTTP 代理设置 | 可选 |
| `EXTRA_DISKS` | 需授予 Read 权限的盘符 | 可选 |

> **安全提示**：`personal_info.md` 已被 `.gitignore` 忽略，不会被提交到 GitHub。请勿将其内容写入任何其他文件。

---

## 第1步：Claude Code 全局设置

将以下配置写入 `~/.claude/settings.json`（与已有内容合并，不要覆盖其他字段）：

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1",
    "ENABLE_TOOL_SEARCH": "true"
  },
  "includeCoAuthoredBy": false,
  "theme": "light-daltonized"
}
```

执行方式：用 `claude config set` 逐项设置，或直接用 Edit 工具写入 `~/.claude/settings.json`。

### 1.1 API 提供商配置（条件执行）

检查 `personal_info.md` 中的 `API_KEY` 字段：

- **如果 `API_KEY` 为空或未填写**：跳过本节。用户已通过 `claude login` 使用官方 Anthropic API。
- **如果 `API_KEY` 有值**：将以下 env 字段合并到 `~/.claude/settings.json` 的 `"env"` 块中：

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "{{API_BASE_URL}}",
    "ANTHROPIC_AUTH_TOKEN": "{{API_KEY}}",
    "ANTHROPIC_MODEL": "{{DEFAULT_MODEL}}",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "{{DEFAULT_MODEL}}",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "{{DEFAULT_MODEL}}",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "{{DEFAULT_MODEL}}"
  }
}
```

将 `{{API_BASE_URL}}`、`{{API_KEY}}`、`{{DEFAULT_MODEL}}` 替换为 `personal_info.md` 中的实际值。

> 如果使用代理，还需在 `"env"` 中添加 `HTTP_PROXY` 和 `HTTPS_PROXY`（格式 `http://{{PROXY_HOST}}:{{PROXY_PORT}}`）。仅当 `PROXY_HOST` 非空时添加。

### 1.2 常用全局权限

以下权限配置写入 `~/.claude/settings.local.json`，允许 Claude Code 在执行日常操作时减少重复的权限弹窗：

```json
{
  "permissions": {
    "allow": [
      "Bash(where *)",
      "Bash(py *)",
      "Bash(python *)",
      "Bash(python3 *)",
      "Bash(pip *)",
      "Bash(npm *)",
      "Bash(npx *)",
      "Bash(node *)",
      "Bash(pandoc *)",
      "Bash(pdftotext *)",
      "Bash(pdfinfo *)",
      "Bash(qpdf *)",
      "Bash(curl *)",
      "Bash(winget *)",
      "Bash(echo *)",
      "WebSearch",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:modelscope.cn)",
      "Skill(update-config)"
    ]
  }
}
```

**额外磁盘权限**：检查 `personal_info.md` 中的 `EXTRA_DISKS`。如果非空，对该字段中列出的每个盘符，在权限列表中添加 `"Read(//<盘符>/**)"` 条目。例如 `EXTRA_DISKS: c,d` 则添加：

```json
"Read(//c/**)",
"Read(//d/**)"
```

> 如果你还有项目文件在其他盘符上，也一并添加对应的 Read 权限。

---

## 第2步：安装全局 Skills

Skills 安装到 `~/.claude/skills/`（全局作用域）。

### 2.1 PDF 处理（`pdf`）

```bash
npx skills add pdf -y --scope global
```

此 skill 提供 pypdf / pdfplumber / reportlab / pdftotext / qpdf 等工具的完整使用指南。**任何涉及 PDF 的操作（读取、合并、拆分、旋转、水印、表单填写、OCR）都应先调用此 skill。**

> 注：`pdf` skill 通常已内置在 Claude Code 中。如果 `npx skills add pdf` 找不到，说明已经可用，跳过此步骤。

### 2.2 技能发现（`find-skills`）

```bash
npx skills add find-skills -y --scope global
```

提供 `find-skills` skill，用于搜索 skills.sh 生态中的其他 skills（如 `vercel-labs/agent-skills`、`anthropics/skills` 等）。

> 注：`find-skills` skill 通常已内置。如果已存在则跳过。

### 2.3 Word 文档处理（`word-docx`，可选）

如果项目涉及 .docx 文件的读取或生成：

```bash
npx skills add word-docx -y --scope global
```

> 也可从 modelscope 安装：`npx skills add https://modelscope.cn/skills/@leoyeai/word-docx -y`

### 2.4 PPT 创建（`pptx`，官方）

创建、编辑和读取 .pptx 文件。**任何涉及幻灯片、演示文稿、PPT 的任务都应先调用此 skill。**

```bash
npx skills add anthropics/skills@pptx -y --scope global
```

此 skill 依赖以下工具：

```bash
npm install -g pptxgenjs                    # 从零创建 PPTX
pip install "markitdown[pptx]" Pillow       # 内容提取 + 缩略图
```

> 额外依赖：LibreOffice (`soffice`) 用于 PPTX→PDF 转换、Poppler (`pdftoppm`) 用于 PDF→图片（QA 视觉审查用）。

三种工作模式：
- **从零创建**：内容驱动，无模板 → 用 pptxgenjs
- **模板编辑**：有现成公司模板 → python-pptx + XML 操作
- **读取分析**：已有 PPTX 提取文字 → markitdown

---

## 第3步：系统依赖安装

以下工具需要在新电脑上手动安装（按优先级排序）。

### 3.1 Python 环境

Windows 上推荐从 Microsoft Store 安装 Python 3.13+，或从 [python.org](https://python.org) 下载。安装后使用 `py` 启动器。

安装必需的 Python 包：

```bash
py -m pip install --upgrade pip
py -m pip install pypdf pdfplumber PyMuPDF pypdfium2 pdf2image pytesseract python-docx python-pptx Pillow reportlab pandas openpyxl
```

各包用途：

| 包 | 用途 |
|----|------|
| `pypdf` | PDF 合并/拆分/旋转/元数据/加密 |
| `pdfplumber` | PDF 文本和表格提取（保留布局） |
| `PyMuPDF` (fitz) | 高性能 PDF 文本提取和渲染 |
| `pypdfium2` | 可选，PDF 渲染的备选方案 |
| `pdf2image` | PDF 页面转图片（OCR 前置步骤） |
| `pytesseract` | OCR 文字识别（需安装 Tesseract 本体） |
| `python-docx` | Word .docx 文件文本提取 |
| `python-pptx` | PowerPoint .pptx 文件创建与编辑 |
| `Pillow` | 图像处理（PPTX 缩略图、公式渲染） |
| `reportlab` | 编程创建 PDF |
| `pandas` / `openpyxl` | 数据处理和 Excel 导出 |

> 如果配置了代理（`PROXY_HOST` 非空），pip 命令需加 `--proxy http://{{PROXY_HOST}}:{{PROXY_PORT}}`。

### 3.2 Node.js

从 [nodejs.org](https://nodejs.org) 安装 LTS 版本（当前参考：v18+）。安装后自带 npm 和 npx。

验证安装：
```bash
node --version
npm --version
```

### 3.3 Pandoc（文档格式转换）

从 [pandoc.org](https://pandoc.org/installing.html) 下载 Windows 安装包。

验证安装：
```bash
pandoc --version
```

常用用途：将 Word .docx 转换为 Markdown（含公式保留）：
```bash
pandoc input.docx --from docx --to markdown --wrap=none -o output.md
```

### 3.4 Git for Windows（含 PDF 工具链）

从 [git-scm.com](https://git-scm.com/download/win) 安装。安装后 `pdftotext`、`pdfinfo`、`curl` 等工具会出现在 Git Bash 的 `/mingw64/bin/` 中。

验证安装：
```bash
git --version
pdftotext -v
```

### 3.5 qpdf（PDF 命令行工具）

从 [qpdf.readthedocs.io](https://qpdf.readthedocs.io/) 下载 Windows 安装包，或通过 winget：

```bash
winget install qpdf
```

提供 PDF 合并/拆分/旋转/解密等命令行操作。

### 3.6 Tesseract OCR（可选，扫描件识别）

从 [GitHub UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki) 下载 Windows 安装包。

验证安装：
```bash
tesseract --version
```

如需中文 OCR：
```bash
curl -L -o "C:\Program Files\Tesseract-OCR\tessdata\chi_sim.traineddata" "https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata"
```

### 3.7 ImageMagick（可选，PDF ↔ 图像转换）

从 [imagemagick.org](https://imagemagick.org/script/download.php) 下载 Windows 安装包。

验证安装：
```bash
magick --version
```

### 3.8 Ghostscript（可选，PDF 后处理）

从 [ghostscript.com](https://ghostscript.com/releases/gsdnld.html) 下载 Windows AGPL 版本。

验证安装：
```bash
gswin64c --version
```

---

## 第4步：MATLAB MCP Server

如果需要在 Claude Code 中运行 MATLAB 代码，配置 MATLAB MCP Server。

### 4.1 前提

检查 `personal_info.md` 中 `MATLAB_INSTALL_DIR` 是否已填写。如果为空，跳过整个第4步。

本机需安装 MATLAB R2024b 或更高版本，MCP server 可执行文件位于 MATLAB 安装目录的 `bin/` 下。

### 4.2 全局注册 MCP Server

```bash
claude mcp add matlab -- "{{MATLAB_INSTALL_DIR}}\bin\matlab-mcp-core-server-win64.exe" --matlab-display-mode=desktop
```

将 `{{MATLAB_INSTALL_DIR}}` 替换为 `personal_info.md` 中的实际路径。

### 4.3 首次配置

```bash
"{{MATLAB_INSTALL_DIR}}\bin\matlab-mcp-core-server-win64.exe" --setup-matlab
```

如果 MATLAB 无法连接，在 MATLAB 命令窗口中运行：
```matlab
enableservice('CommunicationService', true);
enableservice('AutomationServer', true);
```

### 4.4 授予权限

在 `~/.claude/settings.local.json` 中添加 MCP 相关权限。从 `MATLAB_INSTALL_DIR` 提取盘符（如 `D:` → `d`），然后添加：

```json
{
  "permissions": {
    "allow": [
      "mcp__matlab__run_matlab_file",
      "mcp__matlab__evaluate_matlab_code",
      "mcp__matlab__check_matlab_code",
      "Bash(matlab *)",
      "Bash(where matlab *)",
      "Read(//{{MATLAB_DRIVE}}/MATLAB/**)",
      "Read(//{{MATLAB_DRIVE}}/MATLAB/bin/**)",
      "Read(//{{MATLAB_DRIVE}}/MATLAB/bin/win64/**)"
    ]
  }
}
```

将 `{{MATLAB_DRIVE}}` 替换为 MATLAB 安装盘符（小写）。

---

## 第5步：Superpowers 插件

Superpowers 是一个开发工作流插件，包含 6 个 skills：`brainstorming`、`writing-plans`、`dispatching-parallel-agents`、`systematic-debugging`、`verification-before-completion`、`test-driven-development`。

### 5.1 添加 marketplace

```bash
/plugin marketplace add obra/superpowers-marketplace
```

### 5.2 安装插件（全局）

```bash
/plugin install superpowers@superpowers-marketplace
```

安装后可通过 `superpowers:brainstorming`、`superpowers:writing-plans` 等形式调用各个 skill。

---

## 第6步：MCP 服务

MCP（Model Context Protocol）服务扩展 Claude Code 与外部工具的交互能力。以下 MCP 服务配置为全局作用域（`--scope user`）。

### 6.1 PDF Reader MCP（`@sylphx/pdf-reader-mcp`）

提供高性能 PDF 读取和解析能力。

安装（npm 全局）：

```bash
npm install -g @sylphx/pdf-reader-mcp
```

注册 MCP：

```bash
claude mcp add pdf-reader --scope user -- npx @sylphx/pdf-reader-mcp
```

> **本地构建（开发用）**：如果需要从源码构建：
> ```bash
> git clone https://github.com/sylphlab/pdf-reader-mcp.git
> cd pdf-reader-mcp && pnpm install && pnpm run build
> ```
> 构建后手动配置 `~/.claude/settings.json` 中的 `mcpServers`：
> ```json
> {
>   "mcpServers": {
>     "pdf-reader-mcp": {
>       "command": "node",
>       "args": ["/path/to/pdf-reader-mcp/build/index.js"],
>       "name": "PDF Reader (Local Build)"
>     }
>   }
> }
> ```

### 6.2 Context7 MCP（`@upstash/context7-mcp`）

提供上下文感知的代码搜索和理解能力。

安装和注册一步完成：

```bash
claude mcp add context7 --scope user -- npx @upstash/context7-mcp
```

---

## 第7步：状态栏配置（Token 用量显示）

配置 Claude Code 状态栏，实时显示模型上下文使用百分比、具体数值、模型名称、缓存命中率和 Effort 级别。

### 7.1 复制状态栏脚本

将工作区中的 `statusline-command.py` 复制到 `~/.claude/` 目录：

```bash
cp statusline-command.py ~/.claude/
```

### 7.2 注册状态栏

使用 `personal_info.md` 中的 `WINDOWS_USERNAME` 构造命令路径，将以下配置写入 `~/.claude/settings.json`：

```json
{
  "statusLine": {
    "type": "command",
    "command": "py C:/Users/{{WINDOWS_USERNAME}}/.claude/statusline-command.py"
  }
}
```

将 `{{WINDOWS_USERNAME}}` 替换为实际值。**路径必须使用绝对路径**（Windows 不支持 `~` 展开）。

> 也可通过 `/statusline` 交互式界面手动配置。

---

## 第8步：悬浮球状态指示器

一个悬浮于所有窗口之上的状态球，自动跟随 Claude Code 工作状态变色：
- 🟢 **绿色脉冲** = 运行中
- 🟠 **橙色闪烁** = 等待你的操作（工具需要权限确认）
- 🔵 **蓝色常亮** = 任务完成
- 🔴 **红色常亮** = 错误

支持鼠标拖拽移动，位置自动保存，输入 `/exit` 退出 Claude Code 时自动关闭。

### 8.1 复制悬浮球脚本

将工作区中的以下文件复制到 `~/.claude/` 目录：

```bash
cp floating_ball.py ~/.claude/
cp launch_floating_ball.bat ~/.claude/
cp launch_floating_ball.vbs ~/.claude/
```

### 8.2 复制 Hook 脚本

```bash
mkdir -p ~/.claude/hooks
cp hooks/update_floating_ball.py ~/.claude/hooks/
```

### 8.3 注册 Hooks

使用 `personal_info.md` 中的 `WINDOWS_USERNAME` 构造命令路径（Windows 不支持 `~` 展开，必须用绝对路径）。将以下 JSON 合并到 `~/.claude/settings.json` 中：

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "py C:/Users/{{WINDOWS_USERNAME}}/.claude/hooks/update_floating_ball.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "py C:/Users/{{WINDOWS_USERNAME}}/.claude/hooks/update_floating_ball.py",
            "timeout": 10
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "py C:/Users/{{WINDOWS_USERNAME}}/.claude/hooks/update_floating_ball.py",
            "timeout": 10
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "py C:/Users/{{WINDOWS_USERNAME}}/.claude/hooks/update_floating_ball.py",
            "timeout": 10
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "py C:/Users/{{WINDOWS_USERNAME}}/.claude/hooks/update_floating_ball.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

**关键**：将 `{{WINDOWS_USERNAME}}` 替换为 `personal_info.md` 中的实际值后再写入。

### 8.4 启动悬浮球

```bash
# 双击 launch_floating_ball.vbs（静默启动，推荐）
# 或双击 launch_floating_ball.bat

# 命令行方式：
pyw ~/.claude/floating_ball.py
```

开机自启：将 `launch_floating_ball.vbs` 复制到 `shell:startup` 目录。

### 8.5 验证

1. 启动悬浮球，应看到右下方的绿色脉冲球体
2. 鼠标左键拖拽可移动位置
3. 右键点击可手动切换状态
4. 发送一条消息后，悬浮球应在 Claude Code 执行工具时变为橙色，完成后恢复绿色
5. 输入 `/exit` 退出时，悬浮球应在 1 秒内自动关闭

---

## 第9步：验证清单

配置完成后，逐项验证：

| 检查项 | 验证命令 |
|--------|----------|
| Python 包 | `py -c "import pypdf, pdfplumber, fitz, docx, pptx, PIL; print('OK')"` |
| Pandoc | `pandoc --version` |
| pdftotext | `pdftotext -v` |
| qpdf | `qpdf --version` |
| Node.js | `node --version && npm --version` |
| Git | `git --version` |
| Superpowers 插件 | `/plugin list` 应显示 superpowers |
| MATLAB MCP | `claude mcp list` 应显示 matlab（如已配置） |
| PDF Reader MCP | `claude mcp list` 应显示 pdf-reader |
| Context7 MCP | `claude mcp list` 应显示 context7 |
| 全局 skills | `ls ~/.claude/skills/` 应显示 pdf 和 find-skills |
| 状态栏 | 观察 Claude Code 界面底部状态栏是否显示 token 用量、模型名称、缓存命中率、Effort |
| 悬浮球 | 双击 `~/.claude/launch_floating_ball.vbs`，确认悬浮球出现；发送消息后确认颜色随状态变化 |

---

## 附录A：Word → PPT 工作流

将 .docx 技术文档转换为专业 .pptx 演示文稿的完整方案。

### A.1 技术选型

经过多方案对比验证，最终选择 **python-pptx** 作为生成引擎：

| 方案 | 结果 | 原因 |
|------|------|------|
| pptxgenjs (Node.js) | ❌ 弃用 | 不支持 LaTeX 公式、排版控制弱、中文支持差 |
| HTML→PPT (html2pptx) | ❌ 未采用 | 依赖 LibreOffice 转换，格式不可控 |
| **python-pptx** | ✅ 采用 | 原生 PPTX 操作、精确排版控制、python-docx 同生态无缝衔接 |

### A.2 工作流概览

```
Word (.docx) ──→ 提取内容+结构 ──→ 规划幻灯片 ──→ python-pptx生成 ──→ 手动QA
  python-docx     段落/表格/公式      大纲设计        排版+公式          PPT中转换公式
```

### A.3 依赖清单

```bash
# Python 库（已包含在第3步安装命令中）
py -m pip install python-docx python-pptx Pillow

# PPT 创建 skill（已包含在第2.4步）
npx skills add anthropics/skills@pptx -y --scope global

# 可选：视觉QA
# LibreOffice (soffice) — PPTX→PDF转换
# Poppler (pdftoppm)   — PDF→幻灯片图片
```

### A.4 生成脚本架构

参考本目录下的 `create_pptx_v2.py`，核心结构如下：

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width  = Inches(10)     # 16:9
prs.slide_height = Inches(5.625)

# —— 辅助函数 ——
def add_blank_slide(bg_color): ...          # 空白页
def add_left_accent_bar(slide, color): ...   # 左侧装饰竖条
def add_title(slide, text): ...              # 左上标题 + 下划线
def add_left_text(slide, bullets): ...       # 左列正文（bold标签 + 说明 + 子要点）
def add_right_diagram_area(slide): ...       # 右列图表区（上下两个占位框）
def add_formula_box(slide, latex): ...       # 底部LaTeX公式框
def make_content_slide(title, bullets, formulas): ...  # 标准内容页
def make_section_slide(num, title, sub): ...  # 深色章节分隔页
```

### A.5 排版规范

| 要素 | 规格 |
|------|------|
| 页面尺寸 | 10″ × 5.625″ (16:9) |
| 配色 | 深海军蓝 `#1B2A4A` + 青绿 `#0891B2` + 珊瑚红 `#F96167` |
| 标题 | 左上角，26pt 微软雅黑 Bold，下配青绿短横线 |
| 正文 | 左列 5.2″ 宽，12pt Bold 标签 + 11pt 说明 |
| 图表区 | 右列 3.6″ 宽浅灰底，上下两个白色占位框 |
| 公式 | 底部 Consolas 9pt 斜体，前配珊瑚红短横线 |
| 章节分隔 | 深色全幅，72pt 编号 + 30pt 标题 |
| 左侧装饰 | 0.1″ 宽深蓝竖条贯穿全页 |

### A.6 LaTeX 公式处理

**关键规则**：所有含 LaTeX 反斜杠命令的 Python 字符串必须使用 **raw string** (`r"..."`)，否则 `\t`→Tab、`\f`→换页、`\r`→回车等转义会导致公式损坏。

```python
# ✅ 正确：raw string
{"latex": r"K_\theta(s) = \frac{1}{2} K_{\theta 0} \cdot (1 - C_\theta \cdot |s|)"}

# ❌ 错误：普通字符串 —— \t 被解释为Tab，\f 被解释为换页
{"latex": "K_\theta(s) = \frac{1}{2} K_{\theta 0} \cdot (1 - C_\theta \cdot |s|)"}
```

**文本框内联公式**：使用 `$...$` 包裹，在 PPT 中选中后 `Alt+=` → 粘贴即可转换为可编辑数学公式。

**公式框**：底部独立公式框提供完整 LaTeX 代码，便于复制粘贴到 PPT 公式编辑器。

### A.7 生成步骤

1. **提取内容**：`python-docx` 读取 .docx，按段落样式（Heading 1/2/3、Body Text、Normal）解析结构
2. **规划大纲**：根据 Heading 层级设计幻灯片章节和页面数（技术报告建议 25-35 页）
3. **编写脚本**：参照 `create_pptx_v2.py` 模板，逐页填入内容和公式
4. **生成 PPTX**：`py create_pptx_v2.py`
5. **视觉 QA**（可选）：`soffice --headless --convert-to pdf output.pptx` → `pdftoppm -jpeg -r 150 output.pdf slide`，逐张检查排版溢出
6. **公式转换**：在 PowerPoint 中打开，选中 LaTeX 文本 → `Alt+=` → 粘贴 → 回车转换

### A.8 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 公式出现 Tab 空隙 | Python 字符串中 `\t` 被解释为 Tab | 使用 `r"..."` raw string |
| 公式出现 `_x000C_` 乱码 | `\f` 被解释为换页符 | 使用 `r"..."` raw string |
| 中文显示为方块 | 字体未安装 | 使用系统通用字体（微软雅黑/宋体） |
| 排版超出页面 | 文本框宽/高设置过大 | 控制 LEFT_COL_W ≤ 5.2″，BOTTOM_Y ≥ 5.0″ |
| 内容不够凝练 | 直接从 Word 逐段复制 | 每页提炼 4-6 个要点，每个要点 ≤120 字符 |

---

## iFLOW 生态参考

本工作区属于 iFLOW 结构抗震分析项目生态：

| 工作区 | 用途 |
|--------|------|
| `Codextest1` | 3D 基础隔震建筑非线性时程分析（串联 LRB+TLRB 支座） |
| `ClaudeCodetest1` | 隔震建模补充分析与理论文档 |

当在新电脑上配置完成后，可以将这些工作区一并迁移过来继续开发。
