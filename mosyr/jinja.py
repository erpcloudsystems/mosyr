
import frappe

def get_translation(word, target_lang="en"):
    if not word:
        return "  "

    translations = frappe.get_all(
        "Translation", pluck="translated_text",
        filters={"language": target_lang, "source_text": str(word).strip()},
        order_by="creation DESC"
    )
    if not any(translations):
        return word

    return translations[0]
