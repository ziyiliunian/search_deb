# kylinpkgtool - 银河麒麟桌面多架构包下载工具

基于 PyQt5 的图形化工具，在银河麒麟 V10 系统上按目标架构与产线版本切换软件源，查询可用版本并下载 `.deb` 软件包；支持按文件名 / 库名反查所属软件包。

## 功能特性

### 灵活的架构与版本

- 支持 `amd64`、`arm64`、`loongarch64` 三种标准架构，以及 `wayland / 华为`（ARM 特殊架构，独立一类）
- 一键通过 `dpkg --add-architecture` 启用目标架构
- 内置 40 个产线版本，按 8 个产品线分组：XC、HWE、HWE-PP、wayland（990 / 9006c / M900 / 9000C）、华为定制；其中 wayland / 华为 归入 ARM 特殊架构
- 切换版本源后自动刷新 `apt update` 索引
- 部分版本自动写入工具专属 `/etc/apt/preferences.d/kylinpkgtool.pref` 优先级设置，不修改系统原有配置

### 查询与下载

- 通过 `apt-cache policy` 查询指定包在目标架构下的全部可用版本
- 通过 `apt download` 下载指定版本（无需 sudo）
- 下载目录默认为当前用户桌面，可手动选择

### 按文件名 / 库名搜索（新增）

- 输入 deb 解压后的文件名或库名（如 `libssl.so.3`、`libssl`），反查包含该文件的软件包
- 优先使用 `apt-file search`（精确到文件），无结果时自动回退 `apt-cache search`
- 一键把选中的候选包名带入「查询版本」流程

### 源管理与日志

- 实时展示命令执行日志
- 一键恢复系统默认源（同时清理优先级文件）

## 使用方法

### 安装 deb 包

```bash
sudo dpkg -i kylinpkgtool_1.2_all.deb
# 若提示依赖未满足，执行：
sudo apt-get install -f
```

安装后在应用菜单搜索 "KylinPkgTool" 或 "银河麒麟" 即可启动，或在终端运行 `kylinpkgtool`。

### 从源码运行

```bash
pip install PyQt5
python3 -m src.main
```

### 使用步骤

1. 选择目标架构（amd64 / arm64 / loongarch64）
2. 选择产品线与系统版本（HWE/HWE-PP 仅 amd64；wayland/华为 仅 ARM 特殊架构）
3. 点击「启用目标架构」，输入管理员密码
4. 点击「启用目标版本源」，只需输入一次管理员密码；工具会在同一授权会话中迁移配置、写入源和优先级并刷新索引
5. 输入软件包名称，点击「查询版本」，选择版本后可下载选中版本或递归依赖；下载期间可点击目录后的「终止下载」强制停止整个下载进程树

### 按文件名 / 库名搜索

1. 在搜索框输入文件名或库名（如 `libssl.so.3`）
2. 点击「搜索」，从候选包中选择一个
3. 点击「使用选中包查询版本」，自动带入包名并查询、下载

> 提示：`apt-file` 需先执行 `sudo apt-file update` 建立文件索引；未安装时可执行 `sudo apt-get install apt-file`。

## 操作对照

| 操作 | 对应命令 |
|---|---|
| 启用目标架构 | `dpkg --add-architecture <arch>`（需 sudo） |
| 启用选中版本源 | 写入 sources.list 与 preferences 文件并 `apt update`（需 sudo） |
| 查询版本 | `apt-cache policy <pkg>:<arch>` |
| 下载选中版本 | `apt download <pkg>:<arch>=<version>` |
| 文件/库名搜索 | `apt-file search <kw>`（回退 `apt-cache search <kw>`） |
| 恢复默认源 | 删除工具生成的源与优先级文件并刷新索引 |
| 清空 | 清空日志、版本与搜索结果 |

## 项目结构

```
search_deb/
├── src/                        # 源代码
│   ├── __init__.py             # 包元信息（应用名、版本）
│   ├── main.py                 # 主入口（QApplication）
│   ├── main_window.py          # 主窗口 GUI（PyQt5）
│   ├── data_models.py          # 软件源数据（由 Excel 生成）+ 查询辅助
│   ├── apt_core.py             # 核心模块（命令构建 + 结果解析）
│   ├── runner.py               # 异步命令执行（QThread）
│   └── utils.py                # 通用工具（桌面路径等）
├── tools/
│   ├── gen_icon.py             # 多尺寸图标生成脚本（纯标准库）
│   └── excel_to_data_models.py # 从 Excel 生成软件源数据模型
├── packaging/                  # deb 打包配置文件
│   ├── DEBIAN/                 # control / postinst / postrm
│   └── usr/                    # 启动器、desktop、图标
├── build.sh                    # deb 打包脚本
├── pack.py                     # 快速打包脚本（跨平台）
├── requirements.txt            # 依赖（PyQt5）
├── .gitignore
└── README.md                   # 本文件
```

## 数据来源

软件源数据来自「主线版本对应源地址.xlsx」的「外网源」工作表。更新 Excel 后运行：

```bash
python3 tools/excel_to_data_models.py
```

脚本会重新生成 `src/data_models.py`。详细规则见 [`docs/excel-processing.md`](docs/excel-processing.md)。

## 打包为 deb

快速打包（跨平台）：

```bash
python pack.py            # 生成源码压缩包；Linux 上同时构建 deb
```

或使用完整构建脚本：

```bash
./build.sh 1.6
sudo dpkg -i dist/kylinpkgtool_1.6_all.deb
```

程序默认安装到 `/opt/kylinpkgtool`，启动器为 `/usr/bin/kylinpkgtool`。

## 技术栈

- Python 3.8+
- PyQt5（GUI）
- 系统命令 `apt` / `dpkg` / `apt-file`（软件包操作与文件搜索）
- `pkexec`（提权）
- `dpkg-deb`（deb 打包）

## 联系方式

如有问题或建议，欢迎联系作者沟通：

- 邮箱：316878142@qq.com
