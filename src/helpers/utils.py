def bump_version(version: str, bump: str) -> str:
    major, minor = map(int, version.split("."))
    if bump == "major":
        major += 1
        minor = 0
    else:
        minor += 1
    return f"{major}.{minor}"