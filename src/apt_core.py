# -*- coding: utf-8 -*-
"""核心模块：apt 命令构建与结果解析（纯逻辑，无 GUI 依赖）。"""
import re
import shlex


class AptManager:
    """封装银河麒麟系统的 apt / dpkg 相关操作与命令构建。"""

    def __init__(self, source_file, pref_file, state_dir="/var/lib/kylinpkgtool"):
        self.source_file = source_file
        self.pref_file = pref_file
        self.state_dir = state_dir

    # ===================== 命令构建 =====================
    def enable_arch_cmd(self, arch):
        """仅在架构尚未启用时添加，并记录由本工具新增的架构。"""
        arch_q = shlex.quote(arch)
        state_q = shlex.quote(self.state_dir)
        inner = (
            "set -e; arch={arch}; state={state}; "
            "native=$(dpkg --print-architecture); "
            "if [ \"$arch\" = \"$native\" ] || "
            "dpkg --print-foreign-architectures | grep -Fxq \"$arch\"; then exit 0; fi; "
            "dpkg --add-architecture \"$arch\"; mkdir -p \"$state\"; "
            "touch \"$state/added-architectures\"; "
            "grep -Fxq \"$arch\" \"$state/added-architectures\" || "
            "printf '%s\\n' \"$arch\" >> \"$state/added-architectures\""
        ).format(arch=arch_q, state=state_q)
        return "bash -c {}".format(shlex.quote(inner))

    def _write_file_cmd(self, path, content, key):
        """首次写入前备份原文件，再以临时文件原子替换工具配置。"""
        path_q = shlex.quote(path)
        content_q = shlex.quote(content)
        state_q = shlex.quote(self.state_dir)
        key_q = shlex.quote(key)
        inner = (
            "set -e; target={path}; state={state}; key={key}; "
            "mkdir -p \"$state/backup\"; "
            "if [ ! -e \"$state/backup/$key.saved\" ]; then "
            "if [ -e \"$target\" ]; then cp -a \"$target\" \"$state/backup/$key.original\"; "
            "else : > \"$state/backup/$key.absent\"; fi; "
            ": > \"$state/backup/$key.saved\"; fi; "
            "tmp=$(mktemp \"${{target}}.tmp.XXXXXX\"); "
            "printf %s {content} > \"$tmp\"; chmod 0644 \"$tmp\"; mv -f \"$tmp\" \"$target\""
        ).format(path=path_q, state=state_q, key=key_q, content=content_q)
        return "bash -c {}".format(shlex.quote(inner))

    def _clear_file_cmd(self, path, key):
        """首次操作前备份原文件，然后移除工具当前配置。"""
        path_q = shlex.quote(path)
        state_q = shlex.quote(self.state_dir)
        key_q = shlex.quote(key)
        inner = (
            "set -e; target={path}; state={state}; key={key}; "
            "mkdir -p \"$state/backup\"; "
            "if [ ! -e \"$state/backup/$key.saved\" ]; then "
            "if [ -e \"$target\" ]; then cp -a \"$target\" \"$state/backup/$key.original\"; "
            "else : > \"$state/backup/$key.absent\"; fi; "
            ": > \"$state/backup/$key.saved\"; fi; rm -f \"$target\""
        ).format(path=path_q, state=state_q, key=key_q)
        return "bash -c {}".format(shlex.quote(inner))

    def _restore_file_cmd(self, path, key):
        """恢复首次操作前的原文件；没有工具状态记录时不触碰现有文件。"""
        path_q = shlex.quote(path)
        state_q = shlex.quote(self.state_dir)
        key_q = shlex.quote(key)
        inner = (
            "set -e; target={path}; state={state}; key={key}; "
            "if [ -e \"$state/backup/$key.original\" ]; then "
            "cp -a \"$state/backup/$key.original\" \"$target\"; "
            "elif [ -e \"$state/backup/$key.absent\" ] || "
            "[ -e \"$state/backup/$key.saved\" ]; then rm -f \"$target\"; fi; "
            "rm -f \"$state/backup/$key.original\" \"$state/backup/$key.absent\" "
            "\"$state/backup/$key.saved\""
        ).format(path=path_q, state=state_q, key=key_q)
        return "bash -c {}".format(shlex.quote(inner))

    def write_source_cmd(self, content):
        return self._write_file_cmd(self.source_file, content, "source")

    def write_pref_cmd(self, content):
        return self._write_file_cmd(self.pref_file, content, "preferences")

    def clear_pref_cmd(self):
        return self._clear_file_cmd(self.pref_file, "preferences")

    def restore_source_cmd(self):
        return self._restore_file_cmd(self.source_file, "source")

    def restore_pref_cmd(self):
        return self._restore_file_cmd(self.pref_file, "preferences")

    def cleanup_legacy_cmd(self):
        """备份并清理旧版本工具的专属文件，不操作系统默认配置。"""
        state_q = shlex.quote(self.state_dir)
        inner = (
            "set -e; state={state}; mkdir -p \"$state/legacy-backup\"; "
            "for item in source pref; do case \"$item\" in "
            "source) old=/etc/apt/sources.list.d/kylin-tool-selected.list;; "
            "pref) old=/etc/apt/preferences.d/kylin-tool.pref;; esac; "
            "if [ -e \"$old\" ] && [ ! -e \"$state/legacy-backup/$item.saved\" ]; then "
            "cp -a \"$old\" \"$state/legacy-backup/$item.original\"; "
            "touch \"$state/legacy-backup/$item.saved\"; rm -f \"$old\"; fi; done"
        ).format(state=state_q)
        return "bash -c {}".format(shlex.quote(inner))

    def restore_legacy_cmd(self):
        """恢复旧版本工具文件；无备份记录时不触碰现有文件。"""
        state_q = shlex.quote(self.state_dir)
        inner = (
            "set -e; state={state}; "
            "if [ -e \"$state/legacy-backup/source.original\" ]; then "
            "cp -a \"$state/legacy-backup/source.original\" /etc/apt/sources.list.d/kylin-tool-selected.list; fi; "
            "if [ -e \"$state/legacy-backup/pref.original\" ]; then "
            "cp -a \"$state/legacy-backup/pref.original\" /etc/apt/preferences.d/kylin-tool.pref; fi"
        ).format(state=state_q)
        return "bash -c {}".format(shlex.quote(inner))

    # 兼容旧调用名：恢复操作而不是无条件删除
    def remove_source_cmd(self):
        return self.restore_source_cmd()

    def remove_pref_cmd(self):
        return self.restore_pref_cmd()

    def restore_architectures_cmd(self):
        """撤销本工具新增的外来架构；系统原本已有的架构不会被记录或删除。"""
        state_q = shlex.quote(self.state_dir)
        inner = (
            "set -e; state={state}; file=\"$state/added-architectures\"; "
            "[ -e \"$file\" ] || exit 0; tmp=\"${{file}}.remaining\"; : > \"$tmp\"; "
            "while IFS= read -r arch; do [ -n \"$arch\" ] || continue; "
            "if ! dpkg --remove-architecture \"$arch\"; then printf '%s\\n' \"$arch\" >> \"$tmp\"; fi; done < \"$file\"; "
            "if [ -s \"$tmp\" ]; then mv -f \"$tmp\" \"$file\"; exit 1; "
            "else rm -f \"$tmp\" \"$file\"; fi"
        ).format(state=state_q)
        return "bash -c {}".format(shlex.quote(inner))

    def apt_update_cmd(self):
        return "apt update"

    def policy_cmd(self, pkg, arch):
        return "apt-cache policy {}:{}".format(shlex.quote(pkg), shlex.quote(arch))

    def download_cmd(self, pkg, arch, version):
        return "apt download {}:{}={}".format(
            shlex.quote(pkg), shlex.quote(arch), shlex.quote(version)
        )

    def dependency_query_cmd(self, pkg, arch, version):
        """查询选中包的递归强依赖与预依赖，不包含 recommends/suggests。

        apt-cache depends 在部分银河麒麟版本不接受 pkg=version，因此先用 policy
        确认所选版本仍存在，再按 pkg:arch 查询当前源配置下的依赖关系。
        """
        target = "{}:{}".format(pkg, arch)
        version_q = shlex.quote(version)
        target_q = shlex.quote(target)
        return (
            "apt-cache policy {target} | "
            "grep -F -- {version} >/dev/null && "
            "apt-cache depends --recurse --important --no-recommends --no-suggests "
            "--no-conflicts --no-breaks --no-replaces --no-enhances {target}"
        ).format(target=target_q, version=version_q)

    def dependencies_download_cmd(self, packages, arch):
        """按依赖包的实际架构逐个下载；单包失败不阻断后续包。

        Architecture: all 包不能写成 pkg:arm64，否则 apt 会报告没有候选版本。
        因此优先探测目标架构候选；不存在时再探测架构无关的普通包名。
        """
        packages_q = " ".join(shlex.quote(pkg) for pkg in packages)
        arch_q = shlex.quote(arch)
        inner = (
            "arch={arch}; total=0; failed=0; skipped=0; "
            "for pkg in {packages}; do total=$((total + 1)); target=; "
            "if apt-cache show \"$pkg:$arch\" 2>/dev/null | "
            "grep -Fxq \"Architecture: $arch\"; then target=\"$pkg:$arch\"; "
            "elif apt-cache show \"$pkg\" 2>/dev/null | "
            "grep -Fxq 'Architecture: all'; then target=\"$pkg\"; fi; "
            "if [ -z \"$target\" ]; then "
            "printf '跳过：%s（目标架构及 all 架构均无候选版本，可能是未选中的备选依赖）\\n' \"$pkg\"; "
            "skipped=$((skipped + 1)); continue; fi; "
            "printf '下载：%s\\n' \"$target\"; "
            "if ! apt download \"$target\"; then failed=$((failed + 1)); fi; done; "
            "printf '依赖下载汇总：共 %s 个，成功 %s 个，失败 %s 个，跳过 %s 个\\n' "
            "\"$total\" \"$((total - failed - skipped))\" \"$failed\" \"$skipped\"; "
            "[ \"$failed\" -eq 0 ]"
        ).format(arch=arch_q, packages=packages_q)
        return "bash -c {}".format(shlex.quote(inner))

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
    def parse_dependencies(output, root_pkg, target_arch):
        """解析 apt-cache depends --recurse 输出，返回去重后的实际依赖包名。"""
        dependencies = []
        root_pkg = root_pkg.split(":", 1)[0]
        dependency_labels = ("Depends:", "PreDepends:", "依赖:", "预依赖:")
        ignored_labels = (
            "Recommends:", "Suggests:", "Conflicts:", "Breaks:",
            "Replaces:", "Enhances:", "推荐:", "建议:",
        )
        for raw_line in output.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(ignored_labels):
                continue
            for label in dependency_labels:
                if line.startswith(label):
                    line = line[len(label):].strip()
                    break
            # apt-cache 可能输出“候选包 | 备选包”；选择第一个实际包名。
            line = line.split(" | ", 1)[0].strip()
            if line.startswith("<") or " " in line:
                continue
            if ":" in line:
                pkg, arch = line.rsplit(":", 1)
                if arch not in (target_arch, "any"):
                    continue
            else:
                pkg = line
            if (
                pkg != root_pkg
                and AptManager._PKG_NAME_RE.fullmatch(pkg)
                and pkg not in dependencies
            ):
                dependencies.append(pkg)
        return dependencies

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

        例: libBLT.2.5.so.8.6          -> ["BLT.2.5", "BLT"]
            libssl.so.3                -> ["ssl"]
            /usr/lib/libhandle.so.1.0.3 -> ["handle"]
        """
        base = keyword.strip()
        # 完整路径输入时取文件名部分（兼容 / 与 \ 分隔符）
        base = base.replace("\\", "/").rsplit("/", 1)[-1]
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
