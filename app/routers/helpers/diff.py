from difflib import ndiff


def render_diff(original: str, updated: str) -> list[dict[str, str]]:
    diff_lines = []
    for line in ndiff(original.splitlines(), updated.splitlines()):
        code = line[0]
        text = line[2:]
        diff_lines.append({"op": code, "text": text})
    return diff_lines
