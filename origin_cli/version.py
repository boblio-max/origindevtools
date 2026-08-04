"""version

Parsing and validation of package version constraints.

Supported package spec formats::

    numpy            any version
    numpy@1.2.3      exactly version 1.2.3
    numpy>=1.2.0     version 1.2.0 or newer
    numpy<=2.0.0     version 2.0.0 or older
    numpy^2.1        compatible with 2.x (>=2.1.0, <3.0.0)

Invalid syntax raises :class:`VersionError` with a clear message.
"""

import re
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import Optional

__all__ = [
    "ConstraintType",
    "Version",
    "PackageSpec",
    "VersionError",
    "parse_package_spec",
]

_VERSION_RE = re.compile(
    r"^(?P<core>[0-9]+(?:\.[0-9]+)*)"
    r"(?:-(?P<pre>[0-9A-Za-z][0-9A-Za-z.\-]*))?"
    r"(?:\+(?P<build>[0-9A-Za-z][0-9A-Za-z.\-]*))?$"
)

_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.\-]*")

_OPS = ("@", ">=", "<=", ">", "<", "==", "^")


class VersionError(ValueError):
    """Raised when a package spec or version string is invalid."""


class ConstraintType(Enum):
    """The kind of version constraint expressed by a package spec."""

    NONE = "none"
    EXACT = "@"
    EQ = "=="
    GE = ">="
    LE = "<="
    GT = ">"
    LT = "<"
    CARET = "^"


_SYMBOL_TO_TYPE = {
    "@": ConstraintType.EXACT,
    "==": ConstraintType.EQ,
    ">=": ConstraintType.GE,
    "<=": ConstraintType.LE,
    ">": ConstraintType.GT,
    "<": ConstraintType.LT,
    "^": ConstraintType.CARET,
}


@total_ordering
class Version:
    """A parsed, comparable version such as ``1.2.3`` or ``2.1.0-rc1``.

    Comparison follows semantic-versioning precedence: the dotted numeric
    core dominates, a pre-release sorts before its release, and build
    metadata is ignored.
    """

    def __init__(self, raw: str):
        match = _VERSION_RE.fullmatch(raw.strip())
        if not match:
            raise VersionError(
                f"invalid version '{raw}' (expected a dotted number like 1.2.3, "
                "optionally with -prerelease or +build metadata)"
            )
        self.core = tuple(int(part) for part in match.group("core").split("."))
        self.pre = match.group("pre")
        self.build = match.group("build")

    def __str__(self):
        text = ".".join(str(part) for part in self.core)
        if self.pre:
            text += "-" + self.pre
        if self.build:
            text += "+" + self.build
        return text

    def _cmp_key(self):
        if self.pre is None:
            pre_key = (1,)
        else:
            pre_key = (0, self.pre)
        return self.core, pre_key

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._cmp_key() == other._cmp_key()

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self._cmp_key() < other._cmp_key()

    def __hash__(self):
        return hash(self._cmp_key())


@dataclass(frozen=True)
class PackageSpec:
    """A parsed package name plus optional version constraint.

    Attributes:
        name: The package name.
        constraint: The constraint type (``ConstraintType.NONE`` when the
            spec had no version part).
        version: The parsed :class:`Version`, or ``None`` for ``name`` alone.
        raw: The original spec text as typed.
    """

    name: str
    constraint: ConstraintType = ConstraintType.NONE
    version: Optional[Version] = None
    raw: str = ""

    @property
    def has_constraint(self) -> bool:
        return self.constraint is not ConstraintType.NONE


def parse_package_spec(spec: str) -> PackageSpec:
    """Parse a package spec string into a :class:`PackageSpec`.

    Args:
        spec: One of ``name``, ``name@version``, ``name>=version``,
            ``name<=version``, ``name^version`` (plus ``>``, ``<``, ``==``).

    Returns:
        A parsed :class:`PackageSpec`.

    Raises:
        VersionError: If the spec or its version constraint is invalid.
    """
    if not isinstance(spec, str):
        raise VersionError(
            f"Invalid package spec {spec!r}: expected a string"
        )
    text = spec.strip()
    if not text:
        raise VersionError("Invalid package spec '': a package name is required")

    name_match = _NAME_RE.match(text)
    if not name_match:
        raise VersionError(
            f"Invalid package spec '{text}': package name must start with a "
            "letter or underscore"
        )
    name = name_match.group(0)
    rest = text[name_match.end():]
    if not rest:
        return PackageSpec(name=name, raw=text)

    if not any(rest.startswith(op) for op in _OPS):
        raise VersionError(
            f"Invalid version constraint in '{text}': expected one of "
            "@, >=, <=, >, <, ==, ^ after the package name"
        )

    operator = None
    for op in ("==", ">=", "<="):
        if rest.startswith(op):
            operator = op
            break
    if operator is None:
        operator = rest[0]

    version_text = rest[len(operator):]
    if not version_text:
        raise VersionError(
            f"Invalid version constraint in '{text}': missing version after '{operator}'"
        )

    try:
        version = Version(version_text)
    except VersionError as exc:
        raise VersionError(
            f"Invalid version constraint in '{text}': {exc}"
        ) from exc

    return PackageSpec(
        name=name,
        constraint=_SYMBOL_TO_TYPE[operator],
        version=version,
        raw=text,
    )
