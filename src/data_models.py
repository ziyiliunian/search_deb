# -*- coding: utf-8 -*-
"""数据模型与软件源配置。

数据来源：主线版本对应源地址.xlsx 的「外网源」工作表，
由脚本自动生成；如需修改源数据请更新 Excel 后重新生成。
"""


# 目标架构（选择项）：前三个为标准 dpkg 架构，最后一个为 ARM 特殊架构（华为麒麟/wayland）
ARCHITECTURES = ["amd64", "arm64", "loongarch64", "arm-wayland"]

# 架构显示名
ARCH_LABELS = {
    "amd64": "amd64",
    "arm64": "arm64",
    "loongarch64": "loongarch64",
    "arm-wayland": "wayland / 华为 (ARM 特殊)",
}

# 各架构对应的 dpkg 架构（用于 dpkg --add-architecture 与 apt download）
ARCH_DPKG = {
    "amd64": "amd64",
    "arm64": "arm64",
    "loongarch64": "loongarch64",
    "arm-wayland": "arm64",
}

# 各产品线适用的架构
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

# 工具生成的源文件与优先级文件路径
SOURCE_FILE = "/etc/apt/sources.list.d/kylin-tool-selected.list"
PREF_FILE = "/etc/apt/preferences.d/kylin-tool.pref"

# 每个版本条目：{group, name, sources: [deb行...], preferences: [Pin行...]}
VERSION_ENTRIES = [
    {
        "group": "XC",
        "name": "XC-2107",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2107-updates main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2107-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "XC",
        "name": "XC-2203",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2203-updates-preview main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2203-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "XC",
        "name": "XC-2303",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-updates main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "XC",
        "name": "XC-2303U2",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-update3 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-update2-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "XC",
        "name": "XC-2403U2",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-update2 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "XC",
        "name": "XC-2503",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2503-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503 main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": ["Package: *", "Pin: origin \"archive.kylinos.cn\"", "Pin: release a=10.1-kylin", "Pin-Priority: 500", "Pin: release a=10.1-kylin-2503", "Pin-Priority: 600", "Pin: release a=10.1-2503-bugfix-limit", "Pin: origin \"archive2.kylinos.cn\""],
    },
    {
        "group": "HWE",
        "name": "HWE-2107",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-hwe main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2107-hwe-updates main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2107-hwe-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "HWE",
        "name": "HWE-2203",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2203-hwe-updates-preview main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2203-hwe-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "HWE",
        "name": "HWE-2303",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-updates main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-hwe-updates main universe multiverse restricted", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-hwe-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "HWE",
        "name": "HWE-2303-update2",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-update3 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-update2-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-hwe-update3 main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-hwe-update2-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "HWE",
        "name": "HWE-2403U2",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-update2 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-hwe-update2 main universe multiverse restricted", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-hwe-bugfix-limit main", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "HWE",
        "name": "HWE-2503",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2503-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503 main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2503-hwe-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-hwe main"],
        "preferences": ["Package: *", "Pin: origin \"archive.kylinos.cn\"", "Pin: release a=10.1-kylin", "Pin-Priority: 500", "Pin: release a=10.1-kylin-2503", "Pin-Priority: 600", "Pin: release a=10.1-2503-bugfix-limit", "Pin-Priority: 600", "Pin: release a=10.1-kylin-2503-hwe", "Pin-Priority: 700", "Pin: release a=10.1-2503-hwe-bugfix-limit", "Pin: origin \"archive2.kylinos.cn\""],
    },
    {
        "group": "HWE-PP",
        "name": "HWE-PP-2303",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-updates main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-hwe-pp-updates main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-hwe-pp-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "HWE-PP",
        "name": "HWE-PP-2303-update2",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-update3 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-update2-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-hwe-pp-update3 main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-hwe-pp-update2-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "HWE-PP",
        "name": "HWE-PP-2403U2",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-update2 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-hwe-pp-update2 main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-hwe-pp-bugfix-limit main", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all"],
        "preferences": [],
    },
    {
        "group": "HWE-PP",
        "name": "HWE-PP-2503",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2503-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503 main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-V10-SP1/custom/partner/V10-SP1 default all", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2503-hwe-pp-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-hwe-pp main"],
        "preferences": ["Package: *", "Pin: origin \"archive.kylinos.cn\"", "Pin: release a=10.1-kylin", "Pin-Priority: 500", "Pin: release a=10.1-kylin-2503", "Pin-Priority: 600", "Pin: release a=10.1-2503-bugfix-limit", "Pin-Priority: 600", "Pin: release a=10.1-kylin-2503-hwe-pp", "Pin-Priority: 700", "Pin: release a=10.1-2503-hwe-pp-bugfix-limit", "Pin: origin \"archive2.kylinos.cn\""],
    },
    {
        "group": "wayland-990",
        "name": "wayland-2107-990",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-pv main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2107-wayland-kirin990-bugfix-limit main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin990/custom/partner/10_1-kirin990 default all"],
        "preferences": [],
    },
    {
        "group": "wayland-990",
        "name": "wayland-2203-990",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-wayland-2203-updates main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kirin990-feature main", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2203-wayland-bugfix-limit main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2203-wayland-kirin990-bugfix-limit main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "wayland-990",
        "name": "wayland-2303-990",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-wayland-2303-updates main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kirin990-2303-feature main", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-bugfix-limit main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-kirin990-bugfix-limit main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "wayland-990",
        "name": "wayland-2303-update2-990",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update3 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update3-kirin990 main", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update2-bugfix-limit main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update2-kirin990-bugfix-limit main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "wayland-990",
        "name": "wayland-2403U2-990",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2 main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2-kirin990 main", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-bugfix-limit main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-kirin990-bugfix-limit main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "wayland-990",
        "name": "wayland-2503-990",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland main universe restricted multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2503-wayland-bugfix-limit main universe restricted multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland-kirin990 main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland-kirin990-bugfix main universe restricted multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": ["Package: *", "Pin: origin \"archive.kylinos.cn\"", "Pin: release a=10.1-kylin", "Pin-Priority: 500", "Pin: release a=10.1-kylin-2503-wayland", "Pin-Priority: 600", "Pin: release a=10.1-2503-wayland-bugfix-limit", "Pin: release a=10.1-kylin-2503-wayland-kirin990", "Pin-Priority: 700", "Pin: release a=10.1-kylin-2503-wayland-kirin990-bugfix", "Pin: origin \"archive2.kylinos.cn\""],
    },
    {
        "group": "wayland-9006c",
        "name": "wayland-2107-9006c",
        "sources": ["deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2107-wayland-kirin9006c-bugfix-limit main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kv main restricted universe multiverse"],
        "preferences": [],
    },
    {
        "group": "wayland-9006c",
        "name": "wayland-2203-9006c",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2203-wayland-bugfix-limit main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2203-wayland-kirin9006c-bugfix-limit main", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kirin9006C-feature main", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-wayland-2203-updates main universe restricted multiverse", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "wayland-9006c",
        "name": "wayland-2303-9006c",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-wayland-2303-updates main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kirin9006C-2303-feature main", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-bugfix-limit main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-kirin9006c-bugfix-limit main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "wayland-9006c",
        "name": "wayland-2303-update2-9006c",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update3 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update3-kirin9006C main", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update2-bugfix-limit main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update2-kirin9006c-bugfix-limit main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "wayland-9006c",
        "name": "wayland-2403U2-9006c",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2 main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2-kirin9006C main", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-bugfix-limit main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-kirin9006c-bugfix-limit main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "wayland-9006c",
        "name": "wayland-2503-9006c",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland main universe restricted multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2503-wayland-bugfix-limit main universe restricted multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland-kirin9006C main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland-kirin9006C-bugfix main universe restricted multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": ["Package: *", "Pin: origin \"archive.kylinos.cn\"", "Pin: release a=10.1-kylin", "Pin-Priority: 500", "Pin: release a=10.1-kylin-2503-wayland", "Pin-Priority: 600", "Pin: release a=10.1-2503-wayland-bugfix-limit", "Pin: release a=10.1-kylin-2503-wayland-kirin9006C", "Pin-Priority: 700", "Pin: release a=10.1-kylin-2503-wayland-kirin9006C-bugfix", "Pin: origin \"archive2.kylinos.cn\""],
    },
    {
        "group": "wayland-M900",
        "name": "wayland-2303-update2-M900",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update3 main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update3-m900 main", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update2-bugfix-limit main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2303-wayland-update2-kirinM900-bugfix-limit main", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "wayland-M900",
        "name": "wayland-2403U2-M900",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2 main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2-kirinM900 main", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-bugfix-limit main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-kirinM900-bugfix-limit main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "wayland-M900",
        "name": "wayland-2503-M900",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland main universe restricted multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2503-wayland-bugfix-limit main universe restricted multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland-kirinM900 main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland-kirinM900-bugfix main universe restricted multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": ["Package: *", "Pin: origin \"archive.kylinos.cn\"", "Pin: release a=10.1-kylin", "Pin-Priority: 500", "Pin: release a=10.1-kylin-2503-wayland", "Pin-Priority: 600", "Pin: release a=10.1-2503-wayland-bugfix-limit", "Pin: release a=10.1-kylin-2503-wayland-kirinM900", "Pin-Priority: 700", "Pin: release a=10.1-kylin-2503-wayland-kirinM900-bugfix", "Pin: origin \"archive2.kylinos.cn\""],
    },
    {
        "group": "wayland-9000C",
        "name": "wayland-2503-9000C",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin main restricted universe multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland main universe restricted multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2503-wayland-bugfix-limit main universe restricted multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland-kirin9000C main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kylin-2503-wayland-kirin9000C-bugfix main universe restricted multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": ["Package: *", "Pin: origin \"archive.kylinos.cn\"", "Pin: release a=10.1-kylin", "Pin-Priority: 500", "Pin: release a=10.1-kylin-2503-wayland", "Pin-Priority: 600", "Pin: release a=10.1-2503-wayland-bugfix-limit", "Pin: release a=10.1-kylin-2503-wayland-kirin9000C", "Pin-Priority: 700", "Pin: release a=10.1-kylin-2503-wayland-kirin9000C-bugfix", "Pin: origin \"archive2.kylinos.cn\""],
    },
    {
        "group": "华为",
        "name": "wayland 华为Pangux-a 2403",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kirin9000C-2403-feature-bugfix-limit main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kirin9000C-2403-feature main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-wayland-2403-updates main universe restricted multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": ["Package: *", "Pin: origin \"archive.kylinos.cn\"", "Pin: release a=10.1-kylin", "Pin-Priority: 500", "Pin: release a=10.1-wayland-2403-updates", "Pin: release a=10.1-kirin9000C-2403-feature-bugfix-limit", "Pin-Priority: 600", "Pin: release a=10.1-kirin9000C-2403-feature", "Pin: origin \"archive2.kylinos.cn\""],
    },
    {
        "group": "华为",
        "name": "wayland 华为Pangux-b",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kirin9000C-2403-feature-bugfix-limit main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kirin9000C-b-2403-feature main", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-wayland-2403-updates main universe restricted multiverse", "deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb http://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": ["Package: *", "Pin: origin \"archive.kylinos.cn\"", "Pin: release a=10.1-kylin", "Pin-Priority: 500", "Pin: release a=10.1-wayland-2403-updates", "Pin: release a=10.1-kirin9000C-2403-feature-bugfix-limit", "Pin-Priority: 600", "Pin: release a=10.1-kirin9000C-b-2403-feature", "Pin: origin \"archive2.kylinos.cn\""],
    },
    {
        "group": "华为",
        "name": "wayland 华为flemingx",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2-kirin9000C-pre-bugfix-limit main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2 main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2-kirin9000C-pre main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": ["Package: *", "Pin: origin \"archive.kylinos.cn\"", "Pin: release a=10.1-kylin", "Pin-Priority: 500", "Pin: release a=10.1-2403-wayland-update2", "Pin: release a=10.1-2403-wayland-update2-kirin9000C-pre", "Pin-Priority: 600", "Pin: release a= 10.1-2403-wayland-update2-kirin9000C-pre-bugfix-limit", "Pin: origin \"archive2.kylinos.cn\""],
    },
    {
        "group": "华为",
        "name": "wayland 华为panguy",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2-kirin9000X-bugfix-limit main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2 main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2-kirin9000X main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": ["Package: *", "Pin: origin \"archive.kylinos.cn\"", "Pin: release a=10.1-kylin", "Pin-Priority: 500", "Pin: release a=10.1-2403-wayland-update2", "Pin: release a=10.1-2403-wayland-update2-kirin9000X", "Pin-Priority: 600", "Pin: release a=10.1-2403-wayland-update2-kirin9000X-bugfix-limit", "Pin: origin \"archive2.kylinos.cn\""],
    },
    {
        "group": "华为",
        "name": "wayland 华为panguw 2107",
        "sources": ["deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-pw main restricted universe multiverse"],
        "preferences": [],
    },
    {
        "group": "华为",
        "name": "wayland 华为9000C 2403",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-wayland-2403-updates main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-kirin9000C-2403-feature main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "华为",
        "name": "wayland 华为9000C 2403-update1",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update1 main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update1-kirin9000C main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
    {
        "group": "华为",
        "name": "wayland 华为9000C 2403-update2",
        "sources": ["deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2 main universe restricted multiverse", "deb https://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2403-wayland-update2-kirin9000C main", "deb https://archive2.kylinos.cn/deb/kylin/production/PART-10_1-kirin9a0/custom/partner/10_1-kirin9a0 default all"],
        "preferences": [],
    },
]


# 组名（保持插入顺序）
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
    e = _BY_NAME.get(name)
    if not e:
        return ""
    return "\n".join(e["sources"]) + "\n"


def build_preferences_content(name):
    """返回该版本的 apt 优先级设置内容；无则返回 None。"""
    e = _BY_NAME.get(name)
    if not e or not e["preferences"]:
        return None
    return "\n".join(e["preferences"]) + "\n"
