"""Tests for package version constraint parsing, storage, and validation."""

import json
import os
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from .classes import AINode, ConnectorListNode, GiveNode, InstallNode
from .install_pkg import _record_install, install_pkg
from .lexer import lex
from .parser import Parser
from .version import (
    ConstraintType,
    PackageSpec,
    Version,
    VersionError,
    parse_package_spec,
)


class TestParsePackageSpec(unittest.TestCase):
    """Each supported spec format parses into the expected data structure."""

    def test_plain_name(self):
        spec = parse_package_spec("numpy")
        self.assertEqual(spec.name, "numpy")
        self.assertIs(spec.constraint, ConstraintType.NONE)
        self.assertIsNone(spec.version)
        self.assertFalse(spec.has_constraint)
        self.assertEqual(spec.raw, "numpy")

    def test_exact_at(self):
        spec = parse_package_spec("numpy@1.2.3")
        self.assertEqual(spec.name, "numpy")
        self.assertIs(spec.constraint, ConstraintType.EXACT)
        self.assertEqual(str(spec.version), "1.2.3")
        self.assertTrue(spec.has_constraint)

    def test_minimum_ge(self):
        spec = parse_package_spec("numpy>=1.2.0")
        self.assertEqual(spec.name, "numpy")
        self.assertIs(spec.constraint, ConstraintType.GE)
        self.assertEqual(str(spec.version), "1.2.0")

    def test_maximum_le(self):
        spec = parse_package_spec("numpy<=2.0.0")
        self.assertEqual(spec.name, "numpy")
        self.assertIs(spec.constraint, ConstraintType.LE)
        self.assertEqual(str(spec.version), "2.0.0")

    def test_caret(self):
        spec = parse_package_spec("numpy^2.1")
        self.assertEqual(spec.name, "numpy")
        self.assertIs(spec.constraint, ConstraintType.CARET)
        self.assertEqual(str(spec.version), "2.1")

    def test_extra_operators(self):
        self.assertIs(parse_package_spec("numpy>1.0").constraint, ConstraintType.GT)
        self.assertIs(parse_package_spec("numpy<3").constraint, ConstraintType.LT)
        self.assertIs(parse_package_spec("numpy==1.2.3").constraint, ConstraintType.EQ)

    def test_whitespace_trimmed(self):
        spec = parse_package_spec("  numpy>=1.2.0  ")
        self.assertEqual(spec.name, "numpy")
        self.assertEqual(str(spec.version), "1.2.0")

    def test_pre_release_and_build(self):
        spec = parse_package_spec("numpy@1.2.3-rc1+build.5")
        self.assertEqual(str(spec.version), "1.2.3-rc1+build.5")

    def test_dashed_and_dotted_names(self):
        self.assertEqual(parse_package_spec("scikit-learn>=1.0").name, "scikit-learn")
        self.assertEqual(parse_package_spec("foo.bar@1.0").name, "foo.bar")


class TestParseInvalidSpec(unittest.TestCase):
    """Invalid constraint syntax is rejected with a clear error."""

    def assert_invalid(self, spec, needle=None):
        with self.assertRaises(VersionError) as ctx:
            parse_package_spec(spec)
        message = str(ctx.exception)
        if needle is not None:
            self.assertIn(needle, message)

    def test_empty(self):
        self.assert_invalid("")

    def test_missing_version_after_at(self):
        self.assert_invalid("numpy@", "missing version")

    def test_missing_version_after_ge(self):
        self.assert_invalid("numpy>=", "missing version")

    def test_missing_version_after_caret(self):
        self.assert_invalid("numpy^", "missing version")

    def test_non_numeric_version(self):
        self.assert_invalid("numpy>=abc", "invalid version")

    def test_invalid_version_character(self):
        self.assert_invalid("numpy@1.2.x", "invalid version")

    def test_compound_constraint_rejected(self):
        self.assert_invalid("numpy>=1.2.0,<2.0", "invalid version")

    def test_unsupported_operator(self):
        self.assert_invalid("numpy~1.2", "expected one of")

    def test_no_operator_with_version(self):
        self.assert_invalid("numpy 1.2", "expected one of")

    def test_name_must_start_with_letter(self):
        self.assert_invalid("1numpy@1.0", "package name must start")

    def test_leading_operator_only(self):
        self.assert_invalid(">=1.0", "package name must start")

    def test_not_a_string(self):
        self.assert_invalid(None)


class TestVersion(unittest.TestCase):
    def test_str_round_trip(self):
        self.assertEqual(str(Version("1.2.3")), "1.2.3")
        self.assertEqual(str(Version("2.1")), "2.1")
        self.assertEqual(str(Version("1.2.3-rc1+build.5")), "1.2.3-rc1+build.5")

    def test_invalid_version(self):
        with self.assertRaises(VersionError):
            Version("abc")
        with self.assertRaises(VersionError):
            Version("1..2")
        with self.assertRaises(VersionError):
            Version("")

    def test_comparison(self):
        self.assertLess(Version("1.2.0"), Version("1.2.1"))
        self.assertLess(Version("1.2"), Version("1.2.1"))
        self.assertLess(Version("1.2.3-rc1"), Version("1.2.3"))
        self.assertGreater(Version("2.0.0"), Version("1.9.9"))
        self.assertEqual(Version("1.2.3"), Version("1.2.3"))
        self.assertLessEqual(Version("1.0"), Version("1.0"))


class TestLexerAndParser(unittest.TestCase):
    def spec_value_of(self, line):
        tokens = lex([line])
        spec_tokens = [t for t in tokens if t.type == "SPEC"]
        self.assertEqual(len(spec_tokens), 1, tokens)
        return spec_tokens[0].value

    def test_spec_lexed_as_single_token(self):
        for line, expected in [
            ("origin install numpy", "numpy"),  # no constraint -> IDENT, no SPEC
            ("origin install numpy@1.2.3", "numpy@1.2.3"),
            ("origin install numpy>=1.2.0", "numpy>=1.2.0"),
            ("origin install numpy<=2.0.0", "numpy<=2.0.0"),
            ("origin install numpy^2.1", "numpy^2.1"),
        ]:
            tokens = lex([line])
            if expected == "numpy":
                self.assertNotIn("SPEC", [t.type for t in tokens])
                idents = [t.value for t in tokens if t.type == "IDENT"]
                self.assertIn("numpy", idents)
            else:
                self.assertEqual(self.spec_value_of(line), expected)

    def test_parser_passes_full_spec(self):
        for line, expected in [
            ("origin install numpy", "numpy"),
            ("origin install numpy@1.2.3", "numpy@1.2.3"),
            ("origin install numpy>=1.2.0", "numpy>=1.2.0"),
            ("origin install numpy<=2.0.0", "numpy<=2.0.0"),
            ("origin install numpy^2.1", "numpy^2.1"),
        ]:
            node = Parser(lex([line])).command()
            self.assertIsInstance(node, InstallNode)
            self.assertEqual(node.lang, expected)


class TestInstalledJson(unittest.TestCase):
    """Parsed constraints are stored in installed.json."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.venv_root = self._tmp.name
        self._old_env = os.environ.get("ORIGIN_ENV")
        os.environ["ORIGIN_ENV"] = self.venv_root

    def tearDown(self):
        if self._old_env is None:
            os.environ.pop("ORIGIN_ENV", None)
        else:
            os.environ["ORIGIN_ENV"] = self._old_env

    def installed(self):
        path = os.path.join(self.venv_root, "installed.json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_record_install_stores_constraint(self):
        spec = parse_package_spec("numpy^2.1")
        _record_install(self.venv_root, spec, "https://example.test", os.path.join(self.venv_root, "pkg"))
        data = self.installed()
        entry = data["numpy"]
        self.assertEqual(entry["spec"], "numpy^2.1")
        self.assertEqual(entry["constraint"], "^")
        self.assertEqual(entry["version"], "2.1")

    def test_record_install_plain_name(self):
        spec = parse_package_spec("calc")
        _record_install(self.venv_root, spec, "https://example.test", os.path.join(self.venv_root, "pkg"))
        entry = self.installed()["calc"]
        self.assertNotIn("constraint", entry)
        self.assertNotIn("version", entry)
        self.assertEqual(entry["spec"], "calc")

    @patch("origin_cli.install_pkg.in_venv", return_value=True)
    @patch("origin_cli.install_pkg._resolve", return_value="https://example.test/pkg.zip")
    @patch("origin_cli.install_pkg._download")
    def test_install_pkg_end_to_end(self, download, _resolve, _in_venv):
        def fake_download(url, dest):
            with zipfile.ZipFile(dest, "w") as zf:
                zf.writestr("calc-pkg/manifest.toml", "[package]\nname = 'calc'\n")
        download.side_effect = fake_download

        install_pkg("calc@1.2.3")

        entry = self.installed()["calc"]
        self.assertEqual(entry["constraint"], "@")
        self.assertEqual(entry["version"], "1.2.3")
        self.assertTrue(os.path.isdir(os.path.join(self.venv_root, "packages", "calc")))

    @patch("origin_cli.install_pkg.in_venv", return_value=True)
    def test_install_pkg_rejects_invalid_spec(self, _in_venv):
        with patch("origin_cli.install_pkg._resolve") as resolve:
            install_pkg("numpy>=1.x")
            resolve.assert_not_called()
        self.assertFalse(os.path.exists(os.path.join(self.venv_root, "installed.json")))


class TestAIParsing(unittest.TestCase):
    """origin run / give / connector statements parse into the right nodes."""

    def test_run_model_with_dot(self):
        node = Parser(lex(["origin run llama3.2"])).command()
        self.assertIsInstance(node, AINode)
        self.assertEqual(node.model, "llama3.2")

    def test_run_model_plain_name(self):
        node = Parser(lex(["origin run llama3"])).command()
        self.assertIsInstance(node, AINode)
        self.assertEqual(node.model, "llama3")

    def test_give_with_connectors(self):
        node = Parser(lex(["origin give llama3.2 origin"])).command()
        self.assertIsInstance(node, GiveNode)
        self.assertEqual(node.model, "llama3.2")
        self.assertEqual(node.connectors, ["origin"])

    def test_give_no_connectors(self):
        node = Parser(lex(["origin give llama3.2"])).command()
        self.assertIsInstance(node, GiveNode)
        self.assertEqual(node.model, "llama3.2")
        self.assertEqual(node.connectors, [])

    def test_connector_list(self):
        node = Parser(lex(["origin connector list"])).command()
        self.assertIsInstance(node, ConnectorListNode)


class TestConnectorRegistry(unittest.TestCase):
    """The connector registry attaches connectors to models."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._old_env = os.environ.get("ORIGIN_CONNECTORS_FILE")
        self.path = os.path.join(self._tmp.name, "connectors.json")
        os.environ["ORIGIN_CONNECTORS_FILE"] = self.path

    def tearDown(self):
        if self._old_env is None:
            os.environ.pop("ORIGIN_CONNECTORS_FILE", None)
        else:
            os.environ["ORIGIN_CONNECTORS_FILE"] = self._old_env

    def test_give_attaches_connector(self):
        from .mcp import give_connectors, load_registry
        give_connectors("llama3.2", ["origin"])
        data = load_registry()
        self.assertEqual(data["given"]["llama3.2"], ["origin"])

    def test_give_unknown_connector(self):
        from .mcp import give_connectors, load_registry
        give_connectors("llama3.2", ["does-not-exist"])
        data = load_registry()
        self.assertNotIn("llama3.2", data.get("given", {}))

    def test_give_lists_attachments(self):
        from .mcp import give_connectors, load_registry
        give_connectors("llama3.2", ["origin"])
        give_connectors("llama3.2", [])
        data = load_registry()
        self.assertEqual(data["given"]["llama3.2"], ["origin"])


if __name__ == "__main__":
    unittest.main()
