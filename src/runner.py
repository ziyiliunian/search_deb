# -*- coding: utf-8 -*-
"""异步命令执行（QThread），避免阻塞 GUI 并实时回传输出。"""
import os
import signal
import subprocess
import threading

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
        self._proc_lock = threading.Lock()

    @staticmethod
    def _signal_process(proc, sig):
        if proc is None or proc.poll() is not None:
            return
        try:
            os.killpg(os.getpgid(proc.pid), sig)
        except (ProcessLookupError, PermissionError, OSError):
            try:
                proc.send_signal(sig)
            except (ProcessLookupError, OSError):
                pass

    def _kill_if_running(self, proc):
        self._signal_process(proc, signal.SIGKILL)

    def stop(self):
        """先请求进程组正常退出，超时后强制终止。"""
        with self._proc_lock:
            self._stop_requested = True
            proc = self._proc
        if proc is None or proc.poll() is not None:
            return
        self._signal_process(proc, signal.SIGTERM)
        timer = threading.Timer(2.0, self._kill_if_running, args=(proc,))
        timer.daemon = True
        timer.start()

    def run(self):
        full = ("pkexec " + self.cmd) if self.privileged else self.cmd
        self.line_ready.emit("\n▶ 执行：" + full)
        output = []
        try:
            with self._proc_lock:
                cancelled = self._stop_requested
                if not cancelled:
                    self._proc = subprocess.Popen(
                        full,
                        shell=True,
                        cwd=self.cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        start_new_session=True,
                    )
                    proc = self._proc
            if cancelled:
                self.finished.emit(130, "")
                return
            for line in iter(proc.stdout.readline, ""):
                self.line_ready.emit(line.rstrip("\n"))
                output.append(line.rstrip("\n"))
            code = proc.wait()
            if self._stop_requested:
                code = 130
        except Exception as exc:  # noqa: BLE001
            self.line_ready.emit("错误：" + str(exc))
            code = 130 if self._stop_requested else -1
        finally:
            with self._proc_lock:
                self._proc = None
        self.finished.emit(code, "\n".join(output))
