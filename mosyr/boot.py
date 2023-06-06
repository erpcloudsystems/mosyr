from mosyr.api import custom_get_letter_heads

def boot_session(bootinfo):
    bootinfo.letter_heads = custom_get_letter_heads()