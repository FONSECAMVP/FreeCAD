"""FreeCAD AI Addon — REQ-028: check deps at load, degrade gracefully."""

_MISSING: list[str] = []

try:
    import openai  # noqa: F401

    # DEC-012: must run after openai import, before any openai response is parsed
    from . import _compat  # noqa: F401
except ImportError:
    _MISSING.append("openai")

try:
    import keyring  # noqa: F401
except ImportError:
    _MISSING.append("keyring")

DEPS_OK = len(_MISSING) == 0

if not DEPS_OK:
    try:
        import FreeCAD

        FreeCAD.Console.PrintWarning(
            f"[AI Addon] Missing dependencies: {', '.join(_MISSING)}.\n"
            f"Install via: pip install {' '.join(_MISSING)}\n"
            "Chat panel disabled until dependencies are installed.\n"
        )
    except ImportError:
        pass
