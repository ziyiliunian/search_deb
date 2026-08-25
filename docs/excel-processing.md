# Excel 软件源数据处理逻辑

本文说明 `主线版本对应源地址.xlsx` 如何转换为程序使用的 `src/data_models.py`。

## 1. 使用的工作表

转换脚本只读取名称精确为 **`外网源`** 的工作表，不依赖工作表序号，因此即使 Excel 中存在 `外网源-old`、`命名规则`、`工作表2`，也不会误读旧数据或说明数据。

- `外网源`：当前生效的软件源数据，参与生成
- `外网源-old`：旧版历史数据，不参与生成
- `命名规则`：人工说明，不参与生成
- `工作表2`：构建信息，不参与生成

## 2. 表格结构

新版 `外网源` 工作表主要使用两列：

| 列 | 含义 |
|---|---|
| A 列 | 版本名称，例如 `XC-2503`、`HWE-2403U2`、`wayland-2503-990` |
| B 列 | 多行软件源和 apt preferences 配置 |

如果 A 列为空、B 列有内容，则该行视为上一个版本条目的续行。这样可以支持一个版本的软件源跨多个 Excel 行保存。

表头、产品线标题（例如 `HWE`、`wayland`）、说明文字和空行不会写入数据模型。

## 3. B 列内容分类

脚本逐行读取 B 列内容，并按前缀分类：

### 软件源 `sources`

以下前缀的行写入条目的 `sources`：

```text
deb ...
deb-src ...
```

### apt 优先级 `preferences`

以下前缀的行写入条目的 `preferences`：

```text
Package:
Pin:
Pin-Priority:
```

例如 Excel 中：

```text
deb http://archive.kylinos.cn/... 10.1-kylin main ...
优先级设置【/etc/apt/preferences.d/kylin.pref文件】
Package: *
Pin: origin "archive.kylinos.cn"
Pin-Priority: 500
```

生成结果中，说明文字会被忽略，`deb` 行进入 `sources`，其余三类配置行进入 `preferences`。

## 4. 产品线分类规则

脚本根据版本名称自动生成 `group`：

| 版本名称规则 | group |
|---|---|
| `XC-*` | `XC` |
| `HWE-PP-*` | `HWE-PP` |
| `HWE-*` | `HWE` |
| `wayland-*-990` | `wayland-990` |
| `wayland-*-9006c` | `wayland-9006c` |
| `wayland-*-M900` | `wayland-M900` |
| `wayland-*-9000C` | `wayland-9000C` |
| `wayland 华为*` | `华为` |

若新增名称无法匹配上述规则，脚本会报错并停止，避免静默生成错误分类。

## 5. 生成方法

在项目根目录运行：

```bash
python3 tools/excel_to_data_models.py
```

默认行为等价于：

```bash
python3 tools/excel_to_data_models.py \
  主线版本对应源地址.xlsx \
  --sheet 外网源 \
  --output src/data_models.py
```

转换脚本仅使用 Python 标准库（`zipfile` + XML 解析），不依赖 `openpyxl`。

## 6. 生成前后的校验

脚本会检查：

1. Excel 中是否存在 `外网源` 工作表
2. 是否读取到至少一个版本条目
3. 版本名称是否重复
4. 每个版本是否至少包含一条 `deb` 或 `deb-src` 源
5. 产品线名称是否能正确分类

生成后建议执行：

```bash
python3 -m compileall -q src
python3 -c "from src import data_models as d; print(len(d.VERSION_ENTRIES))"
```

本次更新后的 Excel 共生成 **41 个版本条目**，包括新增的 `XC-2303U2`、`XC-2403U2`。

## 7. 维护要求

- 软件源变更应优先修改 Excel，再运行转换脚本
- 不建议直接手工修改 `src/data_models.py` 中的 `VERSION_ENTRIES`
- Excel 中应保持版本名称唯一
- 软件源必须保持完整的一行 `deb ...` 格式
- preferences 配置必须分别以 `Package:`、`Pin:`、`Pin-Priority:` 开头
- 新增产品线命名规则时，应同步修改 `tools/excel_to_data_models.py` 的 `_classify_group()`
