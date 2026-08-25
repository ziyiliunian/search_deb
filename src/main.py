#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主入口：创建 QApplication 并启动主窗口。"""
import sys

from PyQt5.QtCore import QCoreApplication
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

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
