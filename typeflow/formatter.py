from __future__ import annotations

import re
from dataclasses import dataclass


SPOKEN_COMMANDS = {
    "new line": "\n",
    "line break": "\n",
    "new paragraph": "\n\n",
    "paragraph break": "\n\n",
    "comma": ",",
    "period": ".",
    "question mark": "?",
    "exclamation mark": "!",
    "colon": ":",
    "semicolon": ";",
    "tab": "\t",
    "neue zeile": "\n",
    "zeilenumbruch": "\n",
    "neuer absatz": "\n\n",
    "absatz": "\n\n",
    "komma": ",",
    "punkt": ".",
    "fragezeichen": "?",
    "ausrufezeichen": "!",
    "doppelpunkt": ":",
    "semikolon": ";",
    "tabulator": "\t",
}

FILLER_WORDS = (
    "uh",
    "um",
    "erm",
    "hmm",
    "like",
    "you know",
    "äh",
    "aeh",
    "ähm",
    "aehm",
    "hm",
    "also",
    "sozusagen",
)


@dataclass(slots=True)
class FormattedText:
    text: str
    applied_commands: list[str]


class OutputFormatter:
    def format(
        self,
        text: str,
        mode: str,
        *,
        remove_fillers: bool = True,
        replacements: dict[str, str] | None = None,
        snippets: dict[str, str] | None = None,
    ) -> FormattedText:
        normalized = self._normalize_whitespace(text)
        if not normalized:
            return FormattedText(text="", applied_commands=[])

        result = normalized
        result = self._apply_phrase_map(result, snippets or {})
        result = self._apply_phrase_map(result, replacements or {})
        if remove_fillers:
            result = self._remove_fillers(result)
        replaced, commands = self._apply_voice_commands(result)

        if mode == "email":
            final_text = self._format_email(replaced)
        elif mode == "chat":
            final_text = self._format_chat(replaced)
        elif mode == "code":
            final_text = self._format_code(replaced)
        else:
            final_text = self._format_normal(replaced)

        return FormattedText(text=final_text, applied_commands=commands)

    def _apply_voice_commands(self, text: str) -> tuple[str, list[str]]:
        commands_found: list[str] = []
        result = text

        for spoken, replacement in sorted(SPOKEN_COMMANDS.items(), key=lambda item: len(item[0]), reverse=True):
            pattern = re.compile(rf"(?<!\S){re.escape(spoken)}(?!\S)", flags=re.IGNORECASE)
            if pattern.search(result):
                commands_found.append(spoken)
                result = pattern.sub(f" {replacement} ", result)

        result = re.sub(r"[ \t]+\n", "\n", result)
        result = re.sub(r"\n[ \t]+", "\n", result)
        result = re.sub(r"[ \t]{2,}", " ", result)
        return result.strip(), commands_found

    def _format_normal(self, text: str) -> str:
        text = self._tighten_punctuation(text)
        text = self._sentence_case(text)
        if text and text[-1] not in ".!?":
            text += "."
        return text

    def _format_email(self, text: str) -> str:
        text = self._tighten_punctuation(text)
        text = self._sentence_case(text)
        text = text.replace("\n\n", "\n\n")
        if text and text[-1] not in ".!?":
            text += "."
        return text

    def _format_chat(self, text: str) -> str:
        text = self._tighten_punctuation(text)
        text = self._sentence_case(text)
        return text

    def _format_code(self, text: str) -> str:
        text = re.sub(r"[ \t]*([,.;:!?])[ \t]*", r"\1", text)
        text = re.sub(r" ?\n ?", "\n", text)
        lines = [line.rstrip() for line in text.splitlines()]
        text = "\n".join(lines)
        return text.strip()

    def _normalize_whitespace(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _apply_phrase_map(self, text: str, mapping: dict[str, str]) -> str:
        result = text
        for spoken, replacement in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
            spoken = spoken.strip()
            if not spoken:
                continue
            pattern = re.compile(rf"(?<!\S){re.escape(spoken)}(?!\S)", flags=re.IGNORECASE)
            result = pattern.sub(replacement, result)
        return result

    def _remove_fillers(self, text: str) -> str:
        result = text
        for filler in sorted(FILLER_WORDS, key=len, reverse=True):
            pattern = re.compile(rf"(?<!\S){re.escape(filler)}(?!\S)", flags=re.IGNORECASE)
            result = pattern.sub(" ", result)
        result = re.sub(r"[ \t]{2,}", " ", result)
        result = re.sub(r"[ \t]+\n", "\n", result)
        result = re.sub(r"\n[ \t]+", "\n", result)
        return result.strip()

    def _tighten_punctuation(self, text: str) -> str:
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)
        text = re.sub(r"([,.;:!?])(?=[^\s\n])", r"\1 ", text)
        text = re.sub(r" ?\n ?", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _sentence_case(self, text: str) -> str:
        if not text:
            return ""

        chars = list(text)
        capitalize_next = True
        for index, char in enumerate(chars):
            if capitalize_next and char.isalpha():
                chars[index] = char.upper()
                capitalize_next = False
            elif char in ".!?\n":
                capitalize_next = True
        return "".join(chars)
