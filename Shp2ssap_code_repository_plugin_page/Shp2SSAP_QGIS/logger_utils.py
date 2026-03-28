# -*- coding: utf-8 -*-
"""Minimal call logger for Shp2SSAP Suite QGIS plugin.

Writes a log file in the user's Downloads folder:
    ~/Downloads/qgis_plugin_log.txt

Keeps implementation small and resilient across QGIS/Qt signal signatures.
"""

from __future__ import annotations

import inspect
import logging
import os
from functools import wraps
from types import FunctionType
from typing import Any, Callable, Dict, Optional

_LOGGER_NAME = "Shp2SSAP_calls"
_logger = logging.getLogger(_LOGGER_NAME)
_logger.addHandler(logging.NullHandler())  # evita warning se non abilitato


def enable_file_logging(enabled: bool = True, log_dir: Optional[str] = None) -> None:
    """Abilita/disabilita il logging su file."""

    if not enabled:
        return

    if _logger.handlers and any(isinstance(h, logging.FileHandler) for h in _logger.handlers):
        return  # già inizializzato

    if log_dir is None:
        log_dir = os.path.join(os.path.expanduser("~"), "Downloads")

    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        return

    log_file = os.path.join(log_dir, "qgis_plugin_log.txt")

    _logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    _logger.addHandler(fh)
    _logger.propagate = False


def log_call(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that logs calls and tolerates extra Qt signal args.

    If the wrapped callable fails due to a mismatched signature (common with QAction
    signals passing a 'checked' bool), it retries dropping extra args.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            _logger.info(f"{func.__module__}.{func.__qualname__}")
        except Exception:
            pass

        # Be resilient to Qt signals adding extra positional args (e.g. clicked(bool)).
        # IMPORTANT: never mask exceptions coming from inside the wrapped function.
        try:
            sig = inspect.signature(func)
        except Exception:
            sig = None

        if sig is not None:
            params = list(sig.parameters.values())
            has_varargs = any(p.kind == p.VAR_POSITIONAL for p in params)
            if not has_varargs:
                max_pos = sum(
                    1 for p in params
                    if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                )
                if len(args) > max_pos:
                    args = args[:max_pos]

        return func(*args, **kwargs)

    return wrapper


def auto_log_methods(cls: type) -> type:
    """Class decorator: wraps all methods with log_call."""
    for name, method in inspect.getmembers(cls, inspect.isfunction):
        setattr(cls, name, log_call(method))
    return cls


def auto_log_module_functions(module_globals: Dict[str, Any]) -> None:
    """Wrap module-level functions in-place.

    Wraps public functions (no leading underscore).
    """
    for name, obj in list(module_globals.items()):
        if name.startswith("_"):
            continue
        if isinstance(obj, FunctionType):
            module_globals[name] = log_call(obj)
