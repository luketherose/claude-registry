"""Accenture brand constants for python-pptx.

Import this instead of pasting the block into every generation script:
    from pptx_constants import ACC_PURPLE, SLIDE_W, FONT_BODY
Values are generated from assets/brand-tokens.json and must stay in step
with it. Change the JSON first.
"""

from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

ACC_PURPLE      = RGBColor(0xA1, 0x00, 0xFF)
ACC_PURPLE_DARK = RGBColor(0x75, 0x00, 0xC0)
ACC_PURPLE_DK2  = RGBColor(0x46, 0x00, 0x73)
ACC_PURPLE_PINK = RGBColor(0xB4, 0x55, 0xAA)
ACC_PURPLE_LT   = RGBColor(0xBE, 0x82, 0xFF)
ACC_PURPLE_LT2  = RGBColor(0xDC, 0xAF, 0xFF)
ACC_BLACK       = RGBColor(0x00, 0x00, 0x00)
ACC_WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
ACC_GRAY        = RGBColor(0x96, 0x96, 0x8C)
ACC_GRAY_LT     = RGBColor(0xE6, 0xE6, 0xDC)

SLIDE_W      = Inches(13.33)
SLIDE_H      = Inches(7.50)
FONT_BODY    = "Arial"
FONT_DISPLAY = "Palatino Linotype"
