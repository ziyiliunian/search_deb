# KylinPkgTool 代码审查报告

## 项目概述

- **用途**：银河麒麟 V10 多架构软件包下载 GUI 工具（PyQt5）
- **工作流**：选择架构 → 选择产品线/系统版本 → 启用目标架构 → 写入工具专属 `/etc/apt/sources.list.d/kylinpkgtool.list`（+ `/etc/apt/preferences.d/kylinpkgtool.pref`）→ `apt update` → `apt-cache policy` 查版本 → `apt download` 下载包或依赖包或依赖
- **附加功能**：`apt-file`/`apt-cache` 按文件名/库名反查包
- **执行模型**：`CommandWorker`(QThread) + `pkexec` 提权，命令经 `shell=True` 执行
- **打包**：`pack.py` / `build.sh` 生成 deb（源码直接拷贝到 `/opt/kylinpkgtool`）

---

## 恶性 Bug（高风险，建议优先修复）

### 1. 命令注入：`policy_cmd` / `download_cmd` 未转义用户输入的包名
文件：`src/apt_core.py:37-41`

```python
def policy_cmd(self, pkg, arch):
    return "apt-cache policy {}:{}".format(pkg, arch)

def download_cmd(self, pkg, arch, version):
    return "apt download {}:{}={}".format(pkg, arch, version)
```

`pkg` 直接来自 GUI 输入框 `pkg_edit`（`main_window.py:331, 368`），而同一文件中 `apt_file_search_cmd`/`apt_cache_search_cmd` 都用了 `shlex.quote`，唯独这两处没有。由于 `runner.py:27` 用 `shell=True` 执行，输入如 `libssl3;touch ~/evil` 或 `$(malicious)` 会被 shell 解释，导致以当前用户权限执行任意命令。
**修复**：对 `pkg`、`arch`、`version` 统一做 `shlex.quote`（或改用列表参数、去掉 `shell=True`）。

### 2. 「启用选中版本源」成功/失败状态误报
文件：`src/main_window.py:277-297`

```python
if results and results[0] != 0:
    ...
    return
self.log("\n✅ 源文件已写入")
if pref:
    self.log("✅ 优先级设置已写入 ...")          # 错误点 A
...
update_code = results[-1] if results else 0
if update_code == 0:
    self.log("\n✅ ... 索引刷新完成")            # 错误点 B
```

`run_steps(steps, done)` 默认 `stop_on_error=True`：
- **错误点 A**：若第 1 步写源成功（0）、第 2 步写 preferences 失败（非 0），流程在步骤 2 提前停止，但 `results[0]==0` 使代码进入 `if pref:` 分支，仍打印「✅ 优先级设置已写入」——实际写入失败，误导用户。
- **错误点 B**：同一场景下 `results[-1]` 是步骤 2 的失败码，打印的是「⚠️ 刷新完成，个别源警告可忽略」，而 `apt update` 根本没执行。用户会误以为索引已刷新，随后查询/下载失败时无从排查。
- 附带问题：`on_done(ok, results)` 的 `ok` 参数在 `done` 中完全未使用，与 `results` 手动判断逻辑不一致。
**修复**：按 `results[i]` 与步骤一一对应判断每步结果，未执行的步骤不要输出成功提示；未执行 `apt update` 时不要报「刷新完成」。

### 3. 窗口关闭时后台 QThread 未回收，可能崩溃或悬挂
文件：`src/runner.py` + `src/main_window.py`

`MainWindow` 没有 `closeEvent` 处理，`self._worker` 线程在 `apt update`、`pkexec` 认证等长时间任务运行时若用户直接关窗，Qt 会报 `QThread: Destroyed while thread is still running`，极端情况下程序崩溃；同时 `pkexec` 弹出的认证进程可能残留。
**修复**：在 `closeEvent` 中设置取消标志并 `worker.wait()`（或 `terminate()` + `wait()`），再接受关闭。

---

## 中等问题

### 4. 桌面目录不存在时，所有命令全部失败
文件：`src/utils.py:21-26`。若 `xdg-user-dir` 不可用且 `~/桌面`、`~/Desktop` 都不存在，回退返回 `~/桌面`（可能不存在）。`CommandWorker` 用 `cwd=` 启动进程会抛 `No such file or directory`，被捕获为 `code=-1`，导致所有下载/查询功能不可用。
**修复**：目录不存在时 `os.makedirs` 或回退到 `home`。

### 5. `parse_versions` 过滤规则可能漏掉合法版本
文件：`src/apt_core.py:60`。`if not ver.isdigit() and "." in ver` 会排除不含 `.` 的版本（如纯数字日期版本 `20240101`），`ver.isdigit()` 判断本身也无必要。
**修复**：直接校验版本号非空且不重复即可。

### 6. preferences 数据：部分 2503/华为条目 Pin 段落缺 `Pin-Priority`
文件：`src/data_models.py:80, 116` 等。末尾 `Pin: release a=10.1-2503-bugfix-limit` 后直接跟 `Pin: origin "archive2.kylinos.cn"`，属于同一段落，apt 会将其 OR 合并并应用前一个 Pin-Priority（600），`archive2` 的优先级可能不符合预期。属数据生成问题（来源 Excel），建议核对。
另外 `"Pin-Priority:600"`（`data_models.py:116`）与 `"Pin-Priority: 600"` 写法不统一（解析虽合法，但建议统一）。

### 7. 下载成功后的 `ls -lh *.deb` 在无文件时报错
文件：`src/main_window.py:384`。若目标目录下无 `.deb`（例如下载到别的名称或失败残留），`ls` 非零退出，错误信息会被打印到日志，但不影响功能。

### 8. heredoc 写法对内容中含单引号脆弱
文件：`src/apt_core.py:18-26`。`bash -c 'cat > ... <<"KYLIN_EOF"...'` 外层用单引号包裹，若未来 sources/preferences 内容含 `'` 会破坏整条命令。当前内置数据仅含双引号，暂安全。

---

## 良性观察（非 bug）

- `restore_default_source` 使用 `stop_on_error=False` 且 `done` 忽略 `ok`，行为符合预期（尽力清理）。
- `apt-file` 未安装时命令返回 127、输出为空，会正确回退 `apt-cache search`。
- `parse_search_packages` 对 apt-cache 描述中含 `": "` 的行可能切分错误（极小概率，且仅影响搜索结果展示）。
- `build.sh` / `pack.py` 逻辑正确；`pack.py` 在 Windows 下 zip 内路径可能带 `\`，但目标环境是麒麟 Linux，可忽略。

---

## 结论

项目整体结构清晰、职责划分合理，核心功能（多架构切换、源管理、下载）设计可用。最需要优先修复的是 **3 个恶性问题：命令注入（#1）、源启用状态误报（#2）、线程关闭崩溃（#3）**，其中 #1 属安全缺陷、#2 直接影响用户对系统源状态判断、#3 影响稳定性。
