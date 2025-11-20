import os.path
import subprocess
import sys
from importlib import metadata

import jinja2

from .models import OutputTemplate
from .module_validation import ModuleValidator


def outputfile_compiler(output_file: OutputTemplate) -> str:
    templates_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))

    version = metadata.version("betterproto2_compiler")

    env = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        loader=jinja2.FileSystemLoader(templates_folder),
        undefined=jinja2.StrictUndefined,
    )

    # List of the symbols that should appear in the `__all__` variable of the file
    all: list[str] = []

    def add_to_all(name: str) -> str:
        all.append(name)
        return name

    env.filters["add_to_all"] = add_to_all

    body_template = env.get_template("template.py.j2")
    header_template = env.get_template("header.py.j2")

    # Load the body first do know the symbols defined in the file
    code = body_template.render(output_file=output_file)
    code = header_template.render(output_file=output_file, version=version, all=all) + "\n" + code

    try:
        # Sort imports, delete unused ones, sort __all__
        code = subprocess.check_output(
            ["ruff", "check", "--select", "I,F401,TC005,RUF022", "--fix", "--silent", "-"],
            input=code,
            encoding="utf-8",
        )

        # Format the code
        code = subprocess.check_output(["ruff", "format", "-"], input=code, encoding="utf-8")
    except subprocess.CalledProcessError:
        with open("invalid-generated-code.py", "w") as f:
            f.write(code)

        raise SyntaxError(
            f"Can't format the source code:\nThe invalid generated code has been written in `invalid-generated-code.py`"
        )

    # Validate the generated code.
    validator = ModuleValidator(iter(code.splitlines()))
    if not validator.validate():
        message_builder = ["[WARNING]: Generated code has collisions in the module:"]
        for collision, lines in validator.collisions.items():
            message_builder.append(f'  "{collision}" on lines:')
            for num, line in lines:
                message_builder.append(f"    {num}:{line}")
        print("\n".join(message_builder), file=sys.stderr)
    return code
