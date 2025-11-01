#!/usr/bin/env python3
"""
Development Setup Script for Kometa MediUX Resolver

This script provides convenient development commands for the project.
Run with -h to see all available commands.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description="", exit_on_error=True):
    """Run a shell command with nice output."""
    print(f"🔧 {description}")
    print(f"   Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")

    result = subprocess.run(cmd, shell=isinstance(cmd, str))

    if result.returncode != 0 and exit_on_error:
        print(f"❌ Command failed with exit code {result.returncode}")
        sys.exit(1)
    elif result.returncode == 0:
        print(f"✅ {description} completed successfully")

    return result


def setup_environment():
    """Install all dependencies."""
    print("🚀 Setting up development environment...")

    # Install main dependencies
    run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Installing main dependencies",
    )

    # Install development dependencies
    dev_deps = [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
        "coverage>=7.0.0",
        "responses>=0.23.0",
        "black>=22.0.0",
        "isort>=5.10.0",
        "flake8>=5.0.0",
        "mypy>=1.0.0",
        "bandit>=1.7.0",
        "pre-commit>=2.20.0",
    ]

    run_command(
        [sys.executable, "-m", "pip", "install"] + dev_deps, "Installing development dependencies"
    )

    # Setup pre-commit hooks
    run_command(
        [sys.executable, "-m", "pre_commit", "install"],
        "Installing pre-commit hooks",
        exit_on_error=False,
    )

    print("🎉 Development environment setup complete!")


def run_tests(coverage=False, fast=False):
    """Run the test suite."""
    cmd = [sys.executable, "-m", "pytest"]

    if fast:
        cmd.extend(["-m", "not selenium"])
        print("⚡ Running fast tests (excluding selenium)...")
    else:
        print("🧪 Running full test suite...")

    if coverage:
        cmd.extend(
            ["--cov=.", "--cov-report=term-missing", "--cov-report=html", "--cov-report=xml"]
        )
        print("📊 Including coverage reporting...")

    cmd.extend(["-v"])

    result = run_command(cmd, "Running tests", exit_on_error=False)

    if coverage and result.returncode == 0:
        print("📈 Coverage report generated in htmlcov/index.html")

    return result.returncode == 0


def run_linting():
    """Run all linting tools."""
    print("🔍 Running code quality checks...")

    tools = [
        ([sys.executable, "-m", "black", "--check", "."], "Black formatting check"),
        ([sys.executable, "-m", "isort", "--check-only", "."], "Import sorting check"),
        ([sys.executable, "-m", "flake8", "."], "Flake8 linting"),
        ([sys.executable, "-m", "mypy", "kometa_mediux_resolver.py"], "MyPy type checking"),
        ([sys.executable, "-m", "bandit", "-r", ".", "-f", "json"], "Security scanning"),
    ]

    all_passed = True
    for cmd, description in tools:
        result = run_command(cmd, description, exit_on_error=False)
        if result.returncode != 0:
            all_passed = False

    if all_passed:
        print("✅ All quality checks passed!")
    else:
        print("❌ Some quality checks failed")

    return all_passed


def format_code():
    """Format code with black and isort."""
    print("🎨 Formatting code...")

    run_command([sys.executable, "-m", "black", "."], "Formatting with Black")
    run_command([sys.executable, "-m", "isort", "."], "Sorting imports with isort")

    print("✨ Code formatting complete!")


def run_security_scan():
    """Run security scanning."""
    print("🔒 Running security scans...")

    run_command(
        [sys.executable, "-m", "bandit", "-r", ".", "-ll"],
        "Security scanning with Bandit",
        exit_on_error=False,
    )


def main():
    parser = argparse.ArgumentParser(description="Development tools for Kometa MediUX Resolver")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Setup command
    subparsers.add_parser(
        "setup", help="Install all dependencies and setup development environment"
    )

    # Test commands
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--coverage", action="store_true", help="Include coverage reporting")
    test_parser.add_argument(
        "--fast", action="store_true", help="Skip selenium tests for faster execution"
    )

    # Quality commands
    subparsers.add_parser("lint", help="Run all linting tools")
    subparsers.add_parser("format", help="Format code with black and isort")
    subparsers.add_parser("security", help="Run security scanning")

    # Convenience commands
    subparsers.add_parser("check-all", help="Run tests, linting, and security checks")
    subparsers.add_parser("dev-test", help="Quick development test (fast tests with coverage)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Change to project directory
    project_root = Path(__file__).parent.absolute()
    import os

    os.chdir(project_root)

    if args.command == "setup":
        setup_environment()

    elif args.command == "test":
        success = run_tests(coverage=args.coverage, fast=args.fast)
        sys.exit(0 if success else 1)

    elif args.command == "lint":
        success = run_linting()
        sys.exit(0 if success else 1)

    elif args.command == "format":
        format_code()

    elif args.command == "security":
        run_security_scan()

    elif args.command == "check-all":
        print("🔄 Running comprehensive quality checks...")

        test_success = run_tests(coverage=True, fast=False)
        lint_success = run_linting()

        print("\n📋 Summary:")
        print(f"   Tests: {'✅ PASSED' if test_success else '❌ FAILED'}")
        print(f"   Linting: {'✅ PASSED' if lint_success else '❌ FAILED'}")

        if test_success and lint_success:
            print("🎉 All checks passed! Ready for production.")
            sys.exit(0)
        else:
            print("❌ Some checks failed. Please fix issues before committing.")
            sys.exit(1)

    elif args.command == "dev-test":
        print("⚡ Running quick development tests...")
        success = run_tests(coverage=True, fast=True)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
