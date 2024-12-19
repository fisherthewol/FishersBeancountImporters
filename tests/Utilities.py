from pathlib import Path


def GetTestFilesDir():
    cwd = Path.cwd()
    match cwd.parts[-1]:
        case "tests":
            return Path("./TestFiles")
        case "BeancountImporters":
            return Path("./tests/TestFiles")
        case _:
            raise ValueError("Current Working Directory isn't the right place.")