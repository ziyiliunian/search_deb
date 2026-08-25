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
│   │   └── KylinPkgTool   # 启动器脚本（放到 /usr/bin）
│   └── share/
│       ├── applications/
│       │   └── KylinPkgTool.desktop       # 桌面快捷方式
│       ├── doc/kylinpkgtool/
│       │   └── copyright                  # 版权信息（changelog.gz 由 build.sh 生成）
│       └── icons/hicolor/256x256/apps/
│           └── KylinPkgTool.png           # 应用图标
└── README.md          # 本文件
```

> 注意：deb 内部 `Package` 字段按 Debian 规范使用小写 `kylinpkgtool`（dpkg 不允许大写包名），
> 而安装后的可执行文件、桌面项、图标与 deb 文件名均为 `KylinPkgTool`。
> 程序源码在打包时由根目录 `build.sh` 自动复制到 `opt/search_deb/`，安装后位于 `/opt/search_deb`。

## 依赖

* `python3` (>= 3.8)
* `python3-pyqt5`（PyQt5 图形界面）

## 构建 deb 包

直接运行根目录的 `build.sh` 一键完成（复制源码、生成图标与 changelog、构建）：

```bash
./build.sh 1.2
```

## 安装与卸载

```bash
sudo dpkg -i dist/KylinPkgTool_1.2_all.deb
sudo apt-get install -f   # 若依赖未满足，自动修复

# 卸载（注意使用 dpkg 内部小写包名）
sudo dpkg -r kylinpkgtool
```
