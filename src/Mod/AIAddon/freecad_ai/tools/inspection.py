"""Model inspection tools — REQ-009. All FreeCAD imports lazy (REQ-019)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from freecad_ai.registry import ToolRegistry


def _make_schema(name: str, description: str, properties: dict, required: list) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }


def _handle_list_objects(args: dict) -> dict:
    import FreeCAD  # lazy

    doc = FreeCAD.ActiveDocument
    return {"objects": [{"label": o.Label, "type": o.TypeId} for o in doc.Objects]}


def _handle_get_object_properties(args: dict) -> dict:
    import FreeCAD  # lazy

    doc = FreeCAD.ActiveDocument
    label = args["label"]
    objs = doc.getObjectsByLabel(label)
    if not objs:
        return {"error": "execution", "message": f"Object '{label}' not found"}
    obj = objs[0]
    props = {}
    for prop in obj.PropertiesList:
        try:
            props[prop] = str(getattr(obj, prop))
        except Exception:
            props[prop] = "<unreadable>"
    return {"label": obj.Label, "type": obj.TypeId, "properties": props}


def _handle_get_selection(args: dict) -> dict:
    import FreeCADGui  # lazy

    sel = FreeCADGui.Selection.getSelection()
    return {"selection": [{"label": o.Label, "type": o.TypeId} for o in sel]}


def register_tools(registry: ToolRegistry) -> None:
    registry.register(
        "list_objects",
        _make_schema("list_objects", "List all objects in the active document.", {}, []),
        _handle_list_objects,
        workbench="Part",
    )
    registry.register(
        "get_object_properties",
        _make_schema(
            "get_object_properties",
            "Get all properties of a named object.",
            {"label": {"type": "string", "description": "Object label"}},
            ["label"],
        ),
        _handle_get_object_properties,
        workbench="Part",
    )
    registry.register(
        "get_selection",
        _make_schema("get_selection", "Get the currently selected objects.", {}, []),
        _handle_get_selection,
        workbench="Part",
    )
