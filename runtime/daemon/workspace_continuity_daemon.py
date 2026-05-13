from __future__ import annotations

import ast
import json
import logging
import os
import re
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Deque, Dict, List, Optional, Set, Tuple

from ..session.workspace_runtime_session import WorkspaceRuntimeSession
from ...topology.compaction.compact_context_builder import CompactContextBuilder

# Keep watchdog imports at module scope so nested handlers can always resolve.
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    FileSystemEventHandler = None
    Observer = None

LOG = logging.getLogger(__name__)

HARD_EXCLUDED_DIRS = {
    "backup scripts",
    "backups",
    "archive",
    "archived",
    "old",
    "tmp",
    "temp",
    "__pycache__",
    ".git",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
}

ENTRYPOINT_CANDIDATES = (
    "main_app.py",
    "Qt/main_app.py",
    "run_qt.py",
)


@dataclass
class WorkspaceContinuityDaemon:
    """
    Persistent runtime-local continuity cache daemon.

    PECS v2 correction:
    - runtime-reachable topology only
    - deterministic entrypoint reconstruction
    - compact continuity outputs
    - no workspace-wide archival indexing
    """

    workspace_root: Path
    runtime_session: WorkspaceRuntimeSession
    compact_builder: CompactContextBuilder
    watch_pattern: str = "*.py"
    artifact_dir_name: str = ".pecs"
    monitor_recursive: bool = True

    artifact_dir: Path = field(init=False)
    observer: Optional[object] = field(default=None, init=False)
    current_changes: Set[Path] = field(default_factory=set, init=False)
    pid_file_name: str = "daemon.pid"

    runtime_reachable_files: Set[Path] = field(default_factory=set, init=False)
    runtime_locality_payload: Dict[str, Dict[str, object]] = field(
        default_factory=dict, init=False
    )
    runtime_topology_edges: List[Dict[str, str]] = field(
        default_factory=list, init=False
    )

    def __post_init__(self) -> None:
        self.workspace_root = self.workspace_root.resolve()
        self.artifact_dir = self.workspace_root / self.artifact_dir_name
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

        if not self.workspace_root.exists():
            raise FileNotFoundError(
                f"Workspace root does not exist: {self.workspace_root}"
            )

    def start(self) -> None:
        """Start live filesystem monitoring and artifact regeneration."""
        if FileSystemEventHandler is None or Observer is None:
            raise ImportError(
                "watchdog is required for the daemon. "
                "Install it with `pip3 install watchdog`."
            )

        self._write_pid_file()

        try:
            self._write_health_state()
        except Exception:
            pass

        self._chat_history_path = self.workspace_root / ".pecs" / "ai_chat_history.json"
        self._last_chat_history_mtime = None
        if self._chat_history_path.exists():
            self._last_chat_history_mtime = self._chat_history_path.stat().st_mtime

        if self._should_full_scan():
            self._clean_core_artifacts()
            self._rebuild_runtime_topology()

        class ChangeHandler(FileSystemEventHandler):
            def __init__(self, daemon: WorkspaceContinuityDaemon) -> None:
                self.daemon = daemon

            def on_created(self, event):
                self._handle(event)

            def on_modified(self, event):
                self._handle(event)

            def on_moved(self, event):
                if event.is_directory:
                    return
                self._handle(event)

            def on_deleted(self, event):
                if event.is_directory:
                    return
                self._handle(event)

            def _handle(self, event) -> None:
                if event.is_directory:
                    return

                path = Path(
                    event.dest_path if hasattr(event, "dest_path") else event.src_path
                )
                if self.daemon._is_monitored_file(path):
                    self.daemon._record_change(path)

        handler = ChangeHandler(self)
        observer = Observer()
        observer.schedule(
            handler, str(self.workspace_root), recursive=self.monitor_recursive
        )

        self.observer = observer
        observer.start()

        message = (
            f"PECS daemon started for {self.workspace_root}. "
            "Do not close this terminal."
        )
        print(message)
        LOG.info(message)

        try:
            if not self.runtime_locality_payload:
                self._rebuild_runtime_topology()

            while True:
                self._poll_chat_history()
                time.sleep(1.0)
        except KeyboardInterrupt:
            LOG.info("PECS daemon interrupted, stopping")
        finally:
            observer.stop()
            observer.join()
            self._remove_pid_file()

    def stop(self) -> None:
        if self.observer is not None:
            try:
                self.observer.stop()
                self.observer.join()
            except Exception:
                pass

    def _should_full_scan(self) -> bool:
        compact_bundle = self.artifact_dir / "compact_bundle.json"
        locality_index = self.artifact_dir / "locality_index.json"

        for path in [compact_bundle, locality_index]:
            if not path.exists():
                return True
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return True

            if not data:
                return True

            if path.name == "compact_bundle.json":
                if data.get("context_count", 0) == 0:
                    return True

            if path.name == "locality_index.json" and len(data) == 0:
                return True

        return False

    def _clean_core_artifacts(self) -> None:
        for name in [
            "locality_index.json",
            "topology_compact.json",
            "compact_bundle.json",
            "active_context.json",
            "session_context.json",
        ]:
            path = self.artifact_dir / name
            try:
                if path.exists():
                    path.unlink()
            except OSError as exc:
                LOG.warning("Failed to remove core PECS artifact %s: %s", path, exc)

    def _record_change(self, file_path: Path) -> None:
        file_path = file_path.resolve()
        self.current_changes.add(file_path)
        self._process_changes()

    def _process_changes(self) -> None:
        if not self.current_changes:
            return

        changed_files = sorted(self.current_changes)
        self.current_changes.clear()

        if self._chat_history_path in changed_files:
            self._on_chat_history_update()

        python_changed_files = [p for p in changed_files if p.suffix == ".py"]
        if not python_changed_files:
            return

        # Rebuild from runtime topology roots (entrypoints), not filesystem-wide inventory.
        self._rebuild_runtime_topology(changed_files=python_changed_files)

    def _rebuild_runtime_topology(
        self,
        changed_files: Optional[List[Path]] = None,
    ) -> None:
        entrypoints = self._discover_entrypoints()
        reachable_files = self._resolve_runtime_reachable_files(entrypoints)
        self._populate_runtime_indexes(reachable_files)

        focus = self._infer_active_focus_from_chat()
        compact_bundle = self._build_compact_bundle(focus)
        active_context = self._build_active_context_payload(focus, compact_bundle)
        topology_payload = {
            "entrypoints": [self._pecs_id_from_path(p) for p in entrypoints],
            "edges": self.runtime_topology_edges,
            "edge_count": len(self.runtime_topology_edges),
        }

        self._write_json("locality_index.json", self.runtime_locality_payload)
        self._write_json("topology_compact.json", topology_payload)
        self._write_json("compact_bundle.json", compact_bundle)
        self._write_json("active_context.json", active_context)
        self._write_json(
            "session_context.json",
            {
                "workspace_root": str(self.workspace_root),
                "active_objects": sorted(self.runtime_session.active_objects),
                "active_paths": sorted(self.runtime_session.active_paths),
                "active_topology_zone": focus.get("active_topology_zone"),
                "current_issue": focus.get("current_issue"),
            },
        )
        self._write_json(
            "daemon_state.json",
            {
                "workspace_root": str(self.workspace_root),
                "artifact_dir": str(self.artifact_dir),
                "changed_files": [str(path) for path in (changed_files or [])],
                "runtime_reachable_count": len(self.runtime_reachable_files),
            },
        )

    def _discover_entrypoints(self) -> List[Path]:
        entrypoints: List[Path] = []
        for relative in ENTRYPOINT_CANDIDATES:
            path = (self.workspace_root / relative).resolve()
            if path.exists() and path.suffix == ".py":
                entrypoints.append(path)

        if entrypoints:
            return entrypoints

        fallback = self.workspace_root / "main.py"
        if fallback.exists():
            return [fallback.resolve()]

        return []

    def _resolve_runtime_reachable_files(self, entrypoints: List[Path]) -> Set[Path]:
        reachable: Set[Path] = set()
        queue: Deque[Path] = deque(entrypoints)

        while queue:
            path = queue.popleft().resolve()

            if path in reachable:
                continue
            if not path.exists() or path.suffix != ".py":
                continue
            if self._is_hard_excluded(path):
                continue

            reachable.add(path)

            for target in self._extract_local_import_targets(path):
                if target not in reachable:
                    queue.append(target)

        return reachable

    def _extract_local_import_targets(self, path: Path) -> Set[Path]:
        targets: Set[Path] = set()

        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
        except Exception:
            return targets

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    resolved = self._resolve_module_to_path(alias.name, path, 0)
                    if resolved is not None:
                        targets.add(resolved)

            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                base = self._resolve_module_to_path(module, path, node.level)
                if base is not None:
                    targets.add(base)

                for alias in node.names:
                    if alias.name == "*":
                        continue
                    symbol_module = f"{module}.{alias.name}" if module else alias.name
                    resolved = self._resolve_module_to_path(
                        symbol_module, path, node.level
                    )
                    if resolved is not None:
                        targets.add(resolved)

        for match in re.findall(
            r"['\"]([A-Za-z_][\w]*(?:\.[A-Za-z_][\w]*)+)['\"]", source
        ):
            resolved = self._resolve_module_to_path(match, path, 0)
            if resolved is not None:
                targets.add(resolved)

        return targets

    def _resolve_module_to_path(
        self,
        module: str,
        current_file: Path,
        level: int,
    ) -> Optional[Path]:
        module = module.strip(".")

        if level > 0:
            current_rel_parent = current_file.relative_to(self.workspace_root).parent
            base_parts = list(current_rel_parent.parts)
            trim = max(0, level - 1)
            if trim > 0:
                base_parts = base_parts[:-trim] if trim <= len(base_parts) else []
            module_parts = module.split(".") if module else []
            candidate = self._resolve_parts_to_file(base_parts + module_parts)
            if candidate is not None:
                return candidate

        if module:
            candidate = self._resolve_parts_to_file(module.split("."))
            if candidate is not None:
                return candidate

        return None

    def _resolve_parts_to_file(self, parts: List[str]) -> Optional[Path]:
        if not parts:
            return None

        module_path = self.workspace_root.joinpath(*parts)

        direct = module_path.with_suffix(".py")
        if direct.exists() and not self._is_hard_excluded(direct):
            return direct.resolve()

        init_file = module_path / "__init__.py"
        if init_file.exists() and not self._is_hard_excluded(init_file):
            return init_file.resolve()

        return None

    def _populate_runtime_indexes(self, reachable_files: Set[Path]) -> None:
        self.runtime_reachable_files = set(reachable_files)
        self.runtime_locality_payload.clear()
        self.runtime_topology_edges = []

        self.runtime_session.locality_index.object_locality.clear()
        self.runtime_session.locality_index.runtime_locality.clear()
        self.runtime_session.locality_index.ownership_locality.clear()
        self.runtime_session.execution_index.execution_paths.clear()
        self.runtime_session.execution_index.execution_chains.clear()
        self.runtime_session.graph_index.node_index.clear()
        self.runtime_session.graph_index.edge_index.clear()
        self.runtime_session.graph_index.zone_index.clear()
        self.runtime_session.topology_retriever.ownership_index.ownership_locality.clear()
        self.runtime_session.active_objects.clear()
        self.runtime_session.active_paths.clear()
        self.runtime_session.clear_context_cache()

        edge_seen: Set[Tuple[str, str, str]] = set()

        for path in sorted(reachable_files):
            object_id = self._object_id_from_path(path)
            path_id = self._path_id_from_path(path)
            pecs_id = self._pecs_id_from_path(path)

            class_name, method_name = self._extract_symbol_metadata(path)
            runtime_zone = self._runtime_zone_for_path(path)

            self.runtime_locality_payload[pecs_id] = {
                "file": str(path.relative_to(self.workspace_root)),
                "class": class_name,
                "method": method_name,
                "runtime_zone": runtime_zone,
            }

            anchors = [pecs_id]
            if class_name:
                anchors.append(f"{pecs_id}.{class_name}")
            if method_name:
                anchors.append(f"{pecs_id}.{method_name}")

            self.runtime_session.locality_index.register_object_locality(
                object_id, anchors
            )
            self.runtime_session.locality_index.runtime_locality[path_id] = anchors
            self.runtime_session.locality_index.ownership_locality[object_id] = anchors
            self.runtime_session.execution_index.register_execution_path(
                path_id, anchors
            )
            self.runtime_session.execution_index.register_execution_chain(
                f"{path_id}.chain", anchors
            )
            self.runtime_session.graph_index.register_node(
                object_id,
                {
                    "object_id": object_id,
                    "path": str(path.relative_to(self.workspace_root)),
                    "runtime_zone": runtime_zone,
                },
            )
            self.runtime_session.graph_index.register_zone(runtime_zone, [object_id])
            self.runtime_session.topology_retriever.ownership_index.register_ownership_locality(
                object_id,
                anchors,
            )
            self.runtime_session.active_objects.add(object_id)
            self.runtime_session.active_paths.add(path_id)

            for edge in self._extract_runtime_edges(path):
                key = (edge["from"], edge["to"], edge["type"])
                if key in edge_seen:
                    continue
                edge_seen.add(key)
                self.runtime_topology_edges.append(edge)

    def _extract_runtime_edges(self, path: Path) -> List[Dict[str, str]]:
        edges: List[Dict[str, str]] = []
        source_id = self._pecs_id_from_path(path)

        for target in self._extract_local_import_targets(path):
            edges.append(
                {
                    "from": source_id,
                    "to": self._pecs_id_from_path(target),
                    "type": "import",
                }
            )

        source = ""
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return edges

        for action_var in re.findall(r"\b(\w+)\s*=\s*QAction\s*\(", source):
            edges.append(
                {
                    "from": source_id,
                    "to": f"PECS_ID:action.{action_var}",
                    "type": "qaction_register",
                }
            )

        for action_var, method_name in re.findall(
            r"\b(\w+)\.triggered\.connect\(\s*self\.(\w+)\s*\)",
            source,
        ):
            edges.append(
                {
                    "from": f"PECS_ID:action.{action_var}",
                    "to": f"{source_id}.{method_name}",
                    "type": "signal_slot",
                }
            )

        for method_name in re.findall(
            r"\b(?:open|launch|show)_([A-Za-z_][\w]*)\s*\(", source
        ):
            edges.append(
                {
                    "from": source_id,
                    "to": f"PECS_ID:dialog.{method_name}",
                    "type": "dialog_launch",
                }
            )

        for method_name in re.findall(r"\bsubprocess\.(?:run|Popen)\s*\(", source):
            edges.append(
                {
                    "from": source_id,
                    "to": "PECS_ID:subprocess.launch",
                    "type": "subprocess_launch",
                }
            )

        return edges

    def _extract_symbol_metadata(self, path: Path) -> Tuple[str, str]:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            return "", ""

        class_name = ""
        method_name = ""

        for node in ast.walk(tree):
            if not class_name and isinstance(node, ast.ClassDef):
                class_name = node.name
            if not method_name and isinstance(node, ast.FunctionDef):
                method_name = node.name
            if class_name and method_name:
                break

        return class_name, method_name

    def _runtime_zone_for_path(self, path: Path) -> str:
        rel = str(path.relative_to(self.workspace_root)).lower()
        if "overlay" in rel:
            return "overlay_pipeline"
        if "dialog" in rel:
            return "dialog_pipeline"
        if "viewer" in rel:
            return "viewer_pipeline"
        if "qaction" in rel or "toolbar" in rel or "menu" in rel:
            return "action_pipeline"
        if "subprocess" in rel:
            return "subprocess_pipeline"
        if "dispatch" in rel:
            return "dispatch_pipeline"
        if "runtime" in rel:
            return "runtime_pipeline"
        return "general_runtime"

    def _infer_active_focus_from_chat(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "current_issue": "",
            "active_topology_zone": "general_runtime",
            "dissatisfaction_signals": [],
            "rejected_edits": [],
            "focus_terms": [],
        }

        if not self._chat_history_path.exists():
            return payload

        try:
            chat = json.loads(self._chat_history_path.read_text(encoding="utf-8"))
        except Exception:
            return payload

        if not isinstance(chat, list) or not chat:
            return payload

        recent = chat[-30:]
        messages: List[str] = []
        for entry in recent:
            if not isinstance(entry, dict):
                continue
            text = entry.get("message", "")
            if not text and isinstance(entry.get("messages"), list):
                chunks = [
                    m.get("content", "")
                    for m in entry.get("messages", [])
                    if isinstance(m, dict)
                ]
                text = " ".join(chunk for chunk in chunks if chunk)
            if text:
                messages.append(str(text))

        if not messages:
            return payload

        payload["current_issue"] = messages[-1][:300]

        joined = " ".join(messages).lower()
        dissatisfaction = []
        for token in [
            "not working",
            "wrong",
            "error",
            "failed",
            "broken",
            "regression",
            "drift",
        ]:
            if token in joined:
                dissatisfaction.append(token)

        rejected = []
        for token in ["do not", "don't", "avoid", "revert", "not this"]:
            if token in joined:
                rejected.append(token)

        zone_keywords = {
            "overlay_pipeline": ["overlay", "band", "wireframe"],
            "dialog_pipeline": ["dialog", "wizard", "popup"],
            "viewer_pipeline": ["viewer", "pdf", "canvas"],
            "action_pipeline": ["qaction", "toolbar", "menu", "shortcut"],
            "subprocess_pipeline": ["subprocess", "runner", "process"],
            "dispatch_pipeline": ["dispatch", "signal", "slot", "callback"],
        }

        chosen_zone = "general_runtime"
        for zone, terms in zone_keywords.items():
            if any(term in joined for term in terms):
                chosen_zone = zone
                break

        focus_terms = re.findall(
            r"[a-zA-Z_][a-zA-Z0-9_]{3,}", payload["current_issue"].lower()
        )

        payload["active_topology_zone"] = chosen_zone
        payload["dissatisfaction_signals"] = dissatisfaction
        payload["rejected_edits"] = rejected
        payload["focus_terms"] = sorted(set(focus_terms))[:16]
        return payload

    def _build_compact_bundle(self, focus: Dict[str, object]) -> Dict[str, object]:
        focus_terms = set(focus.get("focus_terms", []))
        active_zone = str(focus.get("active_topology_zone", "general_runtime"))

        scored: List[Tuple[int, str, Dict[str, object]]] = []
        for pecs_id, meta in self.runtime_locality_payload.items():
            score = 0
            runtime_zone = str(meta.get("runtime_zone", ""))
            file_name = str(meta.get("file", "")).lower()

            if runtime_zone == active_zone:
                score += 5

            for term in focus_terms:
                if term in file_name or term in pecs_id.lower():
                    score += 2

            if score > 0:
                scored.append((score, pecs_id, meta))

        scored.sort(key=lambda item: (-item[0], item[1]))

        selected = (
            scored[:50]
            if scored
            else [
                (0, k, v) for k, v in sorted(self.runtime_locality_payload.items())[:20]
            ]
        )

        bundle = []
        for score, pecs_id, meta in selected:
            bundle.append(
                {
                    "pecs_id": pecs_id,
                    "file": meta.get("file", ""),
                    "runtime_zone": meta.get("runtime_zone", "general_runtime"),
                    "score": score,
                }
            )

        return {
            "bundle": bundle,
            "context_count": len(bundle),
            "active_topology_zone": active_zone,
        }

    def _build_active_context_payload(
        self,
        focus: Dict[str, object],
        compact_bundle: Dict[str, object],
    ) -> Dict[str, object]:
        bundle_ids = [
            entry.get("pecs_id", "") for entry in compact_bundle.get("bundle", [])
        ]

        neighborhood = [
            edge
            for edge in self.runtime_topology_edges
            if edge.get("from") in bundle_ids or edge.get("to") in bundle_ids
        ][:120]

        return {
            "current_issue": focus.get("current_issue", ""),
            "active_topology_zone": focus.get(
                "active_topology_zone", "general_runtime"
            ),
            "recent_locality": bundle_ids[:25],
            "runtime_neighborhood": neighborhood,
            "dissatisfaction_signals": focus.get("dissatisfaction_signals", []),
            "rejected_edits": focus.get("rejected_edits", []),
        }

    def _poll_chat_history(self) -> None:
        if not self._chat_history_path.exists():
            return

        mtime = self._chat_history_path.stat().st_mtime
        if (
            self._last_chat_history_mtime is None
            or mtime > self._last_chat_history_mtime
        ):
            self._last_chat_history_mtime = mtime
            self._on_chat_history_update()

    def _on_chat_history_update(self) -> None:
        try:
            chat_data = json.loads(self._chat_history_path.read_text(encoding="utf-8"))
            self._write_json(
                "chat_history_state.json",
                {
                    "chat_entry_count": (
                        len(chat_data) if isinstance(chat_data, list) else 0
                    ),
                    "updated_at": time.time(),
                },
            )
        except Exception as exc:
            LOG.warning("Failed to load ai_chat_history.json: %s", exc)

        # Refresh only compact artifacts from chat focus without widening topology.
        if self.runtime_locality_payload:
            focus = self._infer_active_focus_from_chat()
            compact_bundle = self._build_compact_bundle(focus)
            active_context = self._build_active_context_payload(focus, compact_bundle)
            self._write_json("compact_bundle.json", compact_bundle)
            self._write_json("active_context.json", active_context)

    def _write_json(self, name: str, data: object) -> None:
        path = self.artifact_dir / name
        try:
            path.write_text(
                json.dumps(data, indent=2, sort_keys=True),
                encoding="utf-8",
            )
        except OSError as exc:
            LOG.warning("Failed to write PECS artifact %s: %s", path, exc)

    def _write_pid_file(self) -> None:
        pid_path = self.artifact_dir / self.pid_file_name
        try:
            pid_path.write_text(str(os.getpid()), encoding="utf-8")
        except OSError as exc:
            LOG.warning("Failed to write PECS daemon PID file: %s", exc)

    def _remove_pid_file(self) -> None:
        pid_path = self.artifact_dir / self.pid_file_name
        try:
            if pid_path.exists():
                pid_path.unlink()
        except OSError as exc:
            LOG.warning("Failed to remove PECS daemon PID file: %s", exc)

    def _write_health_state(self) -> None:
        self._write_json(
            "daemon_health.json",
            {
                "workspace_root": str(self.workspace_root),
                "artifact_dir": str(self.artifact_dir),
                "daemon_pid": os.getpid(),
                "started_at": time.time(),
            },
        )

    def _is_monitored_file(self, path: Path) -> bool:
        path = path.resolve()

        if path == self._chat_history_path:
            return True

        if path.suffix != ".py":
            return False

        if self._is_hard_excluded(path):
            return False

        return True

    def _is_hard_excluded(self, path: Path) -> bool:
        try:
            rel_parts = [
                part.lower() for part in path.relative_to(self.workspace_root).parts
            ]
        except ValueError:
            return True

        for part in rel_parts:
            if part in HARD_EXCLUDED_DIRS:
                return True

        return False

    def _pecs_id_from_path(self, path: Path) -> str:
        relative = path.relative_to(self.workspace_root)
        return f"PECS_ID:{'.'.join(relative.with_suffix('').parts)}"

    def _object_id_from_path(self, path: Path) -> str:
        relative = path.relative_to(self.workspace_root)
        return ".".join(relative.with_suffix("").parts)

    def _path_id_from_path(self, path: Path) -> str:
        return self._object_id_from_path(path)
