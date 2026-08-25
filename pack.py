#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速打包脚本（跨平台）。

- 重新生成应用图标；
- 始终生成源码压缩包 dist/KylinPkgTool_<version>_src.zip（可传输到麒麟系统）；
- 若本机存在 dpkg-deb（Linux），自动调用 build.sh 构建 .deb 安装包。

用法:
    python pack.py [版本号]
"""
import os
import re
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
APP_NAME = "KylinPkgTool"


def read_version():
    p = os.path.join(HERE, "src", "__init__.py")
    with open(p, encoding="utf-8") as f:
        for line in f:
            m = re.search(r'__version__\s*=\s*"([^"]+)"', line)
            if m:
                return m.group(1)
    return "1.0"


def run(cmd, cwd=None):
    print("  $ " + cmd)
    return subprocess.call(cmd, shell=True, cwd=cwd)


def make_icon():
    icon = os.path.join(
        HERE, "packaging", "usr", "share", "icons",
        "hicolor", "256x256", "apps", APP_NAME + ".png",
    )
    os.makedirs(os.path.dirname(icon), exist_ok=True)
    gen = os.path.join(HERE, "tools", "gen_icon.py")
    return subprocess.call([sys.executable, gen, icon])


def build_zip(version):
    out = os.path.join(HERE, "dist", "{}_{}_src.zip".format(APP_NAME, version))
    include = ["src", "packaging", "tools", "build.sh", "pack.py",
               "requirements.txt", "README.md", ".gitignore"]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for item in include:
            p = os.path.join(HERE, item)
            if os.path.isdir(p):
                for root, _, files in os.walk(p):
                    if "__pycache__" in root:
                        continue
                    for fn in files:
                        full = os.path.join(root, fn)
                        z.write(full, os.path.relpath(full, HERE))
            elif os.path.isfile(p):
                z.write(p, item)
    print("  SUCCESS: dist/" + os.path.basename(out))


def build_deb(version):
    if os.name != "posix":
        print("  跳过 deb 构建（非 Linux 环境）。可在麒麟系统上运行 ./build.sh 构建。")
        return
    if shutil.which("dpkg-deb") is None:
        print("  跳过 deb 构建（未找到 dpkg-deb）。可在麒麟系统上运行 ./build.sh 构建。")
        return
    return run("bash build.sh {}".format(version), cwd=HERE)


def main():
    version = sys.argv[1] if len(sys.argv) > 1 else read_version()
    print("=== KylinPkgTool 快速打包 v{} ===".format(version))
    os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)

    print("[1/3] 生成应用图标 ...")
    make_icon()

    print("[2/3] 生成源码压缩包 ...")
    build_zip(version)

    print("[3/3] 构建 deb 安装包 ...")
    build_deb(version)

    print("完成。")


if __name__ == "__main__":
    main()
