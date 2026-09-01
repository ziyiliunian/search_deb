# KylinPkgTool Debian 打包说明

本目录存放打包 `.deb` 安装包所需的配置文件与骨架。

## 目录结构

```
packaging/
├── DEBIAN/
│   ├── control        # 包元信息（名称、版本、依赖、架构等）
│   ├── postinst       # 安装后脚本（编译字节码、刷新桌面缓存）
│   └── postrm         # 卸载后脚本（清理桌面缓存）
├── usr/
│   ├── bin/
│   │   └── kylinpkgtool   # 启动器脚本（放到 /usr/bin）
│   └── share/
│       ├── applications/
│       │   └── kylinpkgtool.desktop       # 桌面快捷方式
│       ├── doc/kylinpkgtool/
│       │   ├── copyright                  # 版权信息
│       │   ├── CHANGELOG.md                # 完整版本变更记录
│       │   └── changelog.gz                # Debian 变更记录（由 build.sh 生成）
│       └── icons/hicolor/256x256/apps/
│           └── kylinpkgtool.png           # 应用图标
└── README.md          # 本文件
```

> 注意：deb 内部 `Package` 字段与可执行文件、桌面项、图标、deb 文件名统一为小写 `kylinpkgtool`。
> 程序源码在打包时由根目录 `build.sh` 自动复制到 `opt/kylinpkgtool/`，安装后位于 `/opt/kylinpkgtool`。

## 依赖

* `python3` (>= 3.8)
* `python3-pyqt5`（PyQt5 图形界面）

## 构建 deb 包

直接运行根目录的 `build.sh` 一键完成（复制源码、生成图标与 changelog、构建）：

```bash
./build.sh 1.6.2
```

## 安装与卸载

```bash
sudo dpkg -i dist/kylinpkgtool_1.6.2_all.deb
sudo apt-get install -f   # 若依赖未满足，自动修复

# 卸载（注意使用 dpkg 内部小写包名）
sudo dpkg -r kylinpkgtool
```

应用名称：银河麒麟桌面多架构包下载工具

工具运行期间只维护 `/etc/apt/sources.list.d/kylinpkgtool.list`、`/etc/apt/preferences.d/kylinpkgtool.pref` 及 `/var/lib/kylinpkgtool` 状态目录；恢复默认源时会还原首次操作前的配置，不覆盖系统其他源和优先级文件。
