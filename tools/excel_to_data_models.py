#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将“主线版本对应源地址.xlsx”的“外网源”工作表转换为 src/data_models.py。

仅使用 Python 标准库，避免在打包机上额外安装 openpyxl。
"""

import argparse
import pprint
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
M = "{%s}" % MAIN_NS


def _column_index(cell_ref):
    match = re.match(r"[A-Z]+", cell_ref or "")
    if not match:
        raise ValueError("无效的单元格引用：%r" % cell_ref)
    number = 0
    for char in match.group(0):
        number = number * 26 + ord(char) - ord("A") + 1
    return number - 1


def _shared_strings(archive):
    path = "xl/sharedStrings.xml"
    if path not in archive.namelist():
        return []
    root = ET.fromstring(archive.read(path))
    return [
        "".join(node.text or "" for node in item.iter(M + "t"))
        for item in root.findall(M + "si")
    ]


def _sheet_path(archive, sheet_name):
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rel_map = {
        rel.get("Id"): rel.get("Target")
        for rel in relationships.findall("{%s}Relationship" % PKG_REL_NS)
    }
    sheets = workbook.find(M + "sheets")
    for sheet in sheets:
        if sheet.get("name") != sheet_name:
            continue
        relation_id = sheet.get("{%s}id" % REL_NS)
        target = rel_map[relation_id].lstrip("/")
        if target.startswith("xl/"):
            return target
        return "xl/" + target
    raise ValueError("Excel 中不存在工作表：%s" % sheet_name)


def _read_rows(excel_path, sheet_name):
    with zipfile.ZipFile(str(excel_path)) as archive:
        strings = _shared_strings(archive)
        root = ET.fromstring(archive.read(_sheet_path(archive, sheet_name)))
        rows = []
        for row in root.iter(M + "row"):
            values = {}
            for cell in row.findall(M + "c"):
                value_node = cell.find(M + "v")
                inline_node = cell.find(M + "is")
                if value_node is not None:
                    value = value_node.text or ""
                    if cell.get("t") == "s":
                        value = strings[int(value)]
                elif inline_node is not None:
                    value = "".join(
                        node.text or "" for node in inline_node.iter(M + "t")
                    )
                else:
                    value = ""
                values[_column_index(cell.get("r"))] = value
            if values:
                rows.append([values.get(index, "") for index in range(max(values) + 1)])
        return rows


def _classify_group(name):
    if name.startswith("XC-"):
        return "XC"
    if name.startswith("HWE-PP-"):
        return "HWE-PP"
    if name.startswith("HWE-"):
        return "HWE"
    if name.startswith("wayland-") and name.endswith("-990"):
        return "wayland-990"
    if name.startswith("wayland-") and name.lower().endswith("-9006c"):
        return "wayland-9006c"
    if name.startswith("wayland-") and name.endswith("-M900"):
        return "wayland-M900"
    if name.startswith("wayland-") and name.endswith("-9000C"):
        return "wayland-9000C"
    if name.startswith("wayland 华为"):
        return "华为"
    raise ValueError("无法识别产品线：%s" % name)


def _extract_lines(cell_text):
    sources = []
    preferences = []
    for raw_line in (cell_text or "").splitlines():
        line = raw_line.strip()
        if re.match(r"^deb(?:-src)?\s+", line):
            sources.append(line)
        elif line.startswith("Package:"):
            # apt preferences 的多个记录必须用空行分隔；Excel 未留空行时自动补齐
            if preferences and preferences[-1] != "":
                preferences.append("")
            preferences.append(line)
        elif line.startswith(("Pin:", "Pin-Priority:")):
            preferences.append(line)
        elif not line and preferences and preferences[-1] != "":
            preferences.append("")
    while preferences and preferences[-1] == "":
        preferences.pop()
    return sources, preferences


def parse_entries(excel_path, sheet_name="外网源"):
    """读取新版两列结构，返回 VERSION_ENTRIES。

    A 列为版本名；B 列为多行源/Pin 配置。A 列为空时，B 列视为上一条目的续行。
    标题、备注等非 deb/Pin 行会被忽略。
    """
    entries = []
    current = None
    for row in _read_rows(excel_path, sheet_name):
        name = str(row[0]).strip() if row else ""
        content = str(row[1]).strip() if len(row) > 1 else ""
        sources, preferences = _extract_lines(content)

        if name and (sources or preferences):
            if current:
                entries.append(current)
            current = {
                "group": _classify_group(name),
                "name": name,
                "sources": sources,
                "preferences": preferences,
            }
        elif not name and current and (sources or preferences):
            current["sources"].extend(sources)
            if (
                preferences
                and preferences[0].startswith("Package:")
                and current["preferences"]
                and current["preferences"][-1] != ""
            ):
                current["preferences"].append("")
            current["preferences"].extend(preferences)
        # 表头、分组标题、备注行不进入数据模型

    if current:
        entries.append(current)
    if not entries:
        raise ValueError("未从工作表 %s 读取到任何版本条目" % sheet_name)

    names = [entry["name"] for entry in entries]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError("Excel 中存在重复版本名：%s" % ", ".join(duplicates))
    for entry in entries:
        if not entry["sources"]:
            raise ValueError("版本 %s 没有 deb 源" % entry["name"])
    return entries


def render_data_models(entries):
    formatted_entries = pprint.pformat(entries, width=120, sort_dicts=False)
    return '''# -*- coding: utf-8 -*-
"""数据模型与软件源配置。

数据来源：主线版本对应源地址.xlsx 的「外网源」工作表，
由 tools/excel_to_data_models.py 自动生成，请勿手工修改 VERSION_ENTRIES。
"""


# 目标架构（选择项）：前三个为标准 dpkg 架构，最后一个为 ARM 特殊架构（华为麒麟/wayland）
ARCHITECTURES = ["amd64", "arm64", "loongarch64", "arm-wayland"]

ARCH_LABELS = {
    "amd64": "amd64",
    "arm64": "arm64",
    "loongarch64": "loongarch64",
    "arm-wayland": "wayland / 华为 (ARM 特殊)",
}

ARCH_DPKG = {
    "amd64": "amd64",
    "arm64": "arm64",
    "loongarch64": "loongarch64",
    "arm-wayland": "arm64",
}

GROUP_ARCHS = {
    "XC": ["amd64", "arm64", "loongarch64"],
    "HWE": ["amd64"],
    "HWE-PP": ["amd64"],
    "wayland-990": ["arm-wayland"],
    "wayland-9006c": ["arm-wayland"],
    "wayland-M900": ["arm-wayland"],
    "wayland-9000C": ["arm-wayland"],
    "华为": ["arm-wayland"],
}

# 工具只操作以下专属文件，不修改 /etc/apt/sources.list 或系统既有 preferences
SOURCE_FILE = "/etc/apt/sources.list.d/kylinpkgtool.list"
PREF_FILE = "/etc/apt/preferences.d/kylinpkgtool.pref"

# 每个版本条目：{group, name, sources: [deb行...], preferences: [Pin行...]}
VERSION_ENTRIES = %s

GROUPS = ["XC", "HWE", "HWE-PP", "wayland-990", "wayland-9006c", "wayland-M900", "wayland-9000C", "华为"]

_BY_NAME = {e["name"]: e for e in VERSION_ENTRIES}


def versions_of_group(group):
    """返回指定组下的版本名列表。"""
    return [e["name"] for e in VERSION_ENTRIES if e["group"] == group]


def available_versions(arch):
    """按架构返回可用版本名列表。"""
    return [e["name"] for e in VERSION_ENTRIES if arch in GROUP_ARCHS.get(e["group"], [])]


def available_groups(arch):
    """按架构返回可用的产品线名列表（保持顺序）。"""
    return [g for g in GROUPS if arch in GROUP_ARCHS.get(g, []) and versions_of_group(g)]


def dpkg_arch_of(arch):
    """返回架构对应的 dpkg 架构名。"""
    return ARCH_DPKG.get(arch, arch)


def get_entry(name):
    """按版本名返回条目，不存在则返回 None。"""
    return _BY_NAME.get(name)


def build_sources_content(name):
    """返回该版本的 sources.list 内容（deb 行）。"""
    entry = _BY_NAME.get(name)
    if not entry:
        return ""
    return "\\n".join(entry["sources"]) + "\\n"


def build_preferences_content(name):
    """返回该版本的 apt 优先级设置内容；无则返回 None。"""
    entry = _BY_NAME.get(name)
    if not entry or not entry["preferences"]:
        return None
    return "\\n".join(entry["preferences"]) + "\\n"
''' % formatted_entries


def main():
    parser = argparse.ArgumentParser(description="从 Excel 生成 src/data_models.py")
    parser.add_argument("excel", nargs="?", default="主线版本对应源地址.xlsx")
    parser.add_argument("--sheet", default="外网源")
    parser.add_argument("--output", default="src/data_models.py")
    args = parser.parse_args()

    excel_path = Path(args.excel).resolve()
    output_path = Path(args.output).resolve()
    entries = parse_entries(excel_path, args.sheet)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_data_models(entries), encoding="utf-8")
    print("已生成 %s，共 %d 个版本条目" % (output_path, len(entries)))


if __name__ == "__main__":
    main()
