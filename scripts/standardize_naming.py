"""
Standardize file and class naming conventions across the SDK.

This script renames files from camelCase to snake_case and fixes class names
to follow proper PascalCase conventions.

**IMPORTANT**: This is a breaking change! Run this only once and commit the changes.

What it does:
1. Renames model files to snake_case (apiKeys.py → api_keys.py)
2. Renames resource files to snake_case
3. Fixes class names to proper PascalCase (Apikey → ApiKey, Projectplanstage → ProjectPlanStage)
4. Updates all imports in __init__.py files
5. Updates client.py attributes
6. Updates test file imports
7. Creates a git commit with all changes

Usage:
    python scripts/standardize_naming.py --dry-run   # Preview changes
    python scripts/standardize_naming.py --execute   # Apply changes

Before running:
    - Commit any pending changes
    - Create a backup branch: git checkout -b backup-before-naming-fix
    - Run with --dry-run first to review changes
"""

import argparse
import re
import shutil
from pathlib import Path

# Define renaming mappings
MODEL_RENAMES = {
    "apiKeys.py": "api_keys.py",
    "orderStages.py": "order_stages.py",
    "projectPlanStages.py": "project_plan_stages.py",
    "salesCoaches.py": "sales_coaches.py",
    "todoViews.py": "todo_views.py",
    "projectplanstatus.py": "project_plan_status.py",
    "clientcategories.py": "client_categories.py",
    "projectplanpriority.py": "project_plan_priority.py",
}

RESOURCE_RENAMES = {
    "apikeys.py": "api_keys.py",
    "orderStages.py": "order_stages.py",
    "projectPlanStages.py": "project_plan_stages.py",
    "todoViews.py": "todo_views.py",
    "projectplanstatus.py": "project_plan_status.py",
    "projectplanpriority.py": "project_plan_priority.py",
}

# Class name fixes (old_name → new_name)
CLASS_NAME_FIXES = {
    "Apikey": "ApiKey",
    "PartialApikey": "PartialApiKey",
    "Projectplanstage": "ProjectPlanStage",
    "PartialProjectplanstage": "PartialProjectPlanStage",
    "Clientcategory": "ClientCategory",
    "PartialClientcategory": "PartialClientCategory",
    "Projectplanpriority": "ProjectPlanPriority",
    "PartialProjectplanpriority": "PartialProjectPlanPriority",
    "Projectplanstatus": "ProjectPlanStatus",
    "PartialProjectplanstatus": "PartialProjectPlanStatus",
}


def to_snake_case(name: str) -> str:
    """Convert PascalCase or camelCase to snake_case."""
    # Insert underscore before uppercase letters
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    # Insert underscore before uppercase letters preceded by lowercase
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def rename_file(old_path: Path, new_name: str, dry_run: bool = True) -> Path | None:
    """
    Rename a file.

    Args:
        old_path: Current file path
        new_name: New file name (not full path)
        dry_run: If True, only print what would happen

    Returns:
        New path if renamed, None if skipped
    """
    new_path = old_path.parent / new_name

    if not old_path.exists():
        print(f"   ⚠️  SKIP: {old_path.name} (file not found)")
        return None

    if old_path == new_path:
        print(f"   ⏭️  SKIP: {old_path.name} (already correct)")
        return None

    if new_path.exists():
        print(f"   ❌ ERROR: {new_path.name} already exists!")
        return None

    if dry_run:
        print(f"   📝 WOULD RENAME: {old_path.name} → {new_name}")
    else:
        shutil.move(str(old_path), str(new_path))
        print(f"   ✅ RENAMED: {old_path.name} → {new_name}")

    return new_path


def fix_class_names_in_file(file_path: Path, dry_run: bool = True) -> int:
    """
    Fix class names in a file.

    Args:
        file_path: Path to file
        dry_run: If True, only print what would happen

    Returns:
        Number of replacements made
    """
    if not file_path.exists():
        return 0

    content = file_path.read_text(encoding="utf-8")
    original_content = content
    replacements = 0

    for old_name, new_name in CLASS_NAME_FIXES.items():
        # Match class definitions: "class Apikey(BaseModel):"
        pattern1 = rf"\bclass {old_name}\b"
        if re.search(pattern1, content):
            content = re.sub(pattern1, f"class {new_name}", content)
            replacements += content.count(f"class {new_name}") - original_content.count(f"class {new_name}")

        # Match type hints: "-> Apikey:" or "list[Apikey]"
        pattern2 = rf"(?<=[:\[\s,]){old_name}(?=[\]\s,:\)])"
        if re.search(pattern2, content):
            content = re.sub(pattern2, new_name, content)
            replacements += 1

    if replacements > 0:
        if dry_run:
            print(f"   📝 WOULD FIX {replacements} class name(s) in: {file_path.name}")
        else:
            file_path.write_text(content, encoding="utf-8")
            print(f"   ✅ FIXED {replacements} class name(s) in: {file_path.name}")

    return replacements


def update_imports_in_file(file_path: Path, old_module: str, new_module: str, dry_run: bool = True) -> int:
    """
    Update import statements in a file.

    Args:
        file_path: Path to file
        old_module: Old module name (e.g., "apiKeys")
        new_module: New module name (e.g., "api_keys")
        dry_run: If True, only print what would happen

    Returns:
        Number of replacements made
    """
    if not file_path.exists():
        return 0

    content = file_path.read_text(encoding="utf-8")
    original_content = content

    # Pattern: from upsales.models.apiKeys import ...
    # Pattern: from upsales.resources.apiKeys import ...
    patterns = [
        (rf"from upsales\.models\.{old_module} import", f"from upsales.models.{new_module} import"),
        (rf"from upsales\.resources\.{old_module} import", f"from upsales.resources.{new_module} import"),
        (rf"import upsales\.models\.{old_module}", f"import upsales.models.{new_module}"),
        (rf"import upsales\.resources\.{old_module}", f"import upsales.resources.{new_module}"),
    ]

    replacements = 0
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            replacements += 1

    if content != original_content:
        if dry_run:
            print(f"   📝 WOULD UPDATE imports in: {file_path.name}")
        else:
            file_path.write_text(content, encoding="utf-8")
            print(f"   ✅ UPDATED imports in: {file_path.name}")

    return replacements


def update_client_attributes(dry_run: bool = True) -> int:
    """
    Update client.py to use snake_case attributes.

    Args:
        dry_run: If True, only print what would happen

    Returns:
        Number of replacements made
    """
    client_path = Path("upsales/client.py")
    if not client_path.exists():
        print("   ⚠️  client.py not found")
        return 0

    content = client_path.read_text(encoding="utf-8")
    original_content = content

    # Attribute mappings (camelCase → snake_case)
    attribute_renames = {
        "orderStages": "order_stages",
        "salesCoaches": "sales_coaches",
        "todoViews": "todo_views",
        "apiKeys": "api_keys",
        "projectPlanStages": "project_plan_stages",
        "projectplanstatus": "project_plan_status",
        "projectplanpriority": "project_plan_priority",
        "clientcategories": "client_categories",
    }

    replacements = 0
    for old_attr, new_attr in attribute_renames.items():
        # Pattern: self.orderStages = OrderStagesResource(...)
        pattern = rf"\bself\.{old_attr}\b"
        if re.search(pattern, content):
            content = re.sub(pattern, f"self.{new_attr}", content)
            replacements += 1

    if content != original_content:
        if dry_run:
            print(f"   📝 WOULD UPDATE {replacements} attribute(s) in: client.py")
        else:
            client_path.write_text(content, encoding="utf-8")
            print(f"   ✅ UPDATED {replacements} attribute(s) in: client.py")

    return replacements


def main():
    """Main refactoring workflow."""
    parser = argparse.ArgumentParser(description="Standardize SDK naming conventions")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the refactoring (default: dry-run)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without applying them (default)"
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompt"
    )
    args = parser.parse_args()

    dry_run = not args.execute

    print("\n" + "=" * 80)
    print("SDK NAMING STANDARDIZATION")
    print("=" * 80)

    if dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made")
        print("   Run with --execute to apply changes\n")
    else:
        print("\n⚠️  EXECUTION MODE - Changes will be applied!")
        print("   Make sure you have a backup branch!\n")
        if not args.yes:
            response = input("Continue? (yes/no): ")
            if response.lower() != "yes":
                print("Aborted.")
                return
        else:
            print("--yes flag provided, proceeding without confirmation.\n")

    # Step 1: Rename model files
    print("\n" + "-" * 80)
    print("STEP 1: Rename Model Files")
    print("-" * 80 + "\n")

    models_dir = Path("upsales/models")
    renamed_models = {}

    for old_name, new_name in MODEL_RENAMES.items():
        old_path = models_dir / old_name
        new_path = rename_file(old_path, new_name, dry_run)
        if new_path:
            renamed_models[old_name] = new_name

    # Step 2: Rename resource files
    print("\n" + "-" * 80)
    print("STEP 2: Rename Resource Files")
    print("-" * 80 + "\n")

    resources_dir = Path("upsales/resources")
    renamed_resources = {}

    for old_name, new_name in RESOURCE_RENAMES.items():
        old_path = resources_dir / old_name
        new_path = rename_file(old_path, new_name, dry_run)
        if new_path:
            renamed_resources[old_name] = new_name

    # Step 3: Fix class names in model files
    print("\n" + "-" * 80)
    print("STEP 3: Fix Class Names in Model Files")
    print("-" * 80 + "\n")

    total_class_fixes = 0
    for model_file in models_dir.glob("*.py"):
        if model_file.name in ("__init__.py", "base.py"):
            continue
        fixes = fix_class_names_in_file(model_file, dry_run)
        total_class_fixes += fixes

    print(f"\n   Total class name fixes: {total_class_fixes}")

    # Step 4: Fix class names in resource files
    print("\n" + "-" * 80)
    print("STEP 4: Fix Class Names in Resource Files")
    print("-" * 80 + "\n")

    for resource_file in resources_dir.glob("*.py"):
        if resource_file.name in ("__init__.py", "base.py"):
            continue
        fix_class_names_in_file(resource_file, dry_run)

    # Step 5: Update imports in __init__.py files
    print("\n" + "-" * 80)
    print("STEP 5: Update __init__.py Import Statements")
    print("-" * 80 + "\n")

    # Models __init__.py
    models_init = models_dir / "__init__.py"
    for old_name, new_name in renamed_models.items():
        old_module = old_name.replace(".py", "")
        new_module = new_name.replace(".py", "")
        update_imports_in_file(models_init, old_module, new_module, dry_run)

    # Resources __init__.py
    resources_init = resources_dir / "__init__.py"
    for old_name, new_name in renamed_resources.items():
        old_module = old_name.replace(".py", "")
        new_module = new_name.replace(".py", "")
        update_imports_in_file(resources_init, old_module, new_module, dry_run)

    # Step 6: Update client.py attributes
    print("\n" + "-" * 80)
    print("STEP 6: Update client.py Attributes")
    print("-" * 80 + "\n")

    update_client_attributes(dry_run)

    # Step 7: Update test files
    print("\n" + "-" * 80)
    print("STEP 7: Update Test File Imports")
    print("-" * 80 + "\n")

    tests_dir = Path("tests")
    for test_file in tests_dir.rglob("*.py"):
        for old_name, new_name in {**renamed_models, **renamed_resources}.items():
            old_module = old_name.replace(".py", "")
            new_module = new_name.replace(".py", "")
            update_imports_in_file(test_file, old_module, new_module, dry_run)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80 + "\n")

    print(f"   Model files to rename: {len(renamed_models)}")
    print(f"   Resource files to rename: {len(renamed_resources)}")
    print(f"   Class name fixes: {total_class_fixes}")
    print()

    if dry_run:
        print("✅ DRY RUN COMPLETE")
        print("\n   Review the changes above.")
        print("   Run with --execute to apply changes:")
        print("   python scripts/standardize_naming.py --execute")
    else:
        print("✅ REFACTORING COMPLETE")
        print("\n   Next steps:")
        print("   1. Run tests: uv run pytest")
        print("   2. Run linting: uv run ruff format . && uv run ruff check .")
        print("   3. Run type checking: uv run mypy upsales")
        print("   4. Commit changes: git add -A && git commit -m 'Standardize naming conventions'")
        print("   5. Update CHANGELOG.md with breaking changes note")

    print()


if __name__ == "__main__":
    main()
