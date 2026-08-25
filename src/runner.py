# -*- coding: utf-8 -*-
"""异步命令执行（QThread），避免阻塞 GUI 并实时回传输出。"""
import subprocess

from PyQt5.QtCore import QThread, pyqtSignal


class CommandWorker(QThread):
    """在后台线程执行一条命令，逐行回传输出，结束时回传返回码与完整输出。"""

    line_ready = pyqtSignal(str)
    finished = pyqtSignal(int, str)  # (返回码, 完整输出)

    def __init__(self, cmd, cwd, privileged=False, parent=None):
        super().__init__(parent)
        self.cmd = cmd
        self.cwd = cwd
        self.privileged = privileged

    def run(self):
        full = ("pkexec " + self.cmd) if self.privileged else self.cmd
        self.line_ready.emit("\n▶ 执行：" + full)
        output = []
        try:
            proc = subprocess.Popen(
                full,
                shell=True,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for line in iter(proc.stdout.readline, ""):
                self.line_ready.emit(line.rstrip("\n"))
                output.append(line.rstrip("\n"))
            code = proc.wait()
        except Exception as exc:  # noqa: BLE001
            self.line_ready.emit("错误：" + str(exc))
            code = -1
        self.finished.emit(code, "\n".join(output))
