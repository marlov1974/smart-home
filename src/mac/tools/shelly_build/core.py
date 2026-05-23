"""Deterministic Shelly build and deploy artifact generation."""

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_MAX_CHUNK_BYTES = 12_000
RECIPE_VERSION = 1


class BuildError(Exception):
    """Raised when Shelly build or validation fails."""


@dataclass(frozen=True)
class BuildResult:
    """Paths generated for one built Shelly role."""

    role: str
    built_path: Path
    chunk_paths: tuple[Path, ...]
    recipe_path: Path


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _byte_len(text: str) -> int:
    return len(text.encode("utf-8"))


def _numeric_chunk_name(index: int) -> str:
    return f"{index:02d}.js"


def _safe_source_path(manifest_dir: Path, raw_path: str) -> Path:
    if not isinstance(raw_path, str) or not raw_path:
        raise BuildError("source path must be a non-empty string")

    source_path = Path(raw_path)
    if source_path.is_absolute():
        raise BuildError(f"absolute source path is not allowed: {raw_path}")

    resolved_base = manifest_dir.resolve()
    resolved_path = (manifest_dir / source_path).resolve()
    if resolved_path != resolved_base and resolved_base not in resolved_path.parents:
        raise BuildError(f"source path escapes manifest directory: {raw_path}")
    if not resolved_path.is_file():
        raise BuildError(f"source file does not exist: {raw_path}")
    return resolved_path


def _script_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    scripts = manifest.get("scripts")
    if not isinstance(scripts, list) or not scripts:
        raise BuildError("manifest must contain a non-empty scripts list")
    for script in scripts:
        if not isinstance(script, dict):
            raise BuildError("each script entry must be an object")
        role = script.get("role")
        sources = script.get("sources")
        if not isinstance(role, str) or not role:
            raise BuildError("script role must be a non-empty string")
        if "/" in role or "\\" in role or role in {".", ".."}:
            raise BuildError(f"invalid role name: {role}")
        if not isinstance(sources, list) or not sources:
            raise BuildError(f"script {role} must contain a non-empty sources list")
    return scripts


def load_manifest(manifest_path: str | Path) -> dict[str, Any]:
    """Read and validate a Shelly build manifest."""

    path = Path(manifest_path)
    try:
        manifest = json.loads(_read_text(path))
    except FileNotFoundError as exc:
        raise BuildError(f"manifest does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise BuildError(f"manifest is not valid JSON: {path}") from exc

    if not isinstance(manifest, dict):
        raise BuildError("manifest root must be an object")
    _script_entries(manifest)
    return manifest


def build_script(manifest_path: str | Path, script: dict[str, Any]) -> tuple[str, str]:
    """Build one complete script from explicit source files."""

    manifest_dir = Path(manifest_path).parent
    role = script["role"]
    parts = []
    for raw_source in script["sources"]:
        source_path = _safe_source_path(manifest_dir, raw_source)
        text = _read_text(source_path)
        parts.append(text.rstrip("\n"))
    return role, "\n\n".join(parts) + "\n"


def chunk_text(text: str, max_chunk_bytes: int = DEFAULT_MAX_CHUNK_BYTES) -> list[str]:
    """Split text into deterministic chunks without exceeding byte limit."""

    if max_chunk_bytes < 1:
        raise BuildError("max chunk bytes must be positive")
    if text == "":
        return [""]

    chunks: list[str] = []
    current = ""
    lines = text.splitlines(keepends=True)

    for line in lines:
        if _byte_len(line) > max_chunk_bytes:
            raise BuildError("one source line exceeds max chunk bytes")
        candidate = current + line
        if current and _byte_len(candidate) > max_chunk_bytes:
            chunks.append(current)
            current = line
        else:
            current = candidate

    if current:
        chunks.append(current)
    return chunks


def write_built_script(build_root: str | Path, role: str, script_text: str) -> Path:
    """Write one complete built Shelly script."""

    built_path = Path(build_root) / f"{role}.js"
    _write_text(built_path, script_text)
    return built_path


def write_chunks(dep_root: str | Path, role: str, chunks: Iterable[str]) -> tuple[Path, ...]:
    """Write ordered numeric deploy chunks for one role."""

    chunk_dir = Path(dep_root) / "ch" / role
    if chunk_dir.exists():
        shutil.rmtree(chunk_dir)
    chunk_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_path = chunk_dir / _numeric_chunk_name(index)
        _write_text(chunk_path, chunk)
        paths.append(chunk_path)
    return tuple(paths)


def write_recipe(dep_root: str | Path, role: str, chunk_count: int) -> Path:
    """Write compact recipe JSON for one role."""

    recipe_path = Path(dep_root) / "rec" / f"{role}.json"
    recipe = {"v": RECIPE_VERSION, "n": chunk_count}
    _write_text(recipe_path, json.dumps(recipe, separators=(",", ":")) + "\n")
    return recipe_path


def validate_role(
    build_root: str | Path,
    dep_root: str | Path,
    role: str,
    max_chunk_bytes: int = DEFAULT_MAX_CHUNK_BYTES,
) -> None:
    """Validate chunk recipe, chunk sizes and exact reconstruction."""

    built_path = Path(build_root) / f"{role}.js"
    recipe_path = Path(dep_root) / "rec" / f"{role}.json"
    chunk_dir = Path(dep_root) / "ch" / role

    if not built_path.is_file():
        raise BuildError(f"built script missing: {built_path}")
    if not recipe_path.is_file():
        raise BuildError(f"recipe missing: {recipe_path}")
    if not chunk_dir.is_dir():
        raise BuildError(f"chunk directory missing: {chunk_dir}")

    try:
        recipe = json.loads(_read_text(recipe_path))
    except json.JSONDecodeError as exc:
        raise BuildError(f"recipe is not valid JSON: {recipe_path}") from exc

    if recipe.get("v") != RECIPE_VERSION:
        raise BuildError(f"unsupported recipe version for {role}")
    chunk_count = recipe.get("n")
    if not isinstance(chunk_count, int) or chunk_count < 1:
        raise BuildError(f"invalid recipe chunk count for {role}")

    chunks = []
    for index in range(1, chunk_count + 1):
        chunk_path = chunk_dir / _numeric_chunk_name(index)
        if not chunk_path.is_file():
            raise BuildError(f"chunk missing: {chunk_path}")
        chunk = _read_text(chunk_path)
        if _byte_len(chunk) > max_chunk_bytes:
            raise BuildError(f"chunk exceeds max bytes: {chunk_path}")
        chunks.append(chunk)

    reconstructed = "".join(chunks)
    if reconstructed != _read_text(built_path):
        raise BuildError(f"chunks do not reconstruct built script for {role}")


def build_from_manifest(
    manifest_path: str | Path,
    build_root: str | Path,
    dep_root: str | Path,
    max_chunk_bytes: int = DEFAULT_MAX_CHUNK_BYTES,
) -> list[BuildResult]:
    """Build every script in a manifest and validate generated artifacts."""

    manifest = load_manifest(manifest_path)
    results = []
    for script in _script_entries(manifest):
        role, script_text = build_script(manifest_path, script)
        chunks = chunk_text(script_text, max_chunk_bytes)
        built_path = write_built_script(build_root, role, script_text)
        chunk_paths = write_chunks(dep_root, role, chunks)
        recipe_path = write_recipe(dep_root, role, len(chunk_paths))
        validate_role(build_root, dep_root, role, max_chunk_bytes)
        results.append(BuildResult(role, built_path, chunk_paths, recipe_path))
    return results


def main(argv: list[str] | None = None) -> int:
    """Run Shelly build tooling from the command line."""

    parser = argparse.ArgumentParser(prog="python3 -m src.mac.tools.shelly_build")
    parser.add_argument("--max-chunk-bytes", type=int, default=DEFAULT_MAX_CHUNK_BYTES)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--manifest", required=True)
    build_parser.add_argument("--build-root", required=True)
    build_parser.add_argument("--dep-root", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("--build-root", required=True)
    validate_parser.add_argument("--dep-root", required=True)
    validate_parser.add_argument("--role", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            results = build_from_manifest(
                args.manifest,
                args.build_root,
                args.dep_root,
                args.max_chunk_bytes,
            )
            for result in results:
                print(f"built {result.role}: {len(result.chunk_paths)} chunks")
            return 0
        if args.command == "validate":
            validate_role(args.build_root, args.dep_root, args.role, args.max_chunk_bytes)
            print(f"valid {args.role}")
            return 0
    except BuildError as exc:
        print(f"error: {exc}")
        return 1

    return 1
