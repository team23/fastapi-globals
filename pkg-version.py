import sys

import tomlkit

if __name__ == "__main__":
    if len(sys.argv) not in (1, 2):
        raise RuntimeError("Usage: python pkg-version.py [version]")

    if len(sys.argv) == 2:
        version = sys.argv[1]

        with open("pyproject.toml", "rb") as f:
            pyproject_toml = tomlkit.parse(f.read())

        pyproject_toml["project"]["version"] = version

        with open("pyproject.toml", "w") as f:
            f.write(tomlkit.dumps(pyproject_toml))
    else:
        with open("pyproject.toml", "rb") as f:
            pyproject_toml = tomlkit.parse(f.read())

        version = pyproject_toml["project"]["version"]
        print(version)
