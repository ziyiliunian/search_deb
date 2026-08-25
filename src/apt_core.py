# -*- coding: utf-8 -*-
"""核心模块：apt 命令构建与结果解析（纯逻辑，无 GUI 依赖）。"""
import re
import shlex


class AptManager:
    """封装银河麒麟系统的 apt / dpkg 相关操作与命令构建。"""

    def __init__(self, source_file, pref_file):
        self.source_file = source_file
        self.pref_file = pref_file

    # ===================== 命令构建 =====================
    def enable_arch_cmd(self, arch):
        return "dpkg --add-architecture {}".format(shlex.quote(arch))

    @staticmethod
    def _write_file_cmd(path, content):
        """构建以特权身份写入文件的命令（重定向在 bash -c 内完成）。

        使用 printf + shlex.quote，避免 heredoc 对内容中的单引号/特殊标记敏感。
        """
        inner = "printf %s {} > {}".format(shlex.quote(content), shlex.quote(path))
        return "bash -c {}".format(shlex.quote(inner))

    def write_source_cmd(self, content):
        return self._write_file_cmd(self.source_file, content)

    def write_pref_cmd(self, content):
        return self._write_file_cmd(self.pref_file, content)

    def remove_source_cmd(self):
        return "rm -f {}".format(self.source_file)

    def remove_pref_cmd(self):
        return "rm -f {}".format(self.pref_file)

    def apt_update_cmd(self):
        return "apt update"

    def policy_cmd(self, pkg, arch):
        return "apt-cache policy {}:{}".format(shlex.quote(pkg), shlex.quote(arch))

    def download_cmd(self, pkg, arch, version):
        return "apt download {}:{}={}".format(
            shlex.quote(pkg), shlex.quote(arch), shlex.quote(version)
        )

    def apt_file_search_cmd(self, keyword):
        return "apt-file search {}".format(shlex.quote(keyword))

    def apt_cache_search_cmd(self, keyword):
        return "apt-cache search {}".format(shlex.quote(keyword))

    # ===================== 结果解析 =====================
    @staticmethod
    def parse_versions(output):
        """从 apt-cache policy 输出中解析可用版本号。"""
        versions = []
        pattern = re.compile(r"^(\d[\w.\-:+~]+)\s+\d+")
        for line in output.splitlines():
            line = line.strip()
            match = pattern.match(line)
            if match:
                ver = match.group(1).strip()
                # 正则已限定以数字开头并带优先级数字，这里仅做非空与去重校验，
                # 避免过滤掉合法的纯数字日期版本（如 20240101）
                if ver and ver not in versions:
                    versions.append(ver)
        return versions

    @staticmethod
    def parse_search_packages(output):
        """从 apt-file / apt-cache search 输出中提取候选包名。"""
        pkgs = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            if ": " in line:  # apt-file 格式: "pkgname: /path/to/file"
                pkg = line.split(": ", 1)[0].strip()
            elif " - " in line:  # apt-cache 格式: "pkgname - description"
                pkg = line.split(" - ", 1)[0].strip()
            else:
                pkg = line.split()[0].strip()
            if pkg and pkg not in pkgs:
                pkgs.append(pkg)
        return pkgs
