# -*- coding: utf-8 -*-
"""异步命令执行（QThread），避免阻塞 GUI 并实时回传输出。"""
import os
import signal
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
        self._proc = None
        self._stop_requested = False

    def stop(self):
        """强制终止命令所在进程组，包括 apt 及其下载子进程。"""
        self._stop_requested = True
        proc = self._proc
        if proc is None or proc.poll() is not None:
            return
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError, OSError):
            try:
                proc.kill()
            except (ProcessLookupError, OSError):
                pass

    def run(self):
        full = ("pkexec " + self.cmd) if self.privileged else self.cmd
        self.line_ready.emit("\n▶ 执行：" + full)
        output = []
        try:
            if self._stop_requested:
                self.finished.emit(130, "")
                return
            self._proc = subprocess.Popen(
                full,
                shell=True,
                cwd=self.cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
            for line in iter(self._proc.stdout.readline, ""):
                self.line_ready.emit(line.rstrip("\n"))
                output.append(line.rstrip("\n"))
            code = self._proc.wait()
            if self._stop_requested:
                code = 130
        except Exception as exc:  # noqa: BLE001
            self.line_ready.emit("错误：" + str(exc))
            code = 130 if self._stop_requested else -1
        finally:
            self._proc = None
        self.finished.emit(code, "\n".join(output))
