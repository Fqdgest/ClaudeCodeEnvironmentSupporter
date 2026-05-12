# Claude Code Environment Supporter

一键配置 Claude Code 全局开发环境 —— 在新电脑上 clone 此仓库，填写个人信息，Claude Code 自动完成全部配置。

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/Fqdgest/ClaudeCodeEnvironmentSupporter.git

# 2. 填写个人信息
cp personal_info_TEMPLATE.md personal_info.md
# 编辑 personal_info.md，填入你的 Windows 用户名等信息

# 3. 在此目录下启动 Claude Code
claude
```

Claude Code 读取 `CLAUDE.md` 后将自动按步骤完成全局环境配置。

## 前置条件

新电脑需已安装：

| 工具 | 说明 |
|------|------|
| [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code/overview) | 已通过 `claude login` 认证（或使用第三方 API） |
| [Python 3.13+](https://python.org) | 使用 `py` 启动器 |
| [Git for Windows](https://git-scm.com/download/win) | 含 Git Bash |
| [Node.js LTS](https://nodejs.org) | v18+ |

## 配置内容

本环境配置器自动安装和配置以下工具链：

### Skills（全局）
| Skill | 用途 |
|-------|------|
| `pdf` | PDF 读取/合并/拆分/旋转/水印/OCR |
| `find-skills` | 搜索 skills.sh 生态 |
| `word-docx`（可选） | Word 文档读写 |
| `pptx` | PowerPoint 创建/编辑/读取 |

### MCP 服务
| 服务 | 用途 |
|------|------|
| PDF Reader MCP | 高性能 PDF 解析 |
| Context7 MCP | 上下文感知代码搜索 |
| MATLAB MCP（可选） | 运行 MATLAB 代码 |

### 系统工具
| 工具 | 用途 |
|------|------|
| Pandoc | 文档格式转换（docx↔md↔pdf 等） |
| qpdf | PDF 命令行操作 |
| Tesseract OCR | 扫描件文字识别 |
| ImageMagick | 图像处理与转换 |
| Ghostscript | PDF 后处理 |

### Python 库
`pypdf` · `pdfplumber` · `PyMuPDF` · `pypdfium2` · `pdf2image` · `pytesseract` · `python-docx` · `python-pptx` · `Pillow` · `reportlab` · `pandas` · `openpyxl`

### Claude Code 增强
| 功能 | 说明 |
|------|------|
| **状态栏** | 实时显示模型名称、Token 用量百分比/数值、缓存命中率、Effort 级别 |
| **悬浮球** | 置顶状态指示器，颜色随 Claude Code 工作状态自动变化 |
| **Superpowers** | 6 个开发工作流 skill（头脑风暴→计划→调试→验证→TDD） |
| **权限预设** | 常用 Bash 命令自动授权，减少弹窗 |

## 目录结构

```
ClaudeCodeEnvironmentSupporter/
├── CLAUDE.md                  # 自动配置指令（Claude Code 读取此文件）
├── README.md                  # 本文件
├── personal_info_TEMPLATE.md  # 个人信息模板 → 复制为 personal_info.md
├── .gitignore                 # 排除 personal_info.md 等敏感文件
│
├── floating_ball.py           # 悬浮球主程序
├── launch_floating_ball.bat   # 悬浮球启动器（CMD）
├── launch_floating_ball.vbs   # 悬浮球启动器（静默，推荐开机自启）
├── statusline-command.py      # 状态栏显示脚本
│
├── hooks/
│   └── update_floating_ball.py  # Claude Code Hook：自动同步悬浮球状态
│
├── .claude/
│   └── settings.local.json    # 权限预设模板
│
├── .agents/skills/pptx/       # vendored pptx skill
├── create_pptx_v2.py          # PPT 生成脚本（参考模板）
└── skills-lock.json           # Skill 版本锁定
```

## 安全说明

- `personal_info.md` 已被 `.gitignore` 忽略，**不会被提交到 GitHub**
- API 密钥、用户名、路径等个人信息仅存储在本地 `personal_info.md` 中
- 推荐使用 `claude login`（官方 Anthropic API）而非手动填写 API key
- GitHub 认证推荐使用 `gh auth login --web`（OAuth），无需存储 token
- 仓库配置了分支保护：要求 PR 审查、禁止 force push、禁止删除分支

## 悬浮球

启动后屏幕右下方出现可拖拽的状态指示球：

| 状态 | 颜色 | 说明 |
|------|------|------|
| 🟢 运行中 | 绿色脉冲 | Claude Code 正在工作 |
| 🟠 等待输入 | 橙色闪烁 | 需要用户确认操作 |
| 🔵 完成 | 蓝色常亮 | 任务完成 |
| 🔴 错误 | 红色常亮 | 出现异常 |

开机自启：将 `launch_floating_ball.vbs` 复制到 `shell:startup` 目录。

## 许可证

MIT
