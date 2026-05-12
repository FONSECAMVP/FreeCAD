"""
AI Chat Panel — DES-008, REQ-002, REQ-011, REQ-012, REQ-015.

Qt import is deferred so this module is importable in headless mode.
All FreeCAD API calls happen in _on_tool_call_ready (main thread slot).
"""

from __future__ import annotations

import html
import json
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from freecad_ai.conversation import ConversationHistory
    from freecad_ai.executor import ToolExecutor
    from freecad_ai.llm_client import LLMClient
    from freecad_ai.preferences import AIPreferences
    from freecad_ai.registry import ToolRegistry

try:
    from PySide2.QtCore import QThread, Slot
    from PySide2.QtGui import QTextCursor
    from PySide2.QtWidgets import (
        QDockWidget,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QSizePolicy,
        QTextBrowser,
        QVBoxLayout,
        QWidget,
    )

    _QT_OK = True
except ImportError:
    try:
        from PySide6.QtCore import QThread, Slot
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import (
            QDockWidget,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPushButton,
            QSizePolicy,
            QTextBrowser,
            QVBoxLayout,
            QWidget,
        )

        _QT_OK = True
    except ImportError:
        _QT_OK = False

_STYLE_USER = "color:#1a73e8;font-weight:bold;"
_STYLE_ASSISTANT = "color:#202124;"
_STYLE_ERROR = "color:#d32f2f;font-style:italic;"
_STYLE_TOOL = "color:#555;font-size:11px;"
_STYLE_THINKING = "color:#999;font-style:italic;"

_TOOL_DETAIL_TMPL = (
    '<details style="{style}">'
    "<summary>tool: {name}</summary>"
    '<pre style="margin:2px 0 0 8px;">{args}</pre>'
    "</details>"
)


class AIChatPanel(QDockWidget if _QT_OK else object):  # type: ignore[misc]
    """Dockable chat panel. Requires Qt."""

    def __init__(
        self,
        registry: ToolRegistry,
        executor: ToolExecutor,
        history: ConversationHistory,
        make_client: Callable[[], LLMClient],
        prefs: AIPreferences,
        parent=None,
    ) -> None:
        if not _QT_OK:
            raise RuntimeError("Qt not available — cannot create AIChatPanel")
        super().__init__("AI Chat", parent)
        self._registry = registry
        self._executor = executor
        self._history = history
        self._make_client = make_client
        self._prefs = prefs
        self._worker: QThread | None = None
        self._pending_tool_results: list[dict] = []

        self._build_ui()
        self._connect_freecad_events()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._history_view = QTextBrowser()
        self._history_view.setOpenLinks(False)
        self._history_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self._history_view)

        self._thinking_label = QLabel("● Thinking…")
        self._thinking_label.setStyleSheet(_STYLE_THINKING)
        self._thinking_label.setVisible(False)
        layout.addWidget(self._thinking_label)

        input_row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("Describe what to design…")
        self._input.returnPressed.connect(self._on_send)
        input_row.addWidget(self._input)

        self._send_btn = QPushButton("Send")
        self._send_btn.clicked.connect(self._on_send)
        input_row.addWidget(self._send_btn)

        layout.addLayout(input_row)
        self.setWidget(container)

    def _connect_freecad_events(self) -> None:
        try:
            import FreeCADGui

            FreeCADGui.getMainWindow().workbenchActivated.connect(
                lambda _: self._executor.set_busy(False)
            )
        except Exception:
            pass

    # ------------------------------------------------------------------ Slots

    @Slot()
    def _on_send(self) -> None:
        text = self._input.text().strip()
        if not text or self._worker is not None:
            return

        if not self._prefs.is_configured:
            self._append_error("API key not set. Open Edit > Preferences > AI Addon.")
            return

        self._input.clear()
        self._append_user(text)

        from freecad_ai.context import build_context

        ctx = build_context()
        full_text = f"{ctx}\n{text}" if ctx else text
        self._history.add_user(full_text)

        self._set_busy(True)
        self._start_worker()

    def _start_worker(self) -> None:
        from freecad_ai.worker import LLMWorker

        if LLMWorker is None:
            self._append_error("Qt thread support unavailable.")
            self._set_busy(False)
            return

        client = self._make_client()
        messages = self._history.messages()
        tools = self._registry.get_tools_for_llm()

        self._worker = LLMWorker(client=client, messages=messages, tools=tools, parent=self)
        self._worker.token_received.connect(self._on_token)
        self._worker.tool_call_ready.connect(self._on_tool_call_ready)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    @Slot(str)
    def _on_token(self, token: str) -> None:
        self._append_assistant_token(token)

    @Slot(str, object)
    def _on_tool_call_ready(self, name: str, args: dict) -> None:
        # FreeCAD API called here — main thread only (DES-005)
        result = self._executor.dispatch(name, args)
        self._pending_tool_results.append({"name": name, "args": args, "result": result})
        self._append_tool_detail(name, args, result)

    @Slot()
    def _on_finished(self) -> None:
        # Add assistant turn + tool results to history
        self._history.add_assistant(content=None, tool_calls=None)
        for entry in self._pending_tool_results:
            self._history.add_tool_result(
                tool_call_id=entry["name"],
                content=json.dumps(entry["result"]),
            )
        self._pending_tool_results.clear()
        self._cleanup_worker()

    @Slot(str)
    def _on_error(self, message: str) -> None:
        self._append_error(message)
        self._cleanup_worker()

    def _cleanup_worker(self) -> None:
        if self._worker:
            self._worker.quit()
            self._worker.wait(2000)
            self._worker = None
        self._set_busy(False)

    # ------------------------------------------------------------------ HTML helpers

    def _append_user(self, text: str) -> None:
        self._history_view.append(f'<p style="{_STYLE_USER}">[You] {html.escape(text)}</p>')

    def _append_assistant_token(self, token: str) -> None:
        cursor = self._history_view.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(token)
        self._history_view.setTextCursor(cursor)
        self._history_view.ensureCursorVisible()

    def _append_tool_detail(self, name: str, args: dict, result: dict) -> None:
        args_str = html.escape(json.dumps(args, indent=2))
        block = _TOOL_DETAIL_TMPL.format(
            style=_STYLE_TOOL,
            name=html.escape(name),
            args=args_str,
        )
        self._history_view.append(block)

    def _append_error(self, message: str) -> None:
        self._history_view.append(f'<p style="{_STYLE_ERROR}">⚠ {html.escape(message)}</p>')

    # ------------------------------------------------------------------ State

    def _set_busy(self, busy: bool) -> None:
        self._send_btn.setEnabled(not busy)
        self._input.setEnabled(not busy)
        self._thinking_label.setVisible(busy)
        self._executor.set_busy(busy)
