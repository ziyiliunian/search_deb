#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主入口：创建 QApplication 并启动主窗口。"""
import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from . import APP_NAME, APP_TITLE, __version__
from .main_window import MainWindow


def main():
    QCoreApplication.setOrganizationName("kylin")
    QCoreApplication.setApplicationName(APP_NAME)

    if "--version" in sys.argv:
        print(__version__)
        return

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_TITLE)
    app.setDesktopFileName("kylinpkgtool")
    # 从 hicolor 图标主题加载；图标缓存尚未刷新时使用 pixmaps 后备文件
    app_icon = QIcon.fromTheme("kylinpkgtool")
    if app_icon.isNull():
        app_icon = QIcon("/usr/share/pixmaps/kylinpkgtool.png")
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    win = MainWindow()
    if not app_icon.isNull():
        win.setWindowIcon(app_icon)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
