from __future__ import annotations

from dataclasses import dataclass

from deep_translator import GoogleTranslator


@dataclass(slots=True)
class TranslationResult:
    text: str
    applied: bool
    mode: str


class TextTranslator:
    def translate(self, text: str, mode: str) -> TranslationResult:
        if not text or mode == "off":
            return TranslationResult(text=text, applied=False, mode="off")

        if mode == "de_to_en":
            translated = GoogleTranslator(source="de", target="en").translate(text)
            return TranslationResult(text=translated or text, applied=True, mode=mode)

        if mode == "en_to_de":
            translated = GoogleTranslator(source="en", target="de").translate(text)
            return TranslationResult(text=translated or text, applied=True, mode=mode)

        return TranslationResult(text=text, applied=False, mode="off")
