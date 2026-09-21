from core.context import CommandContext
from core.registry import command

_BASE_PAIRS = [
    ("q", "й"),
    ("w", "ц"),
    ("e", "у"),
    ("r", "к"),
    ("t", "е"),
    ("y", "н"),
    ("u", "г"),
    ("i", "ш"),
    ("o", "щ"),
    ("p", "з"),
    ("a", "ф"),
    ("s", "ы"),
    ("d", "в"),
    ("f", "а"),
    ("g", "п"),
    ("h", "р"),
    ("j", "о"),
    ("k", "л"),
    ("l", "д"),
    ("z", "я"),
    ("x", "ч"),
    ("c", "с"),
    ("v", "м"),
    ("b", "и"),
    ("n", "т"),
    ("m", "ь"),
]

EN_TO_RU = {}
for en_char, ru_char in _BASE_PAIRS:
    EN_TO_RU[en_char] = ru_char
    EN_TO_RU[en_char.upper()] = ru_char.upper()

EN_TO_RU.update(
    {
        "`": "ё",
        "~": "Ё",
        "[": "х",
        "]": "ъ",
        "{": "Х",
        "}": "Ъ",
        ";": "ж",
        "'": "э",
        ":": "Ж",
        '"': "Э",
        ",": "б",
        ".": "ю",
        "<": "Б",
        ">": "Ю",
        "/": ".",
        "?": ",",
    }
)

RU_TO_EN = {ru_char: en_char for en_char, ru_char in EN_TO_RU.items()}


def switch_layout(text: str) -> str:
    result = []
    for char in text:
        if char in EN_TO_RU:
            result.append(EN_TO_RU[char])
        elif char in RU_TO_EN:
            result.append(RU_TO_EN[char])
        else:
            result.append(char)
    return "".join(result)


@command(name="sw", module="sw", description="Переключает раскладку в сообщении")
async def cmd_sw(ctx: CommandContext):
    target = ctx.message.reply_to_message
    if not target:
        return

    original = target.text or target.caption
    if not original:
        return

    converted = switch_layout(original)

    await ctx.delete_command_message()
    await ctx.reply(converted)
