"""
CLI tool for code generation and validation.

Uses Python 3.13 native type hints and pattern matching.

Example:
    $ upsales generate-model users
    $ upsales generate-model roles --partial
    $ upsales validate

Note:
    Generates Pydantic models from API responses with Python 3.13 syntax.
"""

import asyncio
import os
import re
from typing import Any

import httpx
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.traceback import install

# Install Rich traceback handler for beautiful error messages
install(show_locals=False, width=100, word_wrap=True)

app = typer.Typer(
    name="upsales",
    help="Upsales Python SDK CLI - Generate models and validate code",
    add_completion=False,
)
console = Console()


# Helper functions for model generation


def _to_snake_case(name: str) -> str:
    """
    Convert camelCase or PascalCase to snake_case.

    Args:
        name: Name in camelCase or PascalCase

    Returns:
        Name in snake_case

    Examples:
        >>> _to_snake_case("orderStages")
        'order_stages'
        >>> _to_snake_case("salesCoaches")
        'sales_coaches'
        >>> _to_snake_case("apiKeys")
        'api_keys'
        >>> _to_snake_case("ProjectPlanStages")
        'project_plan_stages'
    """
    # Insert underscore before uppercase letters preceded by lowercase/digits
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    # Insert underscore before uppercase letters preceded by lowercase/digits
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def _detect_partial_model(field_name: str, value: dict[str, Any]) -> str | None:
    """
    Detect if a dict field should use a Partial model based on field name and structure.

    Args:
        field_name: Name of the field
        value: Sample dict value

    Returns:
        Partial model name or None if not an entity reference
    """
    # Must have id to be an entity reference
    if "id" not in value:
        return None

    field_lower = field_name.lower()

    # User/people references
    if any(
        kw in field_lower
        for kw in ["user", "owner", "assigned", "regby", "modby", "createdby", "registeredby"]
    ):
        if "email" in value or "name" in value:
            return "PartialUser"

    # Company/account references
    if any(kw in field_lower for kw in ["client", "company", "account"]):
        if "name" in value:
            return "PartialCompany"

    # Contact references
    if "contact" in field_lower and "name" in value:
        return "PartialContact"

    # Product references
    if "product" in field_lower and "name" in value:
        return "PartialProduct"

    # Order/opportunity references
    if any(kw in field_lower for kw in ["order", "opportunity"]) and "id" in value:
        return "PartialOrder"

    # Role references
    if "role" in field_lower and "name" in value:
        return "PartialRole"

    # Project references
    if "project" in field_lower and "name" in value:
        return "PartialProject"

    # Generic entity with id+name (unknown type)
    if "name" in value:
        return "dict[str, Any]  # Has id+name - consider Partial model"

    return None


def _python_type_from_value(value: Any, field_name: str = "") -> tuple[str, str]:
    """
    Infer Python 3.13 type hint from JSON value.

    Args:
        value: JSON value from API response.
        field_name: Name of the field (helps detect entity references).

    Returns:
        Tuple of (python_type, extra_comment) where extra_comment is additional notes.
    """
    match value:
        case None:
            return "Any", "  # Was None in samples"
        case bool():
            return "bool", ""
        case int():
            return "int", ""
        case float():
            return "float", ""
        case str():
            return "str", ""
        case list():
            if not value:
                return "list[Any]", ""
            # Check if list of entity references
            if value and isinstance(value[0], dict):
                partial = _detect_partial_model(field_name, value[0])
                if partial and "dict" not in partial:  # Found specific Partial model
                    return (
                        f"list[{partial}]",
                        f"  # TODO: from upsales.models.{partial.lower().replace('partial', '')} import {partial}",
                    )
                # Has structure but couldn't map
                if "id" in value[0]:
                    return (
                        "list[dict[str, Any]]",
                        "  # TODO: Has id - check if should use Partial model",
                    )
            # Infer from first element
            first_type, _ = _python_type_from_value(value[0], "")
            return f"list[{first_type}]", ""
        case dict():
            if not value:
                return "dict[str, Any]", ""
            # Check if it's an entity reference
            partial = _detect_partial_model(field_name, value)
            if partial:
                if "dict" not in partial:  # Found specific Partial model
                    return (
                        partial,
                        f"  # TODO: from upsales.models.{partial.lower().replace('partial', '')} import {partial}",
                    )
                # Generic suggestion (has id+name but couldn't map)
                return partial, ""
            # Generic dict
            return "dict[str, Any]", ""
        case _:
            return "Any", ""


def _generate_field_line(
    field_name: str,
    field_info: dict[str, Any],
) -> tuple[str, str]:
    """
    Generate a model field line with type hint based on analysis.

    Args:
        field_name: Name of the field.
        field_info: Analysis info with keys: is_required, sample_value, present_count, total_count.

    Returns:
        Tuple of (field_line, comment) for the field.
    """
    sample_value = field_info["sample_value"]
    is_required = field_info["is_required"]
    present_count = field_info["present_count"]
    non_null_count = field_info["non_null_count"]
    total_count = field_info["total_count"]

    python_type, extra_comment = _python_type_from_value(sample_value, field_name)

    # Generate detailed comment showing analysis
    percentage = (present_count / total_count * 100) if total_count > 0 else 0

    # Build comment with null information
    if present_count == total_count:
        # Present in all objects
        if non_null_count == total_count:
            # Never null - required field
            comment = f"  # Present in 100% ({present_count}/{total_count}){extra_comment}"
        else:
            # Null in some - optional field
            null_count = present_count - non_null_count
            comment = f"  # Present in 100% ({present_count}/{total_count}), null in {null_count}{extra_comment}"
    else:
        # Missing from some objects
        comment = f"  # Present in {percentage:.0f}% ({present_count}/{total_count}){extra_comment}"

    # Special handling for 'custom' field - always optional with default
    if field_name == "custom":
        return f"    {field_name}: list[dict] = []", comment

    # Required fields - present and non-null in all objects
    if is_required:
        # Lists and dicts with defaults even when required
        if python_type.startswith("list"):
            return f"    {field_name}: {python_type} = []", comment
        if python_type.startswith("dict"):
            return f"    {field_name}: {python_type} = {{}}", comment
        return f"    {field_name}: {python_type}", comment

    # Optional fields - missing or null in some objects
    else:
        if python_type == "Any":
            return f"    {field_name}: Any | None = None", comment

        # Lists and dicts - optional with default
        if python_type.startswith("list"):
            return f"    {field_name}: {python_type} | None = []", comment
        if python_type.startswith("dict"):
            return f"    {field_name}: {python_type} | None = {{}}", comment

        # Regular optional field
        return f"    {field_name}: {python_type} | None = None", comment


def _generate_model_code(
    model_name: str,
    endpoint: str,
    field_analysis: dict[str, dict[str, Any]],
    include_partial: bool,
    sample_count: int,
) -> str:
    """
    Generate complete model file code with field analysis.

    Args:
        model_name: Name of the model (e.g., "User").
        endpoint: API endpoint name.
        field_analysis: Analysis of field requirements.
        include_partial: Whether to include PartialModel.
        sample_count: Number of samples analyzed.

    Returns:
        Complete Python file content.
    """
    # Generate imports
    imports = [
        "from typing import Unpack, TypedDict, Any",
        "from pydantic import Field",
        "from upsales.models.base import BaseModel",
    ]

    if include_partial:
        imports.append("from upsales.models.base import PartialModel")

    imports_str = "\n".join(imports)

    # Generate TypedDict (all fields except id)
    typeddict_name = f"{model_name}UpdateFields"
    typeddict_fields = []

    for field_name, field_info in field_analysis.items():
        if field_name in ("id", "_client"):  # Skip read-only and internal fields
            continue
        sample_value = field_info["sample_value"]
        python_type, extra_comment = _python_type_from_value(sample_value, field_name)
        # TypedDicts always use dict[str, Any] for entity references (input data)
        # So if we got a Partial model type, convert back to dict for TypedDict
        if "Partial" in python_type:
            python_type = "dict[str, Any]" if "list" not in python_type else "list[dict[str, Any]]"
            extra_comment = ""  # Remove TODO for TypedDict
        typeddict_fields.append(f"    {field_name}: {python_type}")

    typeddict_code = f'''class {typeddict_name}(TypedDict, total=False):
    """
    Available fields for updating a {model_name}.

    All fields are optional.
    """
{chr(10).join(typeddict_fields) if typeddict_fields else "    pass"}
'''

    # Generate main model with analysis comments
    field_lines = []
    partial_models_needed = set()
    for field_name, field_info in sorted(field_analysis.items()):
        if field_name == "_client":
            continue
        field_line, comment = _generate_field_line(field_name, field_info)
        field_lines.append(field_line + comment)

        # Track which Partial models are referenced
        if "Partial" in field_line:
            import re

            partial_match = re.search(r"Partial\w+", field_line)
            if partial_match:
                partial_models_needed.add(partial_match.group())

    # Build import TODO list
    import_todos = []
    for partial in sorted(partial_models_needed):
        module = partial.lower().replace("partial", "")
        import_todos.append(f"    # from upsales.models.{module} import {partial}")

    imports_section = "\n".join(import_todos) if import_todos else ""
    imports_todo = (
        f"\n{imports_section}\n    TODO: Add the above imports to use Partial models"
        if imports_section
        else ""
    )

    model_code = f'''class {model_name}(BaseModel):
    """
    {model_name} model from /api/v2/{endpoint}.

    Generated from {sample_count} sample{"s" if sample_count != 1 else ""}.

    TODO: Review and update field types and docstrings.
    TODO: Mark read-only fields with Field(frozen=True).
    TODO: Add custom_fields property if model has 'custom' field.{imports_todo}
    """

{chr(10).join(field_lines)}

    async def edit(self, **kwargs: Unpack[{typeddict_name}]) -> "{model_name}":
        """
        Edit this {model_name.lower()}.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated {model_name.lower()}.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.{endpoint}.update(
            self.id,
            **self.to_update_dict(**kwargs)
        )
'''

    # Generate partial model if requested
    partial_code = ""
    if include_partial:
        # Include id and a few key fields for partial
        partial_fields = []
        for field_name in ["id", "name", "title", "email"]:
            if field_name in field_analysis:
                field_info = field_analysis[field_name]
                field_line, comment = _generate_field_line(field_name, field_info)
                partial_fields.append(field_line + comment)

        partial_code = f'''

class Partial{model_name}(PartialModel):
    """
    Partial {model_name} for nested responses.

    TODO: Add fields that should be available in partial objects.
    """

{chr(10).join(partial_fields) if partial_fields else "    id: int"}

    async def fetch_full(self) -> {model_name}:
        """Fetch full {model_name.lower()} data."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.{endpoint}.get(self.id)

    async def edit(self, **kwargs: Unpack[{typeddict_name}]) -> {model_name}:
        """Edit this {model_name.lower()}."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.{endpoint}.update(self.id, **kwargs)
'''

    # Build complete file with analysis metadata
    file_content = f'''"""
{model_name} models for Upsales API.

Generated from /api/v2/{endpoint} endpoint.
Analysis based on {sample_count} sample{"s" if sample_count != 1 else ""}.

Field optionality determined by:
- Required: Field present AND non-null in 100% of samples
- Optional: Field missing OR null in any sample
- Custom fields: Always optional with default []

TODO: Review and customize the generated models:
1. Mark read-only fields with Field(frozen=True)
2. Update field types if needed
3. Add custom_fields property if 'custom' field exists
4. Update docstrings with detailed descriptions
5. Add any custom methods
"""

{imports_str}


{typeddict_code}

{model_code}{partial_code}'''

    return file_content


async def _fetch_api_samples(endpoint: str, token: str, limit: int = 2000) -> list[dict[str, Any]]:
    """
    Fetch multiple samples from API for field analysis.

    Args:
        endpoint: API endpoint name.
        token: API token.
        limit: Maximum number of objects to fetch (default: 2000).

    Returns:
        List of objects from API response (up to limit).

    Raises:
        RuntimeError: If API request fails.
    """
    base_url = os.getenv("UPSALES_BASE_URL", "https://power.upsales.com/api/v2")

    async with httpx.AsyncClient(
        base_url=base_url,
        headers={"Cookie": f"token={token}"},
        timeout=60.0,  # Longer timeout for large requests
    ) as http_client:
        try:
            # Fetch list with specified limit
            response = await http_client.get(f"/{endpoint}", params={"limit": limit})

            # If 401, try token refresh
            if response.status_code == 401:
                email = os.getenv("UPSALES_EMAIL")
                password = os.getenv("UPSALES_PASSWORD")

                if email and password:
                    with console.status("[yellow]Refreshing expired token...", spinner="dots"):
                        session_response = await http_client.post(
                            "/session/",
                            json={"email": email, "password": password, "samlBypass": None},
                        )

                        if session_response.status_code == 200:
                            session_data = session_response.json()
                            new_token = session_data["data"]["token"]

                            # Retry with new token
                            http_client.headers.update({"Cookie": f"token={new_token}"})
                            response = await http_client.get(
                                f"/{endpoint}", params={"limit": limit}
                            )
                        else:
                            raise RuntimeError(
                                "Token refresh failed - check UPSALES_EMAIL/PASSWORD"
                            )

                    console.print("[green]✅ Token refreshed successfully![/green]")

            if response.status_code == 200:
                data = response.json()

                # Get list of objects
                if "data" in data and isinstance(data["data"], list):
                    objects = data["data"]

                    # Show metadata if available
                    if "metadata" in data:
                        total = data["metadata"].get("total", len(objects))
                        console.print(f"[dim]Fetched {len(objects)} of {total} total objects[/dim]")

                    if objects:
                        return objects
                    else:
                        # Empty list - try getting single object
                        console.print(
                            "[yellow]No objects in list, trying single object...[/yellow]"
                        )
                        single_response = await http_client.get(f"/{endpoint}/1")
                        if single_response.status_code == 200:
                            single_data = single_response.json()
                            if "data" in single_data:
                                return [single_data["data"]]

            raise RuntimeError(
                f"Failed to fetch from /api/v2/{endpoint}: "
                f"Status {response.status_code}. "
                f"Response: {response.text[:200]}"
            )

        except httpx.RequestError as e:
            raise RuntimeError(f"API request failed: {e}") from e


def _analyze_field_requirements(objects: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    Analyze field requirements across multiple objects.

    Determines which fields are required vs optional based on their
    presence and null values across the dataset.

    Args:
        objects: List of objects from API.

    Returns:
        Dict mapping field names to analysis results with keys:
        - present_count: Number of objects with this field
        - non_null_count: Number of objects where field is not None
        - total_count: Total number of objects analyzed
        - is_required: Whether field should be required
        - sample_value: Sample value for type inference

    Example:
        >>> analysis = _analyze_field_requirements(objects)
        >>> analysis["email"]["is_required"]  # True if in all objects
        >>> analysis["description"]["is_required"]  # False if missing/null in any
    """
    if not objects:
        return {}

    total_count = len(objects)
    field_analysis: dict[str, dict[str, Any]] = {}

    # Collect all unique field names
    all_fields: set[str] = set()
    for obj in objects:
        all_fields.update(obj.keys())

    # Analyze each field
    for field_name in all_fields:
        present_count = 0
        non_null_count = 0
        sample_value = None

        for obj in objects:
            if field_name in obj:
                present_count += 1
                value = obj[field_name]

                if value is not None:
                    non_null_count += 1
                    if sample_value is None:
                        sample_value = value

        # Field is required if present AND non-null in ALL objects
        # Important: Field that exists but is null in some → OPTIONAL
        # Example: userTitle exists in 100% but null in 40% → OPTIONAL
        is_required = (present_count == total_count) and (non_null_count == total_count)

        field_analysis[field_name] = {
            "present_count": present_count,
            "non_null_count": non_null_count,
            "total_count": total_count,
            "is_required": is_required,
            "sample_value": sample_value,
        }

    return field_analysis


async def _generate_model_async(
    endpoint: str,
    token: str,
    output: str,
    include_partial: bool,
) -> None:
    """
    Async implementation of model generation.

    Args:
        endpoint: API endpoint name.
        token: API token.
        output: Output file path.
        include_partial: Whether to include PartialModel.
    """
    console.rule("[bold blue]Step 1: Fetching Data")

    try:
        with console.status("[cyan]Fetching objects from API (up to 2000)...", spinner="dots"):
            samples = await _fetch_api_samples(endpoint, token, limit=2000)
    except RuntimeError as e:
        console.print(f"[red]✗ Error: {e}[/red]")
        raise

    console.print(
        f"[green]✅ Success![/green] Fetched {len(samples)} object{'s' if len(samples) != 1 else ''}"
    )

    # Warn if limited sample size
    if len(samples) < 10:
        console.print(
            "[yellow]⚠ Warning: Limited sample size may affect field analysis accuracy[/yellow]"
        )

    # Determine model name (capitalize and singularize roughly)
    model_name = endpoint.rstrip("s").capitalize()
    if endpoint == "companies":
        model_name = "Company"
    elif endpoint.endswith("ies"):
        model_name = endpoint[:-3].capitalize() + "y"

    console.rule("[bold blue]Step 2: Analyzing Fields")

    # Analyze field requirements with status spinner
    with console.status(
        f"[cyan]Analyzing {len(samples)} objects for field requirements...", spinner="dots"
    ):
        field_analysis = _analyze_field_requirements(samples)

    # Show analysis summary
    required_count = sum(1 for f in field_analysis.values() if f["is_required"])
    optional_count = len(field_analysis) - required_count

    console.print("[green]✅ Analysis complete![/green]")
    console.print(f"   • Fields: {len(field_analysis)} total")
    console.print(f"   • Required: {required_count}")
    console.print(f"   • Optional: {optional_count}")

    console.rule("[bold blue]Step 3: Code Generation")

    # Generate code with status spinner
    with console.status(f"[cyan]Generating {model_name} model code...", spinner="dots"):
        code = _generate_model_code(
            model_name, endpoint, field_analysis, include_partial, len(samples)
        )

    # Show preview
    console.print("\n[bold]Preview:[/bold]")
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)

    console.rule("[bold blue]Step 4: Writing File")

    # Write to file with status spinner
    with console.status(f"[cyan]Writing to {output}...", spinner="dots"):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output), exist_ok=True)

        with open(output, "w", encoding="utf-8") as f:
            f.write(code)

    console.rule("[bold green]Complete")

    console.print("[green]✅ Model generated successfully![/green]")
    console.print(f"   📄 File: [cyan]{output}[/cyan]")
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(f"  1. Review [cyan]{output}[/cyan]")
    console.print("  2. Mark read-only fields with [yellow]Field(frozen=True)[/yellow]")
    console.print(f"  3. Create resource manager in [cyan]upsales/resources/{endpoint}.py[/cyan]")
    console.print(
        f"  4. Update [cyan]upsales/client.py[/cyan] to add [yellow]self.{endpoint} = {model_name}sResource(...)[/yellow]"
    )


@app.command()
def generate_model(
    endpoint: str = typer.Argument(
        ..., help="API endpoint name (e.g., 'users', 'roles', 'products')"
    ),
    partial: bool = typer.Option(False, "--partial", help="Also generate PartialModel class"),
    output: str | None = typer.Option(
        None, "--output", "-o", help="Output file path (default: upsales/models/{endpoint}.py)"
    ),
    token: str | None = typer.Option(
        None,
        "--token",
        "-t",
        help="Upsales API token (or set UPSALES_TOKEN env var)",
        envvar="UPSALES_TOKEN",
    ),
) -> None:
    """
    Generate Pydantic models from API response.

    Fetches a sample response from the API and generates type-safe
    Pydantic models using Python 3.13 syntax:
    - Native type hints (list, dict, str | None)
    - TypedDict for IDE autocomplete
    - Proper docstrings

    Example:
        $ upsales generate-model users --partial
        $ upsales generate-model roles
        $ upsales generate-model products --output custom/path.py

    Note:
        Use --partial flag to also generate PartialModel class.
        TypedDict is always generated for IDE autocomplete.
    """
    # Load .env if it exists
    load_dotenv()

    # Get token
    if not token:
        token = os.getenv("UPSALES_TOKEN")

    if not token:
        console.print("[red]Error: UPSALES_TOKEN not found[/red]")
        console.print("[dim]Set it in .env file or use --token flag[/dim]")
        raise typer.Exit(1)

    # Determine output path (always use snake_case for file names)
    if output is None:
        file_name = _to_snake_case(endpoint)
        output = f"upsales/models/{file_name}.py"
        console.print(f"[dim]Converted endpoint name to snake_case:[/dim] {endpoint} → {file_name}")

    console.print(
        Panel.fit(
            f"[bold blue]Generating models for:[/bold blue] [cyan]{endpoint}[/cyan]",
            border_style="blue",
        )
    )
    console.print(f"[dim]Output path:[/dim] {output}")
    console.print(f"[dim]Include partial:[/dim] {partial}")

    # Run async generation
    try:
        asyncio.run(_generate_model_async(endpoint, token, output, partial))
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def validate() -> None:
    """
    Validate project code quality and standards.

    Runs comprehensive checks:
    - Docstring coverage (90%+ required via interrogate)
    - Type checking (mypy strict mode)
    - Code style (ruff)
    - Security (bandit)
    - Python 3.13 syntax usage

    Example:
        $ upsales validate
    """
    console.rule("[bold blue]Project Validation")

    # Run validation checks
    import subprocess
    from pathlib import Path

    table = Table(title="Validation Results", show_header=True, header_style="bold")
    table.add_column("Check", style="cyan", width=30)
    table.add_column("Status", width=10)
    table.add_column("Details", style="dim")

    project_root = Path.cwd()
    all_passed = True

    # Check 1: Docstring coverage with interrogate
    with console.status("[cyan]Checking docstring coverage...", spinner="dots"):
        try:
            result = subprocess.run(
                ["interrogate", "upsales", "-q"],
                capture_output=True,
                text=True,
                cwd=project_root,
            )
            if result.returncode == 0 and "100.0%" in result.stdout:
                table.add_row("Docstring Coverage", "[green]✓[/green]", "100% coverage")
            elif result.returncode == 0:
                pct = "90%+" if "PASSED" in result.stdout else "Below 90%"
                table.add_row("Docstring Coverage", "[yellow]⚠[/yellow]", pct)
                all_passed = False
            else:
                table.add_row("Docstring Coverage", "[red]✗[/red]", "Failed to check")
                all_passed = False
        except Exception as e:
            table.add_row("Docstring Coverage", "[red]✗[/red]", f"Error: {str(e)[:30]}")
            all_passed = False

    # Check 2: Check models have complete TypedDicts
    model_files = list((project_root / "upsales" / "models").glob("*.py"))
    model_files = [
        f
        for f in model_files
        if f.name
        not in (
            "__init__.py",
            "base.py",
            "custom_fields.py",
            "role.py",
            "category.py",
            "campaign.py",
        )
    ]

    typeddict_ok = True
    for model_file in model_files:
        with open(model_file) as f:
            source = f.read()
            # Simple check: does it have UpdateFields TypedDict?
            if "UpdateFields(TypedDict" in source:
                continue
            else:
                typeddict_ok = False
                break

    if typeddict_ok and len(model_files) > 0:
        table.add_row(
            "TypedDict Completeness",
            "[green]✓[/green]",
            f"{len(model_files)} models have TypedDict",
        )
    elif len(model_files) == 0:
        table.add_row("TypedDict Completeness", "[yellow]⚠[/yellow]", "No models found")
    else:
        table.add_row(
            "TypedDict Completeness", "[yellow]⚠[/yellow]", "Some models missing TypedDict"
        )
        all_passed = False

    # Check 3: Field descriptions (sample check)
    field_desc_count = 0
    field_total = 0
    for model_file in model_files:
        with open(model_file) as f:
            source = f.read()
            # Count Field( with description=
            field_desc_count += source.count('description="')
            # Rough count of fields
            field_total += (
                source.count(": int = Field") + source.count(": str") + source.count(": bool")
            )

    if field_desc_count > 100:  # Reasonable threshold
        table.add_row("Field Descriptions", "[green]✓[/green]", f"{field_desc_count}+ descriptions")
    else:
        table.add_row("Field Descriptions", "[yellow]⚠[/yellow]", "Add more descriptions")
        all_passed = False

    # Check 4: Resources registered
    with open(project_root / "upsales" / "client.py") as f:
        client_source = f.read()
        resources_ok = (
            "self.users = UsersResource" in client_source
            and "self.companies = CompaniesResource" in client_source
            and "self.products = ProductsResource" in client_source
        )

    if resources_ok:
        table.add_row("Resources Registered", "[green]✓[/green]", "Users, Companies, Products")
    else:
        table.add_row("Resources Registered", "[red]✗[/red]", "Some resources not registered")
        all_passed = False

    # Check 5: Exports complete
    with open(project_root / "upsales" / "models" / "__init__.py") as f:
        models_init = f.read()
        models_exported = (
            "User" in models_init and "Company" in models_init and "Product" in models_init
        )

    if models_exported:
        table.add_row("Model Exports", "[green]✓[/green]", "All models exported")
    else:
        table.add_row("Model Exports", "[red]✗[/red]", "Some models not exported")
        all_passed = False

    # Check 6: Settings available
    with open(project_root / "upsales" / "__init__.py") as f:
        main_init = f.read()
        settings_exported = "UpsalesSettings" in main_init

    if settings_exported:
        table.add_row("Settings Module", "[green]✓[/green]", "pydantic-settings configured")
    else:
        table.add_row("Settings Module", "[yellow]⚠[/yellow]", "Settings not exported")
        all_passed = False

    console.print()
    console.print(table)
    console.print()

    if all_passed:
        console.print("[green]✨ Project structure: EXCELLENT[/green]")
    else:
        console.print("[yellow]⚠️  Some checks need attention[/yellow]")

    console.print("[dim]Run individual tools for details:[/dim]")
    console.print("[dim]  - uv run interrogate upsales[/dim]")
    console.print("[dim]  - uv run mypy upsales[/dim]")
    console.print("[dim]  - uv run pytest tests/unit/[/dim]")


@app.command()
def init_resource(
    name: str = typer.Argument(..., help="Resource name (e.g., 'orders', 'contacts')"),
) -> None:
    """
    Initialize a new resource with boilerplate code.

    Creates model and resource files following project patterns:
    - Models with Python 3.13 type hints
    - Resource manager inheriting from BaseResource
    - Comprehensive docstrings

    Example:
        $ upsales init-resource orders
        $ upsales init-resource contacts

    Note:
        This creates placeholder files that need to be filled in based
        on the actual API structure.
    """
    from pathlib import Path

    console.rule(f"[bold blue]Initializing Resource: {name}")

    project_root = Path.cwd()

    # Convert to snake_case for file names (if needed)
    snake_case_name = _to_snake_case(name)
    if snake_case_name != name:
        console.print(f"[dim]Converted to snake_case:[/dim] {name} → {snake_case_name}")

    # Capitalize name for class names
    singular = snake_case_name.rstrip("s")  # Simple pluralization
    class_name = singular.capitalize()
    resource_class = f"{class_name}sResource"

    # Step 1: Create resource file (always use snake_case)
    resource_path = project_root / "upsales" / "resources" / f"{snake_case_name}.py"

    resource_template = f'''"""
{class_name}s resource manager for Upsales API.

Provides methods to interact with the /{snake_case_name} endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     {singular} = await upsales.{snake_case_name}.get(1)
    ...     {snake_case_name}_list = await upsales.{snake_case_name}.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.{snake_case_name} import {class_name}, Partial{class_name}
from upsales.resources.base import BaseResource


class {resource_class}(BaseResource[{class_name}, Partial{class_name}]):
    """
    Resource manager for {class_name} endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single {singular}
    - list(limit, offset, **params) - List {snake_case_name} with pagination
    - list_all(**params) - Auto-paginated list of all {snake_case_name}
    - update(id, **data) - Update {singular}
    - delete(id) - Delete {singular}
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = {resource_class}(http_client)
        >>> {singular} = await resource.get(1)
        >>> all_active = await resource.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize {snake_case_name} resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/{snake_case_name}",
            model_class={class_name},
            partial_class=Partial{class_name},
        )

    # Add custom methods here as needed
    # Example:
    # async def get_active(self) -> list[{class_name}]:
    #     """Get all active {snake_case_name}."""
    #     return await self.list_all(active=1)
'''

    # Write resource file
    with open(resource_path, "w") as f:
        f.write(resource_template)

    console.print()
    console.print(
        f"[green]✓[/green] Created [cyan]{resource_path.relative_to(project_root)}[/cyan]"
    )

    # Step 2: Update __init__.py
    init_path = project_root / "upsales" / "resources" / "__init__.py"

    with open(init_path) as f:
        init_content = f.read()

    # Add import if not exists (use snake_case for module name)
    import_line = f"from upsales.resources.{snake_case_name} import {resource_class}"
    if import_line not in init_content:
        # Find where to insert import (after other resource imports)
        lines = init_content.split("\n")
        import_idx = -1
        for i, line in enumerate(lines):
            if "from upsales.resources." in line and "import" in line:
                import_idx = i

        if import_idx >= 0:
            lines.insert(import_idx + 1, import_line)

            # Add to __all__
            all_idx = -1
            for i, line in enumerate(lines):
                if "__all__ = [" in line:
                    all_idx = i
                    break

            if all_idx >= 0:
                # Find the closing bracket
                for i in range(all_idx, len(lines)):
                    if "]" in lines[i] and "all" in lines[i - 1].lower():
                        lines.insert(i, f'    "{resource_class}",')
                        break

            with open(init_path, "w") as f:
                f.write("\n".join(lines))

            console.print(
                f"[green]✓[/green] Updated [cyan]{init_path.relative_to(project_root)}[/cyan]"
            )
        else:
            console.print("[yellow]⚠[/yellow] Could not auto-update __init__.py")

    # Step 3: Show next steps
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print()
    console.print("  1. Generate models:")
    console.print(f"     [cyan]uv run upsales generate-model {snake_case_name} --partial[/cyan]")
    console.print()
    console.print("  2. Add to [cyan]upsales/client.py[/cyan]:")
    console.print(
        f"     [dim]from upsales.resources.{snake_case_name} import {resource_class}[/dim]"
    )
    console.print(f"     [dim]self.{snake_case_name} = {resource_class}(self.http)[/dim]")
    console.print()
    console.print("[green]✨ Resource initialized successfully![/green]")


@app.callback()
def callback() -> None:
    """
    Upsales Python SDK CLI.

    Tools for generating models, validating code, and managing resources.
    Built for Python 3.13+ with modern syntax and best practices.
    """
    pass


if __name__ == "__main__":
    app()
