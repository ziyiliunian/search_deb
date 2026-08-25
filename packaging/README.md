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
│   │   └── kylin-pkg-tool   # 启动器脚本（放到 /usr/bin）
│   └── share/
│       ├── applications/
│       │   └── kylin-pkg-tool.desktop       # 桌面快捷方式
│       └── icons/hicolor/256x256/apps/
│           └── kylin-pkg-tool.png           # 应用图标
└── README.md          # 本文件
```

> 注意：`packaging/opt/kylin-pkg-tool/` 目录下的 Python 源码由根目录 `build.sh`
> 在打包时自动复制生成，不需手工维护。程序安装后位于 `/opt/kylin-pkg-tool`。

## 依赖

* `python3` (>= 3.8)
* `python3-pyqt5`（PyQt5 图形界面）

## 手动构建 deb 包

```bash
# 1. 复制源码到打包目录
mkdir -p packaging/opt/kylin-pkg-tool/src
cp -r src/* packaging/opt/kylin-pkg-tool/src/

# 2. 生成应用图标
python3 tools/gen_icon.py packaging/usr/share/icons/hicolor/256x256/apps/kylin-pkg-tool.png

# 3. 设置脚本权限
chmod 755 packaging/DEBIAN/postinst packaging/DEBIAN/postrm
chmod 755 packaging/usr/bin/kylin-pkg-tool

# 4. 构建 deb（需 dpkg-dev）
dpkg-deb --build --root-owner-group packaging kylin-pkg-tool_1.0.0_all.deb
```

或直接运行根目录的 `build.sh` 一键完成以上步骤：

```bash
./build.sh 1.0.0
```

## 安装与卸载

```bash
sudo dpkg -i kylin-pkg-tool_1.0.0_all.deb
sudo apt-get install -f   # 若依赖未满足，自动修复

# 卸载
sudo dpkg -r kylin-pkg-tool
```

## 配置说明

打包前请按需修改 `DEBIAN/control` 中的 `Maintainer` 字段（当前为占位符）。
