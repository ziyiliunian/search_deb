# -*- coding: utf-8 -*-
"""主窗口 GUI（PyQt5）。

通过 data_models 读取软件源配置、apt_core 构建命令、runner 异步执行，
支持按架构 + 产品线 + 版本选择，以及按文件名 / 库名搜索软件包。
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import (
    QAbstractItemView, QComboBox, QFileDialog, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow, QMessageBox,
    QPlainTextEdit, QPushButton, QSizePolicy, QSplitter, QVBoxLayout, QWidget,
)

from . import APP_TITLE, apt_core, data_models
from .runner import CommandWorker
from .utils import get_desktop_path


class SearchListWidget(QListWidget):
    """带空态背景提示的搜索结果列表：无内容时居中显示提示文字。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._placeholder = ""

    def set_placeholder(self, text):
        self._placeholder = text
        self.viewport().update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.count() == 0 and self._placeholder:
            painter = QPainter(self.viewport())
            painter.setPen(QColor(140, 140, 140))
            rect = self.viewport().rect().adjusted(16, 16, -16, -16)
            painter.drawText(
                rect, Qt.AlignCenter | Qt.TextWordWrap, self._placeholder
            )
            painter.end()


class MainWindow(QMainWindow):
    # 搜索结果框空态背景文案
    PLACEHOLDER_DEFAULT = "输入文件名或库名后点击「搜索」"
    PLACEHOLDER_SEARCHING = "正在搜索 ..."
    PLACEHOLDER_NOT_FOUND = (
        "未找到匹配的软件包\n\n"
        "建议安装 apt-file 获得精确的文件→包反查：\n"
        "sudo apt-get install apt-file\n"
        "安装后点击「更新文件索引」按钮"
    )
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1000, 820)

        self.download_dir = get_desktop_path()
        self.apt = apt_core.AptManager(data_models.SOURCE_FILE, data_models.PREF_FILE)
        self._worker = None
        self._busy = False
        self._search_kw = ""

        self._build_ui()
        self._update_groups()

    # ===================== UI 构建 =====================
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)

        tip = QLabel("选架构 → 选产品线/版本 → 启用版本源 → 查询下载（下载无需 sudo）")
        tip.setStyleSheet("color: green; font-weight: bold;")
        root.addWidget(tip)

        form = QFormLayout()

        self.arch_combo = QComboBox()
        for key in data_models.ARCHITECTURES:
            self.arch_combo.addItem(data_models.ARCH_LABELS.get(key, key), key)
        self.arch_combo.currentIndexChanged.connect(self._on_arch_changed)
        form.addRow("目标架构：", self.arch_combo)

        self.group_combo = QComboBox()
        self.group_combo.currentTextChanged.connect(self._update_versions)
        form.addRow("产品线：", self.group_combo)

        self.version_combo = QComboBox()
        form.addRow("系统版本：", self.version_combo)

        self.pkg_edit = QLineEdit()
        self.pkg_edit.setPlaceholderText("输入软件包名称")
        form.addRow("软件包名称：", self.pkg_edit)

        self.pkg_version_combo = QComboBox()
        form.addRow("可用包版本：", self.pkg_version_combo)

        dir_row = QHBoxLayout()
        self.dir_edit = QLineEdit(self.download_dir)
        self.dir_edit.setReadOnly(True)
        browse_btn = QPushButton("选择目录")
        browse_btn.clicked.connect(self.select_dir)
        dir_row.addWidget(self.dir_edit)
        dir_row.addWidget(browse_btn)
        form.addRow("下载目录：", dir_row)

        root.addLayout(form)

        # 功能按钮
        btn_row = QHBoxLayout()
        self.btn_enable_arch = QPushButton("启用目标架构")
        self.btn_enable_arch.clicked.connect(self.enable_target_arch)
        self.btn_enable_source = QPushButton("启用选中版本源")
        self.btn_enable_source.clicked.connect(self.enable_version_source)
        self.btn_query = QPushButton("查询版本")
        self.btn_query.clicked.connect(self.query_arch_version)
        self.btn_download = QPushButton("下载选中版本")
        self.btn_download.clicked.connect(self.download_selected_version)
        self.btn_clear = QPushButton("清空")
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_restore = QPushButton("恢复默认源")
        self.btn_restore.clicked.connect(self.restore_default_source)
        for b in (self.btn_enable_arch, self.btn_enable_source, self.btn_query,
                  self.btn_download, self.btn_clear, self.btn_restore):
            btn_row.addWidget(b)
        self._action_buttons = [self.btn_enable_arch, self.btn_enable_source,
                                self.btn_query, self.btn_download, self.btn_restore]
        root.addLayout(btn_row)

        # 按文件名 / 库名搜索
        search_box = QGroupBox("按文件名 / 库名搜索（apt-file，无结果时回退 apt-cache）")
        search_v = QVBoxLayout(search_box)
        search_row = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("例如：libBLT.2.5.so.8.6、libssl.so.3 或库名关键词")
        self.search_edit.returnPressed.connect(self.search_files)
        self.btn_search = QPushButton("搜索")
        self.btn_search.clicked.connect(self.search_files)
        self.btn_use_pkg = QPushButton("使用选中包查询版本")
        self.btn_use_pkg.clicked.connect(self.use_selected_package)
        self.btn_update_index = QPushButton("更新文件索引")
        self.btn_update_index.setToolTip("更新 apt-file 文件索引（需要管理员权限），搜索不到文件时先点这里")
        self.btn_update_index.clicked.connect(self.update_file_index)
        search_row.addWidget(self.search_edit)
        search_row.addWidget(self.btn_search)
        search_row.addWidget(self.btn_use_pkg)
        search_row.addWidget(self.btn_update_index)
        search_v.addLayout(search_row)
        self.search_list = SearchListWidget()
        self.search_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.search_list.set_placeholder(self.PLACEHOLDER_DEFAULT)
        search_v.addWidget(self.search_list, 1)
        search_box.setMinimumHeight(160)
        search_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # 日志区容器
        log_container = QWidget()
        log_v = QVBoxLayout(log_container)
        log_v.setContentsMargins(0, 0, 0, 0)
        log_v.addWidget(QLabel("运行日志："))
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumBlockCount(5000)
        log_v.addWidget(self.log_box, 1)
        log_container.setMinimumHeight(120)

        # 搜索区与日志区放入垂直分割条：随窗口自动伸缩，中间可拖动调整比例
        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(search_box)
        splitter.addWidget(log_container)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, 1)

    # ===================== 下拉联动 =====================
    def _update_groups(self):
        arch = self.arch_combo.currentData()
        current = self.group_combo.currentText()

        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        self.group_combo.addItems(data_models.available_groups(arch))
        idx = self.group_combo.findText(current)
        if idx >= 0:
            self.group_combo.setCurrentIndex(idx)
        self.group_combo.blockSignals(False)

        self._update_versions()

    def _update_versions(self):
        arch = self.arch_combo.currentData()
        group = self.group_combo.currentText()
        avail = set(data_models.available_versions(arch))
        current = self.version_combo.currentText()

        versions = [v for v in data_models.versions_of_group(group) if v in avail] if group else []

        self.version_combo.blockSignals(True)
        self.version_combo.clear()
        self.version_combo.addItems(versions)
        idx = self.version_combo.findText(current)
        if idx >= 0:
            self.version_combo.setCurrentIndex(idx)
        self.version_combo.blockSignals(False)

    def _on_arch_changed(self, index):
        self._update_groups()
        self.log("已切换架构：{}，版本列表已更新".format(self.arch_combo.currentText()))

    # ===================== 通用工具 =====================
    def log(self, msg):
        self.log_box.appendPlainText(msg)
        sb = self.log_box.verticalScrollBar()
        sb.setValue(sb.maximum())

    def set_busy(self, busy):
        self._busy = busy
        for b in self._action_buttons:
            b.setEnabled(not busy)
        self.btn_search.setEnabled(not busy)
        self.btn_use_pkg.setEnabled(not busy)
        self.btn_update_index.setEnabled(not busy)

    def select_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择下载目录", self.download_dir)
        if d:
            self.download_dir = d
            self.dir_edit.setText(d)

    def clear_all(self):
        self.log_box.clear()
        self.pkg_version_combo.clear()
        self.search_list.clear()
        self.search_list.set_placeholder(self.PLACEHOLDER_DEFAULT)

    # ===================== 异步执行封装 =====================
    def run_single(self, cmd, privileged, callback):
        """执行单条命令，完成后回调 callback(code, output)。"""
        self.set_busy(True)
        self._worker = CommandWorker(cmd, self.download_dir, privileged, self)
        self._worker.line_ready.connect(self.log)

        def _done(code, output):
            self.set_busy(False)
            callback(code, output)

        self._worker.finished.connect(_done)
        self._worker.start()

    def run_steps(self, steps, on_done, stop_on_error=True):
        """顺序执行多条命令，完成后回调 on_done(ok, results)。"""
        results = []

        def run_next(i):
            if i >= len(steps):
                self.set_busy(False)
                on_done(all(c == 0 for c in results), results)
                return
            cmd, priv = steps[i]
            self.set_busy(True)
            self._worker = CommandWorker(cmd, self.download_dir, priv, self)
            self._worker.line_ready.connect(self.log)

            def _done(code, output):
                results.append(code)
                if stop_on_error and code != 0:
                    self.set_busy(False)
                    on_done(False, results)
                    return
                run_next(i + 1)

            self._worker.finished.connect(_done)
            self._worker.start()

        run_next(0)

    # ===================== 1. 启用目标架构 =====================
    def enable_target_arch(self):
        if self._busy:
            return
        arch_label = self.arch_combo.currentText()
        dpkg_arch = data_models.dpkg_arch_of(self.arch_combo.currentData())
        if QMessageBox.question(
            self, "确认", "将启用 {} 架构支持\n需要输入管理员密码，是否继续？".format(arch_label)
        ) != QMessageBox.Yes:
            return

        self.log("=" * 60)
        self.log("正在启用 {} 架构支持...".format(arch_label))
        self.log("=" * 60)

        def done(code, output):
            if code == 0:
                self.log("\n✅ {} 架构已启用，建议点击「启用选中版本源」刷新索引".format(arch_label))
            else:
                self.log("❌ 添加架构失败，请检查密码是否正确")
            self.log("=" * 60)

        self.run_single(self.apt.enable_arch_cmd(dpkg_arch), True, done)

    # ===================== 2. 启用选中版本源（核心） =====================
    def enable_version_source(self):
        if self._busy:
            return
        name = self.version_combo.currentText()
        if not name or not data_models.get_entry(name):
            QMessageBox.warning(self, "提示", "请选择有效的系统版本")
            return
        if QMessageBox.question(
            self, "确认",
            "将切换为【{}】软件源\n覆盖文件：{}\n自动刷新源索引，是否继续？".format(
                name, data_models.SOURCE_FILE
            ),
        ) != QMessageBox.Yes:
            return

        self.log("=" * 60)
        self.log("正在切换到【{}】软件源...".format(name))
        self.log("=" * 60)

        content = data_models.build_sources_content(name)
        pref = data_models.build_preferences_content(name)

        steps = [(self.apt.write_source_cmd(content), True)]
        if pref:
            steps.append((self.apt.write_pref_cmd(pref), True))
        else:
            steps.append((self.apt.remove_pref_cmd(), True))
        steps.append((self.apt.apt_update_cmd(), True))

        # stop_on_error=False：逐步独立判断结果，避免误报成功
        def done(ok, results):
            # steps: [写源, 写/清优先级, apt update]，results 与之一一对应
            if not results or results[0] != 0:
                self.log("❌ 写入源文件失败")
                self.log("=" * 60)
                return
            self.log("\n✅ 源文件已写入")

            if pref:
                if len(results) > 1 and results[1] == 0:
                    self.log("✅ 优先级设置已写入 {}".format(data_models.PREF_FILE))
                else:
                    self.log("❌ 优先级设置写入失败")
            elif len(results) > 1 and results[1] != 0:
                self.log("⚠️ 清理旧优先级文件失败（可忽略）")

            self.log("当前生效源：")
            for line in content.splitlines():
                self.log("  " + line)

            update_code = results[-1] if results else -1
            if update_code == 0:
                self.log("\n✅ 【{}】源已启用，索引刷新完成".format(name))
            else:
                self.log("\n⚠️ 源文件已写入，但索引刷新未完成，可稍后手动执行 sudo apt update")
            self.log("=" * 60)

        self.run_steps(steps, done, stop_on_error=False)

    # ===================== 3. 恢复系统默认源 =====================
    def restore_default_source(self):
        if self._busy:
            return
        if QMessageBox.question(
            self, "确认", "将删除工具生成的源文件与优先级文件，恢复系统默认源状态，是否继续？"
        ) != QMessageBox.Yes:
            return

        self.log("=" * 60)
        self.log("正在恢复系统默认源...")
        self.log("=" * 60)

        steps = [
            (self.apt.remove_source_cmd(), True),
            (self.apt.remove_pref_cmd(), True),
            (self.apt.apt_update_cmd(), True),
        ]

        def done(ok, results):
            self.log("✅ 已删除工具生成的源文件与优先级文件")
            self.log("\n✅ 已恢复系统默认源状态")
            self.log("=" * 60)

        self.run_steps(steps, done, stop_on_error=False)

    # ===================== 4. 查询包版本 =====================
    def query_arch_version(self):
        if self._busy:
            return
        pkg = self.pkg_edit.text().strip()
        arch_label = self.arch_combo.currentText()
        dpkg_arch = data_models.dpkg_arch_of(self.arch_combo.currentData())
        name = self.version_combo.currentText()

        if not pkg:
            QMessageBox.warning(self, "提示", "请输入包名")
            return

        self.log_box.clear()
        self.pkg_version_combo.clear()
        self.log("=" * 60)
        self.log("查询 {} 【{}】架构 【{}】下的版本".format(pkg, arch_label, name))
        self.log("=" * 60)

        def done(code, output):
            versions = apt_core.AptManager.parse_versions(output)
            if not versions:
                self.log("\n❌ 无可用版本")
                self.log("💡 请确认：1.已启用对应架构 2.已点击「启用选中版本源」并刷新成功")
                self.log("=" * 60)
                return
            self.pkg_version_combo.clear()
            self.pkg_version_combo.addItems(versions)
            self.pkg_version_combo.setCurrentIndex(0)
            self.log("\n" + "=" * 60)
            self.log("✅ 找到 {} 个版本：".format(len(versions)))
            for v in versions:
                self.log("  - " + v)
            self.log("=" * 60)

        self.run_single(self.apt.policy_cmd(pkg, dpkg_arch), False, done)

    # ===================== 5. 下载包 =====================
    def download_selected_version(self):
        if self._busy:
            return
        pkg = self.pkg_edit.text().strip()
        dpkg_arch = data_models.dpkg_arch_of(self.arch_combo.currentData())
        ver = self.pkg_version_combo.currentText().strip()

        if not all([pkg, dpkg_arch, ver]):
            QMessageBox.warning(self, "提示", "请先查询并选择版本")
            return

        self.log("\n" + "=" * 60)
        self.log("下载：{}:{}={}".format(pkg, dpkg_arch, ver))
        self.log("保存目录：{}".format(self.download_dir))
        self.log("=" * 60)

        def done(code, output):
            if code == 0:
                self.log("\n✅ 下载成功！")
                self.run_single(
                    "ls -lh -- *.deb 2>/dev/null || echo '（下载目录中暂无 .deb 文件）'",
                    False, lambda c, o: self.log(o),
                )
            else:
                self.log("\n❌ 下载失败，请检查版本号与架构是否匹配")
            self.log("=" * 60)

        self.run_single(self.apt.download_cmd(pkg, dpkg_arch, ver), False, done)

    # ===================== 6. 按文件名 / 库名搜索 =====================
    def search_files(self):
        if self._busy:
            return
        kw = self.search_edit.text().strip()
        if not kw:
            QMessageBox.warning(self, "提示", "请输入文件名或库名")
            return
        self._search_kw = kw
        self.search_list.clear()
        self.search_list.set_placeholder(self.PLACEHOLDER_SEARCHING)
        self.log("=" * 60)
        self.log("按文件/库名搜索：{}".format(kw))
        self.log("=" * 60)
        # 按当前选择的目标架构搜索（跨架构下载场景），并记录以便失败时降级
        self._apt_file_with_arch = True
        dpkg_arch = data_models.dpkg_arch_of(self.arch_combo.currentData())
        self.run_single(
            self.apt.apt_file_search_cmd(kw, dpkg_arch), False, self._on_apt_file_done
        )

    def _on_apt_file_done(self, code, output):
        # 仅命令成功时才解析输出，避免把错误信息误识别为包名
        pkgs = apt_core.AptManager.parse_search_packages(output) if code == 0 else []
        if pkgs:
            self._show_search_results(pkgs)
            return

        if code != 0:
            # 老版本 apt-file 不支持 --architecture：降级为不带架构重试一次
            if getattr(self, "_apt_file_with_arch", False):
                self._apt_file_with_arch = False
                self.run_single(
                    self.apt.apt_file_search_cmd(self._search_kw),
                    False, self._on_apt_file_done,
                )
                return
            lower = output.lower()
            if code == 127 or "not found" in lower:
                self.search_list.set_placeholder(
                    "建议安装 apt-file 以获得精确的文件→包反查：\n\n"
                    "sudo apt-get install apt-file\n\n"
                    "安装后点击「更新文件索引」按钮，再重新搜索"
                )
                self.log("⚠️ 未安装 apt-file，可执行：sudo apt-get install apt-file")
            elif "cache is empty" in lower or "apt-file update" in lower:
                self.search_list.set_placeholder(
                    "apt-file 索引为空\n\n请点击「更新文件索引」按钮\n或执行：sudo apt-file update"
                )
                self.log("⚠️ apt-file 索引为空，可点击「更新文件索引」或执行：sudo apt-file update")
            else:
                self.log("⚠️ apt-file 搜索失败（返回码 {}）".format(code))

        self.log("回退 apt-cache search，尝试提取的关键词 ...")
        self._fallback_terms = (
            apt_core.AptManager.extract_search_terms(self._search_kw) or [self._search_kw]
        )
        self._fallback_idx = 0
        self._fallback_pkgs = []
        self._run_next_fallback()

    def _run_next_fallback(self):
        if self._fallback_idx >= len(self._fallback_terms):
            self._show_search_results(self._fallback_pkgs)
            return
        term = self._fallback_terms[self._fallback_idx]
        self.log("尝试关键词：{}".format(term))
        self.run_single(self.apt.apt_cache_search_cmd(term), False, self._on_fallback_done)

    def _on_fallback_done(self, code, output):
        if code == 0:
            term = self._fallback_terms[self._fallback_idx].lower()
            for p in apt_core.AptManager.parse_search_packages(output):
                # 仅保留包名含关键词的结果，过滤描述匹配引入的噪音
                if term in p.lower() and p not in self._fallback_pkgs:
                    self._fallback_pkgs.append(p)
        # 已有结果或关键词用尽则停止，避免更宽泛的关键词引入大量无关包
        if self._fallback_pkgs or self._fallback_idx + 1 >= len(self._fallback_terms):
            self._show_search_results(self._fallback_pkgs)
            return
        self._fallback_idx += 1
        self._run_next_fallback()

    def update_file_index(self):
        """一键更新 apt-file 文件索引（需要管理员权限）。"""
        if self._busy:
            return
        self.log("=" * 60)
        self.log("正在更新 apt-file 文件索引（可能需要几分钟）...")
        self.log("=" * 60)
        self.run_single("apt-file update", True, self._on_update_index_done)

    def _on_update_index_done(self, code, output):
        if code == 0:
            self.log("\n✅ 文件索引更新完成，可重新搜索")
        else:
            self.log("\n❌ 文件索引更新失败，可手动执行 sudo apt-file update")

    def _show_search_results(self, pkgs):
        self.search_list.clear()
        if not pkgs:
            self.search_list.set_placeholder(self.PLACEHOLDER_NOT_FOUND)
            self.log("\n❌ 未找到匹配的软件包")
            self.log("💡 提示：apt-file 需先执行 `apt-file update` 建立文件索引；也可尝试更短的关键词")
            return
        self.search_list.set_placeholder("")
        self.search_list.addItems(pkgs)
        self.log("\n✅ 找到 {} 个候选包：".format(len(pkgs)))
        for p in pkgs:
            self.log("  - " + p)
        self.log("选中后点击「使用选中包查询版本」")

    def use_selected_package(self):
        items = self.search_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "提示", "请先在搜索结果中选择一个包")
            return
        pkg = items[0].text()
        self.pkg_edit.setText(pkg)
        self.log("已选择包名：{}，正在查询版本...".format(pkg))
        self.query_arch_version()

    # ===================== 关闭处理 =====================
    def closeEvent(self, event):
        """关闭窗口前回收后台线程，避免 QThread 销毁崩溃。"""
        worker = self._worker
        if worker is not None and worker.isRunning():
            self.log("正在停止后台任务...")
            worker.terminate()
            worker.wait(3000)
        event.accept()
