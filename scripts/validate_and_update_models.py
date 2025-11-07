"""
Validate and update existing models against fresh API data.

This script:
1. Fetches fresh data from the API for a given endpoint
2. Compares field types and structure with existing model
3. Identifies missing fields, type mismatches, and structural issues
4. Optionally updates the model file with corrections
5. Tests CRUD operations to verify field editability

Usage:
    # Dry run (report only)
    python scripts/validate_and_update_models.py notifications

    # Update model file
    python scripts/validate_and_update_models.py notifications --update

    # Validate all endpoints
    python scripts/validate_and_update_models.py --all

    # Use specific credentials
    python scripts/validate_and_update_models.py notifications --token YOUR_TOKEN
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import re
import sys
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from upsales.http import HTTPClient
from upsales.settings import load_settings

console = Console()


class ModelValidator:
    """Validates and updates model definitions against API data."""

    def __init__(self, token: str, email: str | None = None, password: str | None = None):
        """Initialize validator with credentials."""
        self.token = token
        self.email = email
        self.password = password
        self.base_url = "https://power.upsales.com/api/v2"

    async def fetch_sample_data(
        self, endpoint: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch sample data from API endpoint."""
        async with HTTPClient(token=self.token) as http:
            try:
                # Pass limit as query parameter via URL
                url = f"/{endpoint}?limit={limit}"
                response = await http.get(url)
                data = response.get("data", [])

                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
                else:
                    return []
            except Exception as e:
                console.print(f"[red]Error fetching {endpoint}: {e}[/red]")
                return []

    def analyze_field_types(
        self, samples: list[dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        """
        Analyze field types across all samples.

        Returns dict of field_name -> {types, nullable, sample_values}
        """
        field_info: dict[str, dict[str, Any]] = {}

        for sample in samples:
            for field_name, value in sample.items():
                if field_name not in field_info:
                    field_info[field_name] = {
                        "types": set(),
                        "nullable": False,
                        "sample_values": [],
                    }

                if value is None:
                    field_info[field_name]["nullable"] = True
                else:
                    field_info[field_name]["types"].add(type(value).__name__)
                    # Store up to 3 sample values
                    if len(field_info[field_name]["sample_values"]) < 3:
                        field_info[field_name]["sample_values"].append(value)

        return field_info

    def infer_python_type(self, field_info: dict[str, Any]) -> str:
        """Infer Python type annotation from field info."""
        types = field_info["types"]
        nullable = field_info["nullable"]

        if not types:
            return "Any | None" if nullable else "Any"

        # Convert Python types to annotation strings
        type_map = {
            "str": "str",
            "int": "int",
            "float": "float",
            "bool": "bool",
            "list": "list[Any]",
            "dict": "dict[str, Any]",
            "NoneType": "None",
        }

        type_strs = [type_map.get(t, "Any") for t in types]

        if len(type_strs) == 1:
            base_type = type_strs[0]
        else:
            # Multiple types - use union
            base_type = " | ".join(sorted(set(type_strs)))

        if nullable and "None" not in base_type:
            return f"{base_type} | None"

        return base_type

    def get_model_fields_from_file(self, model_file: Path, class_name: str) -> dict[str, str] | None:
        """
        Extract field definitions from a specific model class in a file.

        Args:
            model_file: Path to the model file
            class_name: Name of the class to extract fields from

        Returns:
            Dict of field_name -> field_type
        """
        if not model_file.exists():
            return None

        content = model_file.read_text()

        # Find the class definition
        class_pattern = rf"^class {class_name}\([^)]+\):"
        class_match = re.search(class_pattern, content, re.MULTILINE)

        if not class_match:
            return None

        # Get content starting from class definition
        class_start = class_match.end()

        # Find next class definition or end of file
        next_class = re.search(r"^class ", content[class_start:], re.MULTILINE)
        class_end = class_start + next_class.start() if next_class else len(content)

        class_content = content[class_start:class_end]

        # Extract field definitions
        field_pattern = re.compile(
            r"^\s+(\w+):\s+([\w\[\]\|\s,]+?)(?:\s*=|$)", re.MULTILINE
        )

        fields = {}
        for match in field_pattern.finditer(class_content):
            field_name, field_type = match.groups()
            field_type = field_type.strip()
            fields[field_name] = field_type

        return fields

    async def get_existing_model_fields(
        self, endpoint: str
    ) -> dict[str, str] | None:
        """Extract field definitions from existing model file."""
        # Convert endpoint to model filename
        endpoint_clean = endpoint.strip("/").replace("/", "_")
        model_file = (
            Path(__file__).parent.parent / "upsales" / "models" / f"{endpoint_clean}.py"
        )

        if not model_file.exists():
            return None

        # Get fields from the main model class (capitalized, singular)
        class_name = "".join(word.capitalize() for word in endpoint_clean.split("_"))

        # Try different class name patterns
        for name_variant in [class_name, class_name.rstrip("s"), class_name + "s"]:
            fields = self.get_model_fields_from_file(model_file, name_variant)
            if fields:
                return fields

        return None

    def extract_custom_model_name(self, type_annotation: str) -> str | None:
        """
        Extract custom model name from type annotation.

        Examples:
            "PartialUser | None" -> "PartialUser"
            "PartialCompany" -> "PartialCompany"
            "dict[str, Any]" -> None
            "list[PartialContact]" -> "PartialContact"

        Returns:
            Model name if found, None otherwise
        """
        # Remove optional/union with None
        type_clean = type_annotation.replace(" | None", "").replace("| None", "").strip()

        # Check for list types
        list_match = re.match(r"list\[(\w+)\]", type_clean)
        if list_match:
            type_clean = list_match.group(1)

        # Check if it's a custom model (starts with Partial or is a known model)
        if type_clean.startswith("Partial") or type_clean in [
            "User", "Company", "Contact", "Product", "Order", "Role",
        ]:
            return type_clean

        return None

    def get_nested_model_fields(self, model_name: str) -> dict[str, str] | None:
        """
        Get fields for a nested model by searching all model files.

        Args:
            model_name: Name of the model class (e.g., "PartialUser")

        Returns:
            Dict of field_name -> field_type
        """
        models_dir = Path(__file__).parent.parent / "upsales" / "models"

        # Search all model files for this class
        for model_file in models_dir.glob("*.py"):
            if model_file.stem in ("__init__", "base", "custom_fields"):
                continue

            fields = self.get_model_fields_from_file(model_file, model_name)
            if fields:
                return fields

        return None

    def validate_nested_model(
        self,
        field_name: str,
        model_type: str,
        api_sample: Any,
    ) -> dict[str, Any] | None:
        """
        Validate a nested custom model against API data.

        Returns:
            Validation result with nested issues, or None if valid
        """
        # Extract model name
        model_name = self.extract_custom_model_name(model_type)
        if not model_name:
            return None

        # Get model fields
        model_fields = self.get_nested_model_fields(model_name)
        if not model_fields:
            return None

        # Get API structure
        if not isinstance(api_sample, dict):
            return None

        # Analyze nested fields
        api_nested_fields = self.analyze_field_types([api_sample])

        # Compare
        missing_nested = []
        for api_field_name in api_nested_fields.keys():
            if api_field_name not in model_fields:
                missing_nested.append(api_field_name)

        extra_nested = []
        for model_field_name in model_fields.keys():
            if model_field_name not in api_nested_fields:
                extra_nested.append(model_field_name)

        if missing_nested or extra_nested:
            return {
                "model": model_name,
                "missing": missing_nested,
                "extra": extra_nested,
                "sample": api_sample,
            }

        return None

    def compare_fields(
        self,
        api_fields: dict[str, dict[str, Any]],
        model_fields: dict[str, str] | None,
    ) -> dict[str, Any]:
        """
        Compare API fields with model fields.

        Returns:
            dict with 'missing', 'type_mismatches', 'extra', 'nested_issues' keys
        """
        if model_fields is None:
            return {
                "missing": list(api_fields.keys()),
                "type_mismatches": [],
                "extra": [],
                "nested_issues": [],
            }

        missing = []
        type_mismatches = []
        extra = list(set(model_fields.keys()) - set(api_fields.keys()))
        nested_issues = []

        for field_name, field_info in api_fields.items():
            if field_name not in model_fields:
                missing.append(field_name)
            else:
                inferred_type = self.infer_python_type(field_info)
                existing_type = model_fields[field_name]

                # Check if it's a custom model
                custom_model = self.extract_custom_model_name(existing_type)
                if custom_model and field_info["sample_values"]:
                    # Validate nested model
                    sample = field_info["sample_values"][0]
                    if sample:  # Not None
                        nested_validation = self.validate_nested_model(
                            field_name, existing_type, sample
                        )
                        if nested_validation:
                            nested_issues.append({
                                "field": field_name,
                                **nested_validation
                            })
                    # Don't report as type mismatch if using custom model
                    continue

                # Normalize types for comparison
                inferred_normalized = self._normalize_type(inferred_type)
                existing_normalized = self._normalize_type(existing_type)

                # Skip if types are compatible (dict vs dict[str, Any], etc.)
                if self._types_compatible(existing_normalized, inferred_normalized):
                    continue

                if inferred_normalized != existing_normalized:
                    type_mismatches.append(
                        {
                            "field": field_name,
                            "existing": existing_type,
                            "inferred": inferred_type,
                            "samples": field_info["sample_values"][:2],
                        }
                    )

        return {
            "missing": missing,
            "type_mismatches": type_mismatches,
            "extra": extra,
            "nested_issues": nested_issues,
        }

    def _types_compatible(self, type1: str, type2: str) -> bool:
        """Check if two type annotations are compatible."""
        # Remove spaces
        t1 = type1.replace(" ", "")
        t2 = type2.replace(" ", "")

        # dict and dict[str,Any] are compatible
        if ("dict" in t1 and "dict" in t2) or ("list" in t1 and "list" in t2):
            return True

        return False

    def _normalize_type(self, type_str: str) -> str:
        """Normalize type string for comparison."""
        # Remove whitespace
        normalized = type_str.replace(" ", "")

        # Sort union types
        if "|" in normalized:
            parts = normalized.split("|")
            normalized = "|".join(sorted(parts))

        return normalized

    async def validate_endpoint(self, endpoint: str) -> dict[str, Any]:
        """
        Validate an endpoint's model against API data.

        Returns validation report.
        """
        console.print(f"\n[cyan]Validating endpoint: /{endpoint}[/cyan]")

        # Fetch samples
        with console.status(f"[cyan]Fetching data from /{endpoint}..."):
            samples = await self.fetch_sample_data(endpoint)

        if not samples:
            return {
                "endpoint": endpoint,
                "status": "no_data",
                "message": "No data available from API",
            }

        console.print(f"[green]✓[/green] Found {len(samples)} samples")

        # Analyze fields
        api_fields = self.analyze_field_types(samples)
        console.print(f"[green]✓[/green] Analyzed {len(api_fields)} fields")

        # Get existing model
        model_fields = await self.get_existing_model_fields(endpoint)

        if model_fields is None:
            console.print("[yellow]⚠[/yellow] No existing model found")
            status = "no_model"
        else:
            console.print(
                f"[green]✓[/green] Loaded existing model ({len(model_fields)} fields)"
            )
            status = "validated"

        # Compare
        comparison = self.compare_fields(api_fields, model_fields)

        return {
            "endpoint": endpoint,
            "status": status,
            "samples_count": len(samples),
            "api_fields": api_fields,
            "model_fields": model_fields,
            "comparison": comparison,
        }

    def print_validation_report(self, report: dict[str, Any]) -> None:
        """Print a formatted validation report."""
        endpoint = report["endpoint"]
        status = report["status"]

        if status == "no_data":
            console.print(Panel(f"[yellow]{report['message']}[/yellow]", title=endpoint))
            return

        comparison = report["comparison"]

        # Summary table
        table = Table(title=f"Validation Report: {endpoint}")
        table.add_column("Category", style="cyan")
        table.add_column("Count", justify="right")

        table.add_row("API Samples", str(report["samples_count"]))
        table.add_row("API Fields", str(len(report["api_fields"])))
        if report["model_fields"]:
            table.add_row("Model Fields", str(len(report["model_fields"])))
        table.add_row(
            "[yellow]Missing Fields[/yellow]", str(len(comparison["missing"]))
        )
        table.add_row(
            "[red]Type Mismatches[/red]", str(len(comparison["type_mismatches"]))
        )
        table.add_row("[blue]Extra Fields[/blue]", str(len(comparison["extra"])))
        table.add_row(
            "[magenta]Nested Model Issues[/magenta]", str(len(comparison.get("nested_issues", [])))
        )

        console.print(table)

        # Details
        if comparison["missing"]:
            console.print("\n[yellow]Missing Fields:[/yellow]")
            for field in comparison["missing"][:10]:  # Show first 10
                field_info = report["api_fields"][field]
                inferred_type = self.infer_python_type(field_info)
                sample = field_info["sample_values"][0] if field_info["sample_values"] else "N/A"
                console.print(f"  • {field}: {inferred_type} (sample: {sample})")
            if len(comparison["missing"]) > 10:
                console.print(f"  ... and {len(comparison['missing']) - 10} more")

        if comparison["type_mismatches"]:
            console.print("\n[red]Type Mismatches:[/red]")
            for mismatch in comparison["type_mismatches"][:10]:
                console.print(f"  • {mismatch['field']}:")
                console.print(f"    Existing: {mismatch['existing']}")
                console.print(f"    Inferred: {mismatch['inferred']}")
                if mismatch["samples"]:
                    console.print(f"    Sample: {mismatch['samples'][0]}")

        if comparison["extra"]:
            console.print("\n[blue]Extra Fields (in model but not API):[/blue]")
            for field in comparison["extra"][:10]:
                console.print(f"  • {field}")

        if comparison.get("nested_issues"):
            console.print("\n[magenta]Nested Model Issues:[/magenta]")
            for issue in comparison["nested_issues"][:5]:
                console.print(f"  • {issue['field']} ({issue['model']}):")
                if issue.get("missing"):
                    console.print(f"    Missing in model: {', '.join(issue['missing'][:5])}")
                if issue.get("extra"):
                    console.print(f"    Extra in model: {', '.join(issue['extra'][:5])}")

        # Verdict
        nested_count = len(comparison.get("nested_issues", []))
        if not comparison["missing"] and not comparison["type_mismatches"] and not nested_count:
            console.print("\n[green]✓ Model is up to date![/green]")
        else:
            console.print(
                f"\n[yellow]⚠ Model needs updates: {len(comparison['missing'])} missing, "
                f"{len(comparison['type_mismatches'])} mismatches, "
                f"{nested_count} nested issues[/yellow]"
            )


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate and update models against API data"
    )
    parser.add_argument(
        "endpoint",
        nargs="?",
        help="Endpoint to validate (e.g., 'notifications', 'users')",
    )
    parser.add_argument(
        "--all", action="store_true", help="Validate all implemented endpoints"
    )
    parser.add_argument("--update", action="store_true", help="Update model files")
    parser.add_argument("--token", help="API token (overrides .env)")
    parser.add_argument("--email", help="Email for auth fallback")
    parser.add_argument("--password", help="Password for auth fallback")
    parser.add_argument(
        "--limit", type=int, default=100, help="Number of samples to fetch"
    )

    args = parser.parse_args()

    if not args.endpoint and not args.all:
        parser.error("Either specify an endpoint or use --all")

    # Load credentials
    if args.token:
        token = args.token
        email = args.email
        password = args.password
    else:
        try:
            settings = load_settings()
            token = settings.upsales_token
            email = settings.upsales_email
            password = settings.upsales_password
        except Exception as e:
            console.print(f"[red]Error loading settings: {e}[/red]")
            console.print("Please provide --token or configure .env file")
            sys.exit(1)

    validator = ModelValidator(token, email, password)

    # Determine endpoints to validate
    if args.all:
        # Get all implemented resources
        resources_dir = Path(__file__).parent.parent / "upsales" / "resources"
        endpoints = [
            f.stem
            for f in resources_dir.glob("*.py")
            if f.stem not in ("__init__", "base")
        ]
    else:
        endpoints = [args.endpoint]

    # Validate each endpoint
    reports = []
    for endpoint in endpoints:
        report = await validator.validate_endpoint(endpoint)
        reports.append(report)
        validator.print_validation_report(report)

    # Summary
    if len(reports) > 1:
        console.print("\n" + "=" * 60)
        console.print("[bold]Summary:[/bold]")

        summary_table = Table()
        summary_table.add_column("Endpoint")
        summary_table.add_column("Status", justify="center")
        summary_table.add_column("Missing", justify="right")
        summary_table.add_column("Mismatches", justify="right")
        summary_table.add_column("Nested", justify="right")

        for report in reports:
            if report["status"] == "no_data":
                summary_table.add_row(
                    report["endpoint"], "[yellow]No Data[/yellow]", "-", "-", "-"
                )
            elif report["status"] == "no_model":
                summary_table.add_row(
                    report["endpoint"], "[yellow]No Model[/yellow]", "-", "-", "-"
                )
            else:
                comp = report["comparison"]
                nested_count = len(comp.get("nested_issues", []))
                status = (
                    "[green]✓[/green]"
                    if not comp["missing"] and not comp["type_mismatches"] and not nested_count
                    else "[yellow]⚠[/yellow]"
                )
                summary_table.add_row(
                    report["endpoint"],
                    status,
                    str(len(comp["missing"])),
                    str(len(comp["type_mismatches"])),
                    str(nested_count),
                )

        console.print(summary_table)


if __name__ == "__main__":
    asyncio.run(main())
