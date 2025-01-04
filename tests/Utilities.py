from pathlib import Path


def GetTestFilesDir():
    cwd = Path.cwd()
    match cwd.parts[-1]:
        case "tests":
            return Path("./TestFiles")
        case "BeancountImporters", "FishersBeancountImporters":
            return Path("./tests/TestFiles")
        case _:
            print(f"cwd: {cwd}")
            raise ValueError("Current Working Directory isn't the right place.")