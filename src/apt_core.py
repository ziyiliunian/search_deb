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

    def apt_file_search_cmd(self, keyword, arch=None):
        """apt-file 搜索命令；arch 非空时按目标架构搜索（跨架构下载场景）。"""
        if arch:
            return "apt-file --architecture {} search {}".format(
                shlex.quote(arch), shlex.quote(keyword)
            )
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

    # Debian 包名规范：小写字母/数字开头，仅含小写字母数字 . + -
    _PKG_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9.+\-]*$")

    @staticmethod
    def parse_search_packages(output):
        """从 apt-file / apt-cache search 输出中提取候选包名。

        严格校验包名格式，避免把错误输出（如 shell 报错）误识别为包名。
        """
        pkgs = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            if ": " in line:  # apt-file/dpkg -S 格式: "pkg[:arch]: /path/to/file"
                pkg = line.split(": ", 1)[0].strip()
            elif " - " in line:  # apt-cache 格式: "pkgname - description"
                pkg = line.split(" - ", 1)[0].strip()
            else:
                pkg = line.split()[0].strip()
            pkg = pkg.split(":", 1)[0].strip()  # 去掉 :arch 架构后缀
            if pkg and AptManager._PKG_NAME_RE.match(pkg) and pkg not in pkgs:
                pkgs.append(pkg)
        return pkgs

    @staticmethod
    def extract_search_terms(keyword):
        """从库/文件名提取候选搜索关键词（供 apt-cache search 回退使用）。

        例: libBLT.2.5.so.8.6 -> ["BLT.2.5", "BLT"]
            libssl.so.3       -> ["ssl"]
        """
        base = keyword.strip()
        if base.lower().startswith("lib"):
            base = base[3:]
        if ".so" in base:
            base = base.split(".so", 1)[0]
        base = base.strip(".-_")
        terms = []
        if base:
            terms.append(base)
            short = re.split(r"[.\-_]", base)[0]
            if short and short != base:
                terms.append(short)
        return terms
