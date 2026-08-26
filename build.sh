#!/bin/bash
# 银河麒麟桌面多架构包下载工具 Debian 打包脚本
# 用法: ./build.sh [版本号]
#   默认版本 1.6；可传参覆盖，如 ./build.sh 1.6.1
#   默认安装路径 /opt/kylinpkgtool
set -e
cd "$(dirname "$0")"

APP_NAME="kylinpkgtool"
# Debian 包名按规范强制小写（dpkg 内部 Package 字段）
DEB_NAME="kylinpkgtool"
INSTALL_DIR="kylinpkgtool"
VERSION="${1:-1.6}"
ARCH="all"
PKG="${APP_NAME}_${VERSION}_${ARCH}.deb"
OUT_DIR="dist"
BUILD_DIR="build"
# 每次构建使用独立目录，避免破坏性清理及并行构建冲突
PKGROOT="${BUILD_DIR}/pkgroot-${VERSION}-$$"

echo "=== KylinPkgTool Debian Build (v${VERSION}) ==="

# 检查依赖工具
if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "错误: 未找到 dpkg-deb，请安装 dpkg-dev (sudo apt-get install dpkg-dev)"
    exit 1
fi

# 创建本次独立构建目录
mkdir -p "$PKGROOT"

# 以 packaging/ 为骨架复制到构建根
cp -r packaging/* "$PKGROOT/"
# 骨架说明文档不进入 deb
rm -f "$PKGROOT/README.md"

# 复制源码（保持 src/ 包结构，启动器通过 /opt/kylinpkgtool/src 以模块方式导入）
mkdir -p "$PKGROOT/opt/${INSTALL_DIR}"
cp -r src "$PKGROOT/opt/${INSTALL_DIR}/src"
# 排除 Python 字节码缓存，保持包内干净
find "$PKGROOT/opt/${INSTALL_DIR}" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
cp CHANGELOG.md "$PKGROOT/opt/${INSTALL_DIR}/CHANGELOG.md"

# 生成 Debian changelog（打包必要文件，gzip -9 压缩）
DOC_DIR="$PKGROOT/usr/share/doc/${DEB_NAME}"
mkdir -p "$DOC_DIR"
cat > "$DOC_DIR/changelog" <<EOF
${DEB_NAME} (${VERSION}) unstable; urgency=medium

  * 新增“终止下载”，可强制终止软件包及递归依赖下载进程树
  * 目标版本源的迁移、写入、优先级配置与索引更新合并为单次授权
  * 下载终止与关闭窗口时同步回收后台子进程
  * 支持递归解析并仅下载选中版本的依赖包
  * 工具源与优先级使用专属文件，恢复默认时还原原配置和工具新增架构
  * 默认安装路径为 /opt/${INSTALL_DIR}

 -- KylinPkgTool Developers <dev@localhost>  $(date -R)
EOF
gzip -9 -n "$DOC_DIR/changelog"
cp CHANGELOG.md "$DOC_DIR/CHANGELOG.md"

# 生成多尺寸 hicolor 图标，兼容 UKUI/麒麟应用菜单、桌面与任务栏
# gen_icon.py 第二个参数为尺寸；同时提供 /usr/share/pixmaps 兼容入口
ICON_SIZES="16 24 32 48 64 128 256"
echo "生成多尺寸应用图标..."
for SIZE in $ICON_SIZES; do
    ICON="$PKGROOT/usr/share/icons/hicolor/${SIZE}x${SIZE}/apps/${APP_NAME}.png"
    mkdir -p "$(dirname "$ICON")"
    python3 tools/gen_icon.py "$ICON" "$SIZE"
done
PIXMAP="$PKGROOT/usr/share/pixmaps/${APP_NAME}.png"
mkdir -p "$(dirname "$PIXMAP")"
cp "$PKGROOT/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png" "$PIXMAP"

# 设置权限
chmod 755 "$PKGROOT/DEBIAN/postinst" "$PKGROOT/DEBIAN/postrm"
chmod 755 "$PKGROOT/usr/bin/${APP_NAME}"
chmod 644 "$PKGROOT/usr/share/applications/${APP_NAME}.desktop"
find "$PKGROOT/usr/share/icons/hicolor" -type f -name "${APP_NAME}.png" -exec chmod 644 {} +
chmod 644 "$PIXMAP"
chmod 644 "$DOC_DIR/changelog.gz"
[ -f "$DOC_DIR/copyright" ] && chmod 644 "$DOC_DIR/copyright"

# 写入版本号并自动计算 Installed-Size（KB，向上取整）
sed -i "s/^Version:.*/Version: ${VERSION}/" "$PKGROOT/DEBIAN/control"
SIZE_KB=$(du -sk "$PKGROOT/opt" | cut -f1)
sed -i "s/^Installed-Size:.*/Installed-Size: ${SIZE_KB}/" "$PKGROOT/DEBIAN/control"

# 构建 deb（保持 root 拥有者）
mkdir -p "$OUT_DIR"
echo "构建 ${OUT_DIR}/${PKG} ..."
dpkg-deb --build --root-owner-group "$PKGROOT" "${OUT_DIR}/${PKG}"

if [ -f "${OUT_DIR}/${PKG}" ]; then
    echo "=== SUCCESS: ${OUT_DIR}/${PKG} ($(du -h "${OUT_DIR}/${PKG}" | cut -f1)) ==="
    echo "安装: sudo dpkg -i ${OUT_DIR}/${PKG}"
else
    echo "=== 打包失败 ==="
    exit 1
fi
