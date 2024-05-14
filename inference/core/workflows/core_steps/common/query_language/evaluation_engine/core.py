from functools import partial
from typing import Any, Callable, Dict, List, Union

from inference.core.workflows.core_steps.common.query_language.entities.enums import (
    StatementsGroupsOperator,
)
from inference.core.workflows.core_steps.common.query_language.entities.operations import StaticOperand, DynamicOperand, \
    BinaryStatement, UnaryStatement, StatementGroup
from inference.core.workflows.core_steps.common.query_language.entities.types import (
    T,
    V,
)
from inference.core.workflows.core_steps.common.query_language.errors import (
    EvaluationEngineError,
)

BINARY_OPERATORS = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "(Number) >": lambda a, b: a > b,
    "(Number) >=": lambda a, b: a >= b,
    "(Number) <": lambda a, b: a < b,
    "(Number) <=": lambda a, b: a <= b,
    "(String) startsWith": lambda a, b: a.startswith(b),
    "(String) endsWith": lambda a, b: a.endswith(b),
    "(String) contains": lambda a, b: b in a,
    "in": lambda a, b: a in b,
}

UNARY_OPERATORS = {
    "Exists": lambda a: a is not None,
    "DoesNotExist": lambda a: a is None,
    "IsTrue": lambda a: a is True,
    "IsFalse": lambda a: a is False,
    "(Sequence) is empty": lambda a: len(a) == 0,
    "(Sequence) is not empty": lambda a: len(a) > 0,
}


def evaluate(values: dict, definition: dict) -> bool:
    parsed_definition = StatementGroup.model_validate(definition)
    eval_function = build_eval_function(parsed_definition)
    return eval_function(values)


def build_eval_function(
    definition: Union[BinaryStatement, UnaryStatement, StatementGroup],
) -> Callable[[T], bool]:
    if isinstance(definition, BinaryStatement):
        return build_binary_statement(definition)
    if isinstance(definition, UnaryStatement):
        return build_unary_statement(definition)
    statements_functions = []
    for statement in definition.statements:
        statements_functions.append(build_eval_function(statement))
    return partial(
        compound_eval,
        statements_functions=statements_functions,
        operator=definition.operator,
    )


def build_binary_statement(
    definition: BinaryStatement,
) -> Callable[[Dict[str, T]], bool]:
    operator = BINARY_OPERATORS[definition.comparator.type]
    left_operand_builder = create_operand_builder(definition=definition.left_operand)
    right_operand_builder = create_operand_builder(definition=definition.right_operand)
    return partial(
        binary_eval,
        left_operand_builder=left_operand_builder,
        operator=operator,
        right_operand_builder=right_operand_builder,
        negate=definition.negate,
        operation_type=definition.type,
    )


def create_operand_builder(
    definition: Union[StaticOperand, DynamicOperand]
) -> Callable[[Dict[str, T]], V]:
    if isinstance(definition, StaticOperand):
        return create_static_operand_builder(definition)
    return create_dynamic_operand_builder(definition)


def create_static_operand_builder(
    definition: StaticOperand,
) -> Callable[[Dict[str, T]], V]:
    # local import to avoid circular dependency of modules with operations and evaluation
    from inference.core.workflows.core_steps.common.query_language.operations.core import (
        build_operations_chain,
    )

    operations_fun = build_operations_chain(operations=definition.operations)
    return partial(
        static_operand_builder,
        static_value=definition.value,
        operations_function=operations_fun,
    )


def static_operand_builder(
    values: dict,
    static_value: T,
    operations_function: Callable[[T], V],
) -> V:
    return operations_function(static_value)


def create_dynamic_operand_builder(
    definition: DynamicOperand,
) -> Callable[[Dict[str, T]], V]:
    # local import to avoid circular dependency of modules with operations and evaluation
    from inference.core.workflows.core_steps.common.query_language.operations.core import (
        build_operations_chain,
    )

    operations_fun = build_operations_chain(operations=definition.operations)
    return partial(
        dynamic_operand_builder,
        operand_name=definition.operand_name,
        operations_function=operations_fun,
    )


def dynamic_operand_builder(
    values: [Dict[str, T]], operand_name: str, operations_function: Callable[[T], V]
) -> V:
    return operations_function(values[operand_name])


def binary_eval(
    values: Dict[str, T],
    left_operand_builder: Callable[[Dict[str, T]], V],
    operator: Callable[[V, V], bool],
    right_operand_builder: Callable[[Dict[str, T]], V],
    negate: bool,
    operation_type: str,
) -> bool:
    try:
        left_operand = left_operand_builder(values)
        right_operand = right_operand_builder(values)
        result = operator(left_operand, right_operand)
        if negate:
            result = not result
        return result
    except (TypeError, ValueError) as error:
        raise EvaluationEngineError(
            public_message=f"Attempted to execute evaluation of type: {operation_type}, "
                           f"but encountered error: {error}",
            context="step_execution | roboflow_query_language_evaluation",
            inner_error=error,

        )


def build_unary_statement(definition: UnaryStatement) -> Callable[[Dict[str, T]], bool]:
    operator = UNARY_OPERATORS[definition.operator.type]
    operand_builder = create_operand_builder(definition=definition.operand)
    return partial(
        unary_eval,
        operand_builder=operand_builder,
        operator=operator,
        negate=definition.negate,
        operation_type=definition.type,
    )


def unary_eval(
    values: Dict[str, T],
    operand_builder: Callable[[Dict[str, T]], V],
    operator: Callable[[V], bool],
    negate: bool,
    operation_type: str,
) -> bool:
    try:
        operand = operand_builder(values)
        result = operator(operand)
        if negate:
            result = not result
        return result
    except (TypeError, ValueError) as error:
        raise EvaluationEngineError(
            public_message=f"Attempted to execute evaluation of type: {operation_type}, "
                           f"but encountered error: {error}",
            context="step_execution | roboflow_query_language_evaluation",
            inner_error=error,

        )


COMPOUND_EVAL_STATEMENTS_COMBINERS = {
    StatementsGroupsOperator.AND: lambda a, b: a and b,
    StatementsGroupsOperator.OR: lambda a, b: a or b,
}


def compound_eval(
    values: Dict[str, T],
    statements_functions: List[Callable[[Dict[str, T]], bool]],
    operator: StatementsGroupsOperator,
) -> bool:
    if not statements_functions:
        raise EvaluationEngineError(
            public_message=f"Attempted to execute evaluation of statements, but empty statements list provided.",
            context="step_execution | roboflow_query_language_evaluation",
        )
    if operator not in COMPOUND_EVAL_STATEMENTS_COMBINERS:
        raise EvaluationEngineError(
            public_message=f"Attempted to execute evaluation of statements, using operator: "
            f"{operator} which is not registered.",
            context="step_execution | roboflow_query_language_evaluation",
        )
    operator_fun = COMPOUND_EVAL_STATEMENTS_COMBINERS[operator]
    result = statements_functions[0](values)
    for fun in statements_functions[1:]:
        fun_result = fun(values)
        result = operator_fun(result, fun_result)
    return result
