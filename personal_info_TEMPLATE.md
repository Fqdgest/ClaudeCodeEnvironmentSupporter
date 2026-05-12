# 个人信息配置

将此文件复制为 `personal_info.md`（已被 .gitignore 忽略，不会被提交到 GitHub），
然后填写以下字段。Claude Code 在配置环境时会读取此文件。

---

## 必填字段

### Windows 用户名
WINDOWS_USERNAME: {{YOUR_USERNAME}}

## 可选字段

### MATLAB 安装目录（不需要 MATLAB 则留空）
MATLAB_INSTALL_DIR: {{MATLAB_DIR}}

### Git for Windows 安装目录（pdftotext/pdfinfo 等工具路径）
GIT_INSTALL_DIR: {{GIT_DIR}}

### API 提供商配置（使用官方 Anthropic API 则留空）
API_BASE_URL: {{API_BASE_URL}}
API_KEY: {{API_KEY}}
DEFAULT_MODEL: {{MODEL_NAME}}

### HTTP 代理（不需要代理则留空）
PROXY_HOST: {{PROXY_HOST}}
PROXY_PORT: {{PROXY_PORT}}

### 额外磁盘盘符（需要 Claude Code 读取的盘符，逗号分隔，如 c,d）
EXTRA_DISKS: {{DISK_LETTERS}}
