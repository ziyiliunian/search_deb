# -*- coding: utf-8 -*-
"""通用工具函数。"""
import os
import subprocess


def get_desktop_path():
    """获取当前用户桌面目录，优先使用系统配置，失败时回退到常见目录名。"""
    home = os.path.expanduser("~")
    # 尝试通过 xdg-user-dir 获取（遵循系统语言和配置）
    try:
        result = subprocess.run(
            ["xdg-user-dir", "DESKTOP"],
            capture_output=True, text=True, timeout=1,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:  # noqa: BLE001
        pass
    # 常见中文和英文桌面目录名
    for name in ("桌面", "Desktop"):
        path = os.path.join(home, name)
        if os.path.isdir(path):
            return path
    # 若都不存在，创建默认“桌面”目录（避免后续作为 cwd 启动进程失败）；
    # 创建失败则回退到家目录
    default = os.path.join(home, "桌面")
    try:
        os.makedirs(default, exist_ok=True)
        return default
    except OSError:
        return home
