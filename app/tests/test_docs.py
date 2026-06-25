import pathlib
import tomllib
import unittest


APP_DIR = pathlib.Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def test_readmes_match_required_python_version(self):
        pyproject = tomllib.loads((APP_DIR / "pyproject.toml").read_text())
        required_python = pyproject["project"]["requires-python"]
        expected_text = f"Python ≥ {required_python.removeprefix('>=')}"

        for path in (APP_DIR / "README.md", APP_DIR / "docs" / "README-en.md"):
            with self.subTest(path=path):
                self.assertIn(expected_text, path.read_text())


if __name__ == "__main__":
    unittest.main()
