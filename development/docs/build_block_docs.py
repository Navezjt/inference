import os
import re
from collections import defaultdict
from typing import List, Optional, Tuple

from inference.enterprise.workflows.entities.steps import OutputDefinition
from inference.enterprise.workflows.execution_engine.compiler.blocks_loader import (
    describe_available_blocks,
)

BLOCK_DOCUMENTATION_FILE = os.path.join(os.getcwd(), "docs", "workflows", "blocks.md")
BLOCK_DOCUMENTATION_DIRECTORY = os.path.join(os.getcwd(), "docs", "workflows", "blocks")
AUTOGENERATED_BLOCKS_LIST_TOKEN = "<!--- AUTOGENERATED_BLOCKS_LIST -->"

USER_CONFIGURATION_HEADER = [
    "| **Name** | **Type** | **Description** | Refs |",
    "|:---------|:---------|:----------------|:-----|",
]

BLOCK_DOCUMENTATION_TEMPLATE = """
# {class_name}

{description}

## Properties

{block_inputs}

## Available Connections

Check what blocks you can connect to `{class_name}`.

- inputs: {input_connections}
- outputs: {output_connections}

The available connections depend on its binding kinds. Check what binding kinds 
`{class_name}` has.

??? tip "Bindings"

    - input
    
{block_input_bindings}

    - output
    
{block_output_bindings}
"""

BLOCK_CARD_TEMPLATE = '<p class="card block-card" data-url="{data_url}" data-name="{data_name}" data-desc="{data_desc}" data-labels="{data_labels}" data-author="{data_authors}"></p>'


def read_lines_from_file(path: str) -> List[str]:
    with open(path) as file:
        return [line.rstrip() for line in file]


def save_lines_to_file(path: str, lines: List[str]) -> None:
    with open(path, "w") as f:
        for line in lines:
            f.write("%s\n" % line)


def search_lines_with_token(lines: List[str], token: str) -> List[int]:
    result = []
    for line_index, line in enumerate(lines):
        if token in line:
            result.append(line_index)
    return result


def camel_to_snake(name: str) -> str:
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def block_class_name_to_block_title(name: str) -> str:
    words = re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", name)

    if words[-1] == "Block":
        words.pop()

    return " ".join(words)


TYPE_MAPPING = {
    "number": "float",
    "integer": "int",
    "boolean": "bool",
    "string": "str",
    "null": "None",
}


def get_input_bindings(block_definition: dict) -> List[Tuple[str, str, str]]:
    global_result = []
    properties = block_definition["properties"]
    for property_name, property_definition in properties.items():
        if property_name == "type":
            continue
        if property_definition.get("type") in TYPE_MAPPING:
            continue
        if "items" in property_definition:
            if "reference" in property_definition["items"]:
                t_name = format_kinds_string(
                    property_definition["items"].get("kind", [])
                )
                global_result.append(
                    (
                        property_name,
                        f"List[{t_name}]",
                        property_definition.get("description", "not available"),
                    )
                )
                continue
            t_name = create_array_typing_for_bindings(property_definition["items"])
            if t_name is not None:
                global_result.append(
                    (
                        property_name,
                        t_name,
                        property_definition.get("description", "not available"),
                    )
                )
            continue
        if (
            "anyOf" in property_definition
            or "oneOf" in property_definition
            or "allOf" in property_definition
        ):
            x = (
                property_definition.get("anyOf", [])
                + property_definition.get("oneOf", [])
                + property_definition.get("allOf", [])
            )
            non_primitive_types = [e for e in x if "reference" in e]
            if len(non_primitive_types) == 0:
                continue
            all_kinds = []
            for t in non_primitive_types:
                all_kinds.extend(t.get("kind", []))
            result_str = format_kinds_string(all_kinds)
            global_result.append(
                (
                    property_name,
                    result_str,
                    property_definition.get("description", "not available"),
                )
            )
        if "reference" in property_definition:
            global_result.append(
                (
                    property_name,
                    format_kinds_string(property_definition.get("kind", [])),
                    property_definition.get("description", "not available"),
                )
            )
            continue
    return global_result


def create_array_typing_for_bindings(array_definition: dict) -> Optional[str]:
    x = (
        array_definition.get("anyOf", [])
        + array_definition.get("oneOf", [])
        + array_definition.get("allOf", [])
    )
    non_primitive_types = [e for e in x if "reference" in e]
    if len(non_primitive_types) == 0:
        return None
    all_kinds = []
    for t in non_primitive_types:
        all_kinds.extend(t.get("kind", []))
    return format_kinds_string(all_kinds)


def format_kinds_string(kind_definition: list) -> str:
    result = [k["name"] for k in kind_definition]
    if len(result) == 0:
        return "step"
    if len(result) > 1:
        result = ", ".join(set(result))
        return f"Union[{result}]"
    return result[0]


def format_inputs(block_definition: dict) -> List[Tuple[str, str, str, bool]]:
    global_result = []
    properties = block_definition["properties"]
    for property_name, property_definition in properties.items():
        if property_name == "type":
            continue
        if property_definition.get("type") in TYPE_MAPPING:
            result = TYPE_MAPPING[property_definition["type"]]
            global_result.append(
                (
                    property_name,
                    result,
                    property_definition.get("description", "not available"),
                    False,
                )
            )
            continue
        if "items" in property_definition:
            if "reference" in property_definition["items"]:
                continue
            t_name, ref_appears = create_array_typing(property_definition["items"])
            global_result.append(
                (
                    property_name,
                    t_name,
                    property_definition.get("description", "not available"),
                    ref_appears,
                )
            )
            continue
        if (
            "anyOf" in property_definition
            or "oneOf" in property_definition
            or "allOf" in property_definition
        ):
            x = (
                property_definition.get("anyOf", [])
                + property_definition.get("oneOf", [])
                + property_definition.get("allOf", [])
            )
            primitive_types = [e for e in x if "reference" not in e]
            if len(primitive_types) == 0:
                continue
            ref_appears = len(primitive_types) != len(x)
            result = []
            for t in primitive_types:
                if "$ref" in t:
                    t_name = t["$ref"].split("/")[-1]
                elif t["type"] in TYPE_MAPPING:
                    t_name = TYPE_MAPPING[t["type"]]
                elif t["type"] == "array":
                    t_name, ref_appears_nested = create_array_typing(t)
                    ref_appears = ref_appears or ref_appears_nested
                else:
                    t_name = "unknown"
                result.append(t_name)
            result = set(result)
            if "None" in result:
                high_level_type = "Optional"
                result.remove("None")
            else:
                high_level_type = "Union"
            result_str = ", ".join(list(result))
            if len(primitive_types) > 1:
                result_str = f"{high_level_type}[{result_str}]"
            global_result.append(
                (
                    property_name,
                    result_str,
                    property_definition.get("description", "not available"),
                    ref_appears,
                )
            )
        if "reference" in property_definition:
            continue
    return global_result


def create_array_typing(array_definition: dict) -> Tuple[str, bool]:
    ref_appears = False
    high_level_type = (
        "Set" if array_definition.get("uniqueItems", False) is True else "List"
    )
    if len(array_definition.get("items", [])) == 0:
        return f"{high_level_type}[Any]", ref_appears
    if "type" in array_definition["items"]:
        if "reference" in array_definition["items"]:
            ref_appears = True
        if "$ref" in array_definition["items"]["type"]:
            t_name = array_definition["items"]["type"]["$ref"].split("/")[-1]
        elif array_definition["items"]["type"] in TYPE_MAPPING:
            t_name = TYPE_MAPPING[array_definition["items"]["type"]]
        elif array_definition["items"]["type"] == "array":
            t_name = create_array_typing(array_definition["items"]["type"])
        else:
            t_name = "unknown"
        return f"{high_level_type}[{t_name}]", ref_appears


def format_block_inputs(outputs_manifest: dict) -> str:
    data = format_inputs(outputs_manifest)
    rows = []
    for name, kind, description, ref_appear in data:
        rows.append(
            f"| `{name}` | `{kind}` | {description}. | {'✅' if ref_appear else '❌'} |"
        )

    return "\n".join(USER_CONFIGURATION_HEADER + rows)


def format_input_bindings(block_definition: dict) -> str:
    data = get_input_bindings(block_definition)
    rows = []
    for name, kind, description in data:
        rows.append(f"        - `{name}` (`{kind}`): {description}.")
    return "\n".join(rows)


def format_block_outputs(outputs_manifest: List[OutputDefinition]) -> str:
    rows = []

    for output in outputs_manifest:
        if len(output.kind) == 1:
            kind = output.kind[0].name
            description = output.kind[0].description
            rows.append(f"        - `{output.name}` (`{kind}`): {description}.")
        else:
            kind = ", ".join([k.name for k in output.kind])
            description = " or ".join(
                [f"{k.description} if `{k.name}`" for k in output.kind]
            )
            rows.append(f"        - `{output.name}` (`Union[{kind}]`): {description}.")

    return "\n".join(rows)


def get_class_name(fully_qualified_name: str) -> str:
    return fully_qualified_name.split(".")[-1]


def create_directory_if_not_exists(directory_path: str) -> None:
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def get_references_for_blocks(description) -> list:
    result = []
    for block in description["blocks"]:
        block_title = get_class_name(block["fully_qualified_class_name"])
        for property_name, property_definition in block["block_manifest"][
            "properties"
        ].items():
            union_elements = property_definition.get("anyOf", [property_definition])
            for element in union_elements:
                if not element.get("reference", False):
                    continue
                result.append(
                    (
                        block_title,
                        property_name,
                        element["selected_element"],
                        [e["name"] for e in element.get("kind", [])],
                    )
                )
    return result


def get_outputs_for_blocks(description) -> list:
    result = []
    for block in description["blocks"]:
        block_title = get_class_name(block["fully_qualified_class_name"])
        for output in block["outputs_manifest"]:
            result.append((block_title, output["name"], output["kind"]))
    return result


def get_allowed_connections(
    start_block: str,
    blocks_references: list,
    blocks_outputs: list,
) -> list:
    kind_major_step_output_references = defaultdict(list)
    for block_type, field_name, selected_element, kind in blocks_references:
        if selected_element != "step_output":
            continue
        for k in kind:
            kind_major_step_output_references[k].append((block_type, field_name))
    result = []
    for output in blocks_outputs:
        if output[0] != start_block:
            continue
        start_block_output_name = output[1]
        for kind in output[2]:
            considered_matches = kind_major_step_output_references.get(
                kind["name"], []
            ) + kind_major_step_output_references.get("*", [])
            for block_type, field_name in considered_matches:
                if field_name == "*":
                    continue
                result.append(
                    (start_block, start_block_output_name, block_type, field_name)
                )
    return list(set(result))


def describe_block(blocks_references, blocks_outputs, block_description):
    block_data = {}

    block_manifest = block_description["block_manifest"]
    output_manifest = block_description["outputs_manifest"]

    block_data["name"] = get_class_name(block_description["fully_qualified_class_name"])
    block_data["inputs"] = []
    for property_name, property_description in block_manifest["properties"].items():
        block_data["inputs"].append(property_name)

    block_data["outputs"] = []
    for output in output_manifest:
        block_data["outputs"].append(output["name"])

    allowed_connections = get_allowed_connections(
        get_class_name(block_description["fully_qualified_class_name"]),
        blocks_references=blocks_references,
        blocks_outputs=blocks_outputs,
    )
    block_data["connections"] = [connection[2] for connection in allowed_connections]
    return block_data


def compile_compatible_blocks(blocks_references, blocks_outputs, blocks_descriptions):
    input_blocks = {}
    output_blocks = {}

    for block in blocks_descriptions.blocks:
        block_data = describe_block(blocks_references, blocks_outputs, block.dict())
        block_name = get_class_name(block.dict()["fully_qualified_class_name"])

        for compatible_output_block in block_data["connections"]:
            if compatible_output_block not in input_blocks:
                input_blocks[compatible_output_block] = []
            if block_name not in output_blocks:
                output_blocks[block_name] = []

            input_blocks[compatible_output_block].append(block_name)
            output_blocks[block_name].append(compatible_output_block)

    for k, v in input_blocks.items():
        input_blocks[k] = list(set(v))

    for k, v in output_blocks.items():
        output_blocks[k] = list(set(v))

    return input_blocks, output_blocks


def format_block_connections(connections: List[str]) -> str:
    if not connections:
        return "None"

    connections = [
        f"[`{connection}`](/workflows/blocks/{camel_to_snake(connection)})"
        for connection in connections
    ]

    return ", ".join(connections)


create_directory_if_not_exists(BLOCK_DOCUMENTATION_DIRECTORY)

lines = read_lines_from_file(path=BLOCK_DOCUMENTATION_FILE)
lines_with_token_indexes = search_lines_with_token(
    lines=lines, token=AUTOGENERATED_BLOCKS_LIST_TOKEN
)

if len(lines_with_token_indexes) != 2:
    raise Exception(
        f"Please inject two {AUTOGENERATED_BLOCKS_LIST_TOKEN} "
        f"tokens to signal start and end of autogenerated table."
    )

[start_index, end_index] = lines_with_token_indexes

block_card_lines = []

blocks_descriptions = describe_available_blocks()
blocks_references = get_references_for_blocks(blocks_descriptions.dict())
blocks_outputs = get_outputs_for_blocks(blocks_descriptions.dict())
compatible_input_blocks, compatible_output_blocks = compile_compatible_blocks(
    blocks_references, blocks_outputs, blocks_descriptions
)

for block in describe_available_blocks().blocks:
    block_class_name = get_class_name(block.fully_qualified_class_name)
    block_type = block.block_manifest.get("block_type", "").upper()
    block_license = block.block_manifest.get("license", "").upper()

    short_description = block.block_manifest.get("short_description", "")
    long_description = block.block_manifest.get("long_description", "")

    documentation_file_name = camel_to_snake(block_class_name) + ".md"
    documentation_file_path = os.path.join(
        BLOCK_DOCUMENTATION_DIRECTORY, documentation_file_name
    )
    documentation_content = BLOCK_DOCUMENTATION_TEMPLATE.format(
        class_name=block_class_name,
        description=long_description,
        block_inputs=format_block_inputs(block.block_manifest),
        block_input_bindings=format_input_bindings(block.block_manifest),
        block_output_bindings=format_block_outputs(block.outputs_manifest),
        input_connections=format_block_connections(
            compatible_input_blocks.get(block_class_name)
        ),
        output_connections=format_block_connections(
            compatible_output_blocks.get(block_class_name)
        ),
    )
    with open(documentation_file_path, "w") as documentation_file:
        documentation_file.write(documentation_content)

    block_card_line = BLOCK_CARD_TEMPLATE.format(
        data_url=camel_to_snake(block_class_name),
        data_name=block_class_name_to_block_title(block_class_name),
        data_desc=short_description,
        data_labels=", ".join([block_type, block_license]),
        data_authors="",
    )
    block_card_lines.append(block_card_line)

lines = lines[: start_index + 1] + block_card_lines + lines[end_index:]
save_lines_to_file(path=BLOCK_DOCUMENTATION_FILE, lines=lines)
