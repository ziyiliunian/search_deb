#!/bin/bash
# KylinPkgTool Debian 打包脚本
# 用法: ./build.sh [版本号]
#   默认版本 1.0；可传参覆盖，如 ./build.sh 1.0.1
#   默认安装路径 /opt/search_deb
set -e
cd "$(dirname "$0")"

APP_NAME="KylinPkgTool"
# Debian 包名按规范强制小写（dpkg 内部 Package 字段）
DEB_NAME="kylinpkgtool"
INSTALL_DIR="search_deb"
VERSION="${1:-1.2}"
ARCH="all"
PKG="${APP_NAME}_${VERSION}_${ARCH}.deb"
OUT_DIR="dist"
PKGROOT="build/pkgroot"

echo "=== KylinPkgTool Debian Build (v${VERSION}) ==="

# 检查依赖工具
if ! command -v dpkg-deb >/dev/null 2>&1; then
    echo "错误: 未找到 dpkg-deb，请安装 dpkg-dev (sudo apt-get install dpkg-dev)"
    exit 1
fi

# 清理旧构建
rm -rf "$PKGROOT"
mkdir -p "$PKGROOT"

# 以 packaging/ 为骨架复制到构建根
cp -r packaging/* "$PKGROOT/"
# 骨架说明文档不进入 deb
rm -f "$PKGROOT/README.md"

# 复制源码（保持 src/ 包结构，启动器通过 /opt/search_deb/src 以模块方式导入）
mkdir -p "$PKGROOT/opt/${INSTALL_DIR}"
cp -r src "$PKGROOT/opt/${INSTALL_DIR}/src"
# 排除 Python 字节码缓存，保持包内干净
find "$PKGROOT/opt/${INSTALL_DIR}" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true

# 生成 Debian changelog（打包必要文件，gzip -9 压缩）
DOC_DIR="$PKGROOT/usr/share/doc/${DEB_NAME}"
mkdir -p "$DOC_DIR"
cat > "$DOC_DIR/changelog" <<EOF
${DEB_NAME} (${VERSION}) unstable; urgency=medium

  * 搜索区与运行日志区改为可拖动分割布局，随窗口自动伸缩
  * 修复按库文件搜索时错误输出被误识别为包名的问题
  * 默认安装路径为 /opt/${INSTALL_DIR}

 -- KylinPkgTool Developers <dev@localhost>  $(date -R)
EOF
gzip -9 -n "$DOC_DIR/changelog"

# 生成图标（始终重新绘制，确保设计生效；纯标准库，无需 PIL/PyQt5）
ICON="$PKGROOT/usr/share/icons/hicolor/256x256/apps/${APP_NAME}.png"
mkdir -p "$(dirname "$ICON")"
echo "生成应用图标..."
python3 tools/gen_icon.py "$ICON"

# 设置权限
chmod 755 "$PKGROOT/DEBIAN/postinst" "$PKGROOT/DEBIAN/postrm"
chmod 755 "$PKGROOT/usr/bin/${APP_NAME}"
chmod 644 "$PKGROOT/usr/share/applications/${APP_NAME}.desktop"
chmod 644 "$ICON"
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
