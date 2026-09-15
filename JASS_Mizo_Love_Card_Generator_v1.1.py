"""
JASS Mizo Love Card Generator v1.1
Single-file PySide6 application.

Features:
- Click any quick Mizo phrase to put it into the card
- Editable Mizo text before final export
- Live card preview
- Multiple themes/templates
- Text font, size, color, bold, italic, shadow
- Background image support
- Decorative frame, heart icons, footer text
- Random design
- Load background
- Save PNG
- Copy rendered card to clipboard
- Share/export via PNG
- No external project files required

Run:
    py JASS_Mizo_Love_Card_Generator_v1.0.py
"""

import sys
import random
from pathlib import Path

from PySide6.QtCore import Qt, QRectF, QSize, Signal
from PySide6.QtGui import (
    QColor, QFont, QFontDatabase, QLinearGradient, QPainter,
    QPen, QBrush, QPixmap, QImage, QImageReader, QPainterPath
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QTextEdit, QLineEdit,
    QComboBox, QSpinBox, QSlider, QCheckBox, QFileDialog,
    QMessageBox, QFrame, QScrollArea, QSplitter, QColorDialog,
    QGroupBox, QSizePolicy
)


APP_TITLE = "JASS Mizo Love Card Generator v1.1"

PHRASES = [
    "Ka hmangaih che",
    "I hming ka duh",
    "I neih ang che",
    "I nâwn leh ka dam",
    "Ka thlarau i nei",
    "Zawng zawngah i awm",
    "Tunah hian i thlâng ang che",
    "I tan ka hria",
    "Ka ngai­sang che",
    "Hlim takin i awm rawh",
    "Ka thinlung i ta",
    "Ka nunah i pawimawh",
]

THEMES = [
    ("Sunset Love", "sunset"),
    ("Mountain", "mountain"),
    ("Flowers", "flowers"),
    ("Minimal", "minimal"),
    ("Romantic", "romantic"),
    ("Heart", "heart"),
    ("Nature", "nature"),
    ("Elegant", "elegant"),
    ("Vintage", "vintage"),
    ("Cute", "cute"),
    ("Birthday Love", "birthday"),
    ("Pink Blossom", "blossom"),
]

TEMPLATES = [
    ("Sunset Love", "sunset"),
    ("Rose Heart", "rose"),
    ("Mountain View", "mountain"),
    ("Floral Frame", "floral"),
    ("Minimal Love", "minimal"),
    ("Night Sky", "night"),
    ("Vintage", "vintage"),
    ("Cute Hearts", "cute"),
    ("Pink Blossom", "blossom"),
    ("Love Letters", "letters"),
    ("Golden Heart", "golden"),
    ("Blue Romance", "blue"),
]

FONT_OPTIONS = [
    "Dancing Script",
    "Segoe Script",
    "Georgia",
    "Times New Roman",
    "Arial",
    "Calibri",
    "Cascadia Mono",
]

QUICK_TEXT = [
    "Ka Nun Hi I Ti Mawi Ta", 
    "Hmangaihna nen, Engtik lai pawhin",
]


def safe_font(preferred, fallback="Georgia"):
    families = QFontDatabase.families()
    return preferred if preferred in families else fallback


class CardCanvas(QWidget):
    """Paints the complete card and supports inline editing through the main editor."""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(420, 560)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.mizo_text = "Ka hmangaih che"
        self.top_left = "Fanu\nMake My\nLife Beautiful"
        self.top_right = "Daddy\nLoves\nFanu"
        self.footer = "Big Daddy Love  ♥  Always for Fanu"

        self.theme = "sunset"
        self.template = "sunset"
        self.text_color = QColor("#8b0717")
        self.font_name = safe_font("Dancing Script")
        self.font_size = 48
        self.bold = False
        self.italic = True
        self.shadow = True
        self.background = None

        self.show_background = True
        self.show_frame = True
        self.show_hearts = True
        self.show_custom = False
        self.custom_text = ""

    def set_values(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.update()

    def _gradient(self, painter, rect, c1, c2):
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0, QColor(c1))
        grad.setColorAt(1, QColor(c2))
        painter.fillRect(rect, grad)

    def _draw_background(self, p, r):
        if self.background and self.show_background:
            pix = QPixmap(self.background)
            if not pix.isNull():
                scaled = pix.scaled(
                    r.size().toSize(), Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                x = int((scaled.width() - r.width()) / 2)
                y = int((scaled.height() - r.height()) / 2)
                p.drawPixmap(int(r.x()), int(r.y()), scaled, x, y,
                             int(r.width()), int(r.height()))
                return

        t = self.theme
        if t in ("sunset", "rose", "floral", "blossom"):
            self._gradient(p, r, "#ffb5a7", "#f08080")
            # soft sun
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 246, 190, 180))
            p.drawEllipse(QRectF(r.width()*0.68, r.height()*0.42, 42, 42))
            # hills
            path = QPainterPath()
            path.moveTo(0, r.height()*0.70)
            path.cubicTo(r.width()*0.25, r.height()*0.58,
                         r.width()*0.38, r.height()*0.80,
                         r.width()*0.58, r.height()*0.68)
            path.cubicTo(r.width()*0.78, r.height()*0.55,
                         r.width()*0.90, r.height()*0.73,
                         r.width(), r.height()*0.63)
            path.lineTo(r.width(), r.height())
            path.lineTo(0, r.height())
            path.closeSubpath()
            p.setBrush(QColor("#70465d"))
            p.drawPath(path)

            # flowers
            for i in range(13):
                x = (i * 67 + 25) % max(40, int(r.width()))
                y = r.height() - 65 - ((i * 31) % 70)
                p.setBrush(QColor("#f04b72"))
                for a in range(5):
                    import math
                    ang = a * 1.256
                    p.drawEllipse(QRectF(x + 10*math.cos(ang)-8,
                                         y + 10*math.sin(ang)-8, 16, 16))
                p.setBrush(QColor("#ffd45e"))
                p.drawEllipse(QRectF(x-5, y-5, 10, 10))

        elif t in ("mountain", "nature"):
            self._gradient(p, r, "#b8e0ff", "#e9f5ff")
            p.setPen(Qt.NoPen)
            p.setBrush(QColor("#7597b8"))
            p.drawPolygon([
                r.topLeft() + QSize(0, int(r.height()*0.70)),
                r.topLeft() + QSize(int(r.width()*0.25), int(r.height()*0.30)),
                r.topLeft() + QSize(int(r.width()*0.52), int(r.height()*0.70)),
            ])
            p.setBrush(QColor("#4d6f88"))
            p.drawPolygon([
                r.topLeft() + QSize(int(r.width()*0.30), int(r.height()*0.70)),
                r.topLeft() + QSize(int(r.width()*0.62), int(r.height()*0.22)),
                r.topLeft() + QSize(int(r.width()*1.00), int(r.height()*0.70)),
            ])
            p.setBrush(QColor("#9dc2d8"))
            p.drawEllipse(QRectF(r.width()*0.70, r.height()*0.13, 45, 45))

        elif t == "minimal":
            self._gradient(p, r, "#fffaf4", "#f5e9e2")
        elif t == "heart":
            self._gradient(p, r, "#ffd4df", "#fff1f5")
            self._draw_big_heart(p, r, QColor(255, 104, 140, 80))
        elif t == "romantic":
            self._gradient(p, r, "#ffd5df", "#e88ca4")
            self._draw_big_heart(p, r, QColor(255, 255, 255, 80))
        elif t == "elegant":
            self._gradient(p, r, "#101426", "#27354e")
            p.setPen(QPen(QColor("#d5b56b"), 1))
            for i in range(5):
                p.drawEllipse(QRectF(25+i*12, 25+i*12,
                                     r.width()-50-i*24, r.height()-50-i*24))
        elif t == "vintage":
            self._gradient(p, r, "#e9d0a5", "#f5e5c8")
        elif t == "cute":
            self._gradient(p, r, "#ffc9db", "#fff2f6")
            self._draw_big_heart(p, r, QColor(245, 70, 120, 90))
        elif t == "birthday":
            self._gradient(p, r, "#ffd4e5", "#fff5cc")
            p.setPen(QPen(QColor("#c53c64"), 3))
            for x in range(50, int(r.width()), 70):
                p.drawLine(x, 50, x, 100)
                p.drawEllipse(QRectF(x-10, 35, 20, 20))
        else:
            self._gradient(p, r, "#ffd6e4", "#f7e6ed")

    def _draw_big_heart(self, p, r, color):
        cx = r.width() / 2
        cy = r.height() * 0.48
        s = min(r.width(), r.height()) * 0.26
        path = QPainterPath()
        path.moveTo(cx, cy+s*0.92)
        path.cubicTo(cx-s*1.15, cy+s*0.18, cx-s*1.08, cy-s*0.80,
                     cx-s*0.48, cy-s*0.80)
        path.cubicTo(cx-s*0.10, cy-s*0.80, cx, cy-s*0.47,
                     cx, cy-s*0.22)
        path.cubicTo(cx, cy-s*0.47, cx+s*0.10, cy-s*0.80,
                     cx+s*0.48, cy-s*0.80)
        path.cubicTo(cx+s*1.08, cy-s*0.80, cx+s*1.15, cy+s*0.18,
                     cx, cy+s*0.92)
        p.setBrush(QBrush(color))
        p.setPen(QPen(QColor(255,255,255,150), 2))
        p.drawPath(path)

    def _draw_text(self, p, text, rect, size, align, color=None):
        color = color or self.text_color
        font = QFont(self.font_name, size)
        font.setBold(self.bold)
        font.setItalic(self.italic)
        p.setFont(font)

        if self.shadow:
            p.setPen(QColor(0, 0, 0, 75))
            p.drawText(rect.translated(2, 2), align, text)
        p.setPen(color)
        p.drawText(rect, align, text)

    def _draw_heart(self, p, x, y, size, color):
        path = QPainterPath()
        path.moveTo(x, y + size*0.85)
        path.cubicTo(x-size*0.95, y+size*0.18, x-size*0.90, y,
                     x-size*0.42, y)
        path.cubicTo(x-size*0.08, y, x, y+size*0.22, x, y+size*0.38)
        path.cubicTo(x, y+size*0.22, x+size*0.08, y,
                     x+size*0.42, y)
        path.cubicTo(x+size*0.90, y, x+size*0.95, y+size*0.18,
                     x, y+size*0.85)
        path.closeSubpath()
        p.setPen(Qt.NoPen)
        p.setBrush(color)
        p.drawPath(path)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)

        outer = QRectF(0, 0, self.width(), self.height())
        p.fillRect(outer, QColor("#eceff4"))

        margin = min(self.width(), self.height()) * 0.035
        r = QRectF(margin, margin, self.width()-2*margin, self.height()-2*margin)

        self._draw_background(p, r)

        # translucent overlay improves text readability
        p.setBrush(QColor(255,255,255,24))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(r, 12, 12)

        if self.show_frame:
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255,255,255,220), 2.2))
            p.drawRoundedRect(r.adjusted(7,7,-7,-7), 11, 11)
            p.setPen(QPen(QColor(115,50,50,170), 1))
            p.drawRoundedRect(r.adjusted(14,14,-14,-14), 9, 9)

        # top decorative text
        top_h = r.height()*0.19
        self._draw_text(
            p, self.top_left,
            QRectF(r.left()+r.width()*0.05, r.top()+r.height()*0.045,
                   r.width()*0.35, top_h),
            max(15, int(r.width()*0.040)), Qt.AlignLeft | Qt.AlignTop,
            QColor("#7b1020")
        )
        self._draw_text(
            p, self.top_right,
            QRectF(r.left()+r.width()*0.66, r.top()+r.height()*0.045,
                   r.width()*0.28, top_h),
            max(15, int(r.width()*0.038)), Qt.AlignRight | Qt.AlignTop,
            QColor("#7b1020")
        )

        if self.show_hearts:
            self._draw_heart(p, r.left()+r.width()*0.19,
                             r.top()+r.height()*0.16, 25, QColor("#9e1021"))
            self._draw_heart(p, r.left()+r.width()*0.79,
                             r.top()+r.height()*0.16, 25, QColor("#9e1021"))

        # Main heart / text panel
        cx = r.center().x()
        cy = r.top() + r.height()*0.49
        if self.template not in ("minimal", "night", "blue"):
            self._draw_big_heart(p, r, QColor(255, 245, 245, 185))
            # outline heart
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255,255,255,220), 2))
            # approximate panel
            panel = QRectF(cx-r.width()*0.30, cy-r.height()*0.19,
                            r.width()*0.60, r.height()*0.36)
            p.drawEllipse(panel)

        main_rect = QRectF(r.left()+r.width()*0.14, cy-r.height()*0.17,
                           r.width()*0.72, r.height()*0.34)
        main_font = max(18, int(self.font_size * (r.width()/700)))
        self._draw_text(p, self.mizo_text, main_rect, main_font,
                        Qt.AlignCenter | Qt.TextWordWrap)

        # divider + secondary phrase
        y = cy + r.height()*0.17
        p.setPen(QPen(self.text_color, 1.2))
        p.drawLine(cx-r.width()*0.18, y, cx-r.width()*0.05, y)
        p.drawLine(cx+r.width()*0.05, y, cx+r.width()*0.18, y)
        if self.show_hearts:
            self._draw_heart(p, cx-12, y-9, 25, self.text_color)

        self._draw_text(
            p, "I awm chuan\nka hlim tak.",
            QRectF(cx-r.width()*0.25, y+12, r.width()*0.50, r.height()*0.14),
            max(16, int(self.font_size*0.47)),
            Qt.AlignCenter, self.text_color
        )

        if self.show_hearts:
            self._draw_heart(p, cx-12, y+r.height()*0.13, 26, self.text_color)

        # custom text/logo area
        if self.show_custom and self.custom_text:
            self._draw_text(
                p, self.custom_text,
                QRectF(r.left()+r.width()*0.10, r.bottom()-r.height()*0.23,
                       r.width()*0.80, r.height()*0.10),
                max(14, int(self.font_size*0.48)),
                Qt.AlignCenter, self.text_color
            )

        # footer
        p.setPen(QColor(255,255,255,220))
        footer_rect = QRectF(r.left()+25, r.bottom()-55, r.width()-50, 35)
        f = QFont(safe_font("Georgia"), 15)
        f.setItalic(True)
        p.setFont(f)
        p.drawText(footer_rect, Qt.AlignCenter, self.footer)

        p.end()

    def render_image(self, width=1000, height=1300):
        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(QColor("#eceff4"))
        old_size = self.size()
        self.resize(width, height)
        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(QColor("#eceff4"))
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        self._paint_to(painter, QRectF(0, 0, width, height))
        painter.end()
        self.resize(old_size)
        return image

    def _paint_to(self, p, target):
        # Temporarily paint using a cloned-size painter by calling the same
        # drawing logic with target dimensions.
        w, h = target.width(), target.height()
        p.fillRect(target, QColor("#eceff4"))
        margin = min(w, h) * 0.035
        r = QRectF(margin, margin, w-2*margin, h-2*margin)
        self._draw_background(p, r)
        p.setBrush(QColor(255,255,255,24))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(r, 12, 12)
        if self.show_frame:
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255,255,255,220), 3))
            p.drawRoundedRect(r.adjusted(8,8,-8,-8), 14, 14)
            p.setPen(QPen(QColor(115,50,50,170), 1.5))
            p.drawRoundedRect(r.adjusted(16,16,-16,-16), 12, 12)

        def txt(text, rect, size, align, color=None):
            color = color or self.text_color
            f = QFont(self.font_name, size)
            f.setBold(self.bold); f.setItalic(self.italic)
            p.setFont(f)
            if self.shadow:
                p.setPen(QColor(0,0,0,75))
                p.drawText(rect.translated(3,3), align, text)
            p.setPen(color)
            p.drawText(rect, align, text)

        txt(self.top_left, QRectF(r.left()+w*.05,r.top()+h*.045,w*.35,h*.19),
            max(22,int(w*.040)), Qt.AlignLeft|Qt.AlignTop, QColor("#7b1020"))
        txt(self.top_right, QRectF(r.left()+w*.66,r.top()+h*.045,w*.28,h*.19),
            max(22,int(w*.038)), Qt.AlignRight|Qt.AlignTop, QColor("#7b1020"))

        if self.show_hearts:
            self._draw_heart(p, r.left()+w*.19, r.top()+h*.16, 34, QColor("#9e1021"))
            self._draw_heart(p, r.left()+w*.79, r.top()+h*.16, 34, QColor("#9e1021"))

        cx, cy = r.center().x(), r.top()+h*.49
        if self.template not in ("minimal","night","blue"):
            self._draw_big_heart(p, r, QColor(255,245,245,185))
            p.setBrush(Qt.NoBrush)
            p.setPen(QPen(QColor(255,255,255,230), 3))
            p.drawEllipse(QRectF(cx-w*.30,cy-h*.19,w*.60,h*.36))

        main_rect = QRectF(r.left()+w*.14,cy-h*.17,w*.72,h*.34)
        txt(self.mizo_text, main_rect, max(28,int(self.font_size*(w/700))),
            Qt.AlignCenter|Qt.TextWordWrap)

        y=cy+h*.17
        p.setPen(QPen(self.text_color,2))
        p.drawLine(cx-w*.18,y,cx-w*.05,y)
        p.drawLine(cx+w*.05,y,cx+w*.18,y)
        if self.show_hearts:
            self._draw_heart(p,cx-16,y-12,32,self.text_color)

        txt("I awm chuan\nka hlim tak.",
            QRectF(cx-w*.25,y+16,w*.50,h*.14),
            max(20,int(self.font_size*.47)),Qt.AlignCenter,self.text_color)
        if self.show_hearts:
            self._draw_heart(p,cx-16,y+h*.13,34,self.text_color)

        if self.show_custom and self.custom_text:
            txt(self.custom_text,
                QRectF(r.left()+w*.10,r.bottom()-h*.23,w*.80,h*.10),
                max(18,int(self.font_size*.48)),Qt.AlignCenter,self.text_color)

        f=QFont(safe_font("Georgia"),20); f.setItalic(True); p.setFont(f)
        p.setPen(QColor(255,255,255,225))
        p.drawText(QRectF(r.left()+30,r.bottom()-70,r.width()-60,45),
                   Qt.AlignCenter,self.footer)


class ColorButton(QPushButton):
    colorSelected = Signal(QColor)

    def __init__(self, color="#8b0717", parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.setFixedSize(58, 34)
        self.setToolTip("Choose the main Mizo text colour")
        self.clicked.connect(self.choose)
        self.refresh()

    def refresh(self):
        # Keep the actual selected colour visible on the button.
        # Also use a contrasting border so very light colours remain visible.
        border = "#333333" if self.color.lightness() > 180 else "#888888"
        self.setStyleSheet(
            f"QPushButton {{ background-color:{self.color.name()}; "
            f"border:2px solid {border}; border-radius:6px; }}"
            f"QPushButton:hover {{ border:2px solid #e92963; }}"
        )

    def choose(self):
        c = QColorDialog.getColor(
            self.color,
            self,
            "Choose Mizo Text Colour",
            QColorDialog.ShowAlphaChannel
        )
        if c.isValid():
            self.color = QColor(c)
            self.refresh()
            # Emit the selected colour directly instead of relying on widget
            # parent hierarchy. This fixes the colour-change propagation bug.
            self.colorSelected.emit(QColor(c))


class PhraseButton(QPushButton):
    def __init__(self, text, callback):
        super().__init__("♥  " + text + "                                      ⧉")
        self.phrase = text
        self.clicked.connect(lambda: callback(self.phrase))
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(34)
        self.setStyleSheet("""
            QPushButton {
                text-align:left; padding:5px 10px;
                background:#ffffff; border:1px solid #e3dce4;
                border-radius:6px; color:#202533;
            }
            QPushButton:hover { background:#ffeaf1; border-color:#ef7194; }
            QPushButton:pressed { background:#ffd9e5; }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1500, 920)
        self.setMinimumSize(1100, 720)

        self.card = CardCanvas()
        self.build_ui()
        self.apply_theme("sunset")
        self.statusBar().showMessage("Ready")

    def section(self, title, color="#edf2ff"):
        box = QGroupBox(title)
        box.setStyleSheet(f"""
            QGroupBox {{
                font-size:16px; font-weight:700; color:#16366d;
                border:1px solid #d6deeb; border-radius:8px;
                margin-top:9px; padding:12px 8px 8px 8px;
                background:{color};
            }}
            QGroupBox::title {{ subcontrol-origin:margin; left:12px; padding:0 6px; }}
        """)
        return box

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(10, 8, 10, 5)
        root.setSpacing(8)

        header = QFrame()
        header.setStyleSheet("""
            QFrame { background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #fff0f5, stop:.55 #e7efff, stop:1 #d9e9ff);
                border:1px solid #d5dbe6; border-radius:9px; }
        """)
        hl = QHBoxLayout(header)
        icon = QLabel("♥")
        icon.setStyleSheet("font-size:52px;color:#e50046;")
        hl.addWidget(icon)
        titlebox = QVBoxLayout()
        title = QLabel("JASS Mizo Love Card Generator")
        title.setStyleSheet("font-size:30px;font-weight:800;color:#132b54;")
        subtitle = QLabel("Turn your Mizo words and feelings into beautiful love cards")
        subtitle.setStyleSheet("font-size:16px;color:#53657f;")
        titlebox.addWidget(title); titlebox.addWidget(subtitle)
        hl.addLayout(titlebox)
        hl.addStretch()
        right = QVBoxLayout()
        r1 = QLabel("Mizo Thiltihbeihna, Thlân, Hmangaihna ♥")
        r1.setStyleSheet("font-size:20px;font-style:italic;color:#c51458;")
        r2 = QLabel("Love in Mizo, Always Special")
        r2.setAlignment(Qt.AlignRight)
        r2.setStyleSheet("font-size:15px;color:#163d78;")
        right.addWidget(r1); right.addWidget(r2)
        hl.addLayout(right)
        root.addWidget(header)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        # LEFT PANEL
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(3,3,3,3)

        enter = self.section("1. Enter Mizo Text", "#fff4f7")
        el = QVBoxLayout(enter)
        top = QHBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText("Ka hmangaih che")
        self.text_edit.setMaximumHeight(95)
        self.text_edit.textChanged.connect(self.sync_text)
        clear = QPushButton("🗑  Clear")
        clear.clicked.connect(lambda: self.text_edit.clear())
        top.addWidget(self.text_edit)
        top.addWidget(clear)
        el.addLayout(top)
        self.count = QLabel("16/500")
        self.count.setAlignment(Qt.AlignRight)
        el.addWidget(self.count)

        ql = QHBoxLayout()
        qlab = QLabel("Quick Phrases:")
        qlab.setStyleSheet("font-weight:700;color:#183a72;")
        ql.addWidget(qlab); ql.addStretch()
        el.addLayout(ql)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        phrasew = QWidget()
        pv = QVBoxLayout(phrasew)
        pv.setContentsMargins(2,2,2,2)
        for phrase in PHRASES:
            pv.addWidget(PhraseButton(phrase, self.use_phrase))
        pv.addStretch()
        scroll.setWidget(phrasew)
        el.addWidget(scroll)
        ll.addWidget(enter, 1)

        editbox = self.section("2. Edit Before Final", "#f5efff")
        ev = QVBoxLayout(editbox)
        ev.addWidget(QLabel("You can edit the text, font, size, color and style; the preview updates instantly."))
        editbtn = QPushButton("✎  Edit Main Card Text")
        editbtn.clicked.connect(self.focus_text)
        ev.addWidget(editbtn)
        ll.addWidget(editbox)

        genbox = self.section("3. Generate & Save", "#eaf5ff")
        gv = QVBoxLayout(genbox)
        gv.addWidget(QLabel("When you are happy with the design, save or copy the card."))
        savebtn = QPushButton("⚙  Save / Export Card")
        savebtn.clicked.connect(self.save_card)
        gv.addWidget(savebtn)
        ll.addWidget(genbox)

        splitter.addWidget(left)

        # CENTER
        center = QWidget()
        cv = QVBoxLayout(center)
        cv.setContentsMargins(4,3,4,3)
        cv.addWidget(self.card, 1)
        splitter.addWidget(center)

        # RIGHT
        rightpanel = QWidget()
        rv = QVBoxLayout(rightpanel)
        rv.setContentsMargins(3,3,3,3)

        stylebox = self.section("Card Style", "#eef5ff")
        sv = QVBoxLayout(stylebox)
        row = QHBoxLayout()
        row.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        for name, key in THEMES:
            self.theme_combo.addItem(name, key)
        self.theme_combo.currentIndexChanged.connect(self.theme_changed)
        row.addWidget(self.theme_combo, 1)
        rand = QPushButton("✂  Random")
        rand.clicked.connect(self.random_design)
        row.addWidget(rand)
        sv.addLayout(row)

        themegrid = QGridLayout()
        for i,(name,key) in enumerate(THEMES):
            b=QPushButton(name)
            b.setMinimumHeight(52)
            b.setToolTip("Apply " + name)
            b.clicked.connect(lambda _, k=key: self.apply_theme(k))
            themegrid.addWidget(b,i//4,i%4)
        sv.addLayout(themegrid)
        rv.addWidget(stylebox)

        textbox = self.section("Text Settings", "#eef5ff")
        tv = QGridLayout(textbox)
        tv.addWidget(QLabel("Font:"),0,0)
        self.font_combo=QComboBox()
        self.font_combo.addItems(FONT_OPTIONS)
        self.font_combo.setCurrentText(self.card.font_name)
        self.font_combo.currentTextChanged.connect(self.font_changed)
        tv.addWidget(self.font_combo,0,1,1,2)

        tv.addWidget(QLabel("Size:"),1,0)
        self.size_spin=QSpinBox(); self.size_spin.setRange(18,90); self.size_spin.setValue(48)
        self.size_spin.valueChanged.connect(self.size_changed)
        tv.addWidget(self.size_spin,1,1)
        self.size_slider=QSlider(Qt.Horizontal); self.size_slider.setRange(18,90); self.size_slider.setValue(48)
        self.size_slider.valueChanged.connect(self.size_spin.setValue)
        tv.addWidget(self.size_slider,1,2)

        tv.addWidget(QLabel("Text Colour:"), 2, 0)
        self.color_btn = ColorButton(self.card.text_color.name())
        self.color_btn.colorSelected.connect(self.apply_color)
        tv.addWidget(self.color_btn, 2, 1)

        self.color_hex = QLabel(self.card.text_color.name().upper())
        self.color_hex.setMinimumWidth(82)
        self.color_hex.setAlignment(Qt.AlignCenter)
        tv.addWidget(self.color_hex, 2, 2)

        self.bold_cb=QCheckBox("Bold"); self.bold_cb.toggled.connect(lambda v:self.card.set_values(bold=v))
        self.italic_cb=QCheckBox("Italic"); self.italic_cb.setChecked(True); self.italic_cb.toggled.connect(lambda v:self.card.set_values(italic=v))
        self.shadow_cb=QCheckBox("Shadow"); self.shadow_cb.setChecked(True); self.shadow_cb.toggled.connect(lambda v:self.card.set_values(shadow=v))
        tv.addWidget(self.bold_cb,3,0); tv.addWidget(self.italic_cb,3,1); tv.addWidget(self.shadow_cb,3,2)
        rv.addWidget(textbox)

        elem = self.section("Add Elements", "#edfaff")
        ev2=QGridLayout(elem)
        self.bg_cb=QCheckBox("Background Image"); self.bg_cb.setChecked(True)
        self.bg_cb.toggled.connect(lambda v:self.card.set_values(show_background=v))
        self.frame_cb=QCheckBox("Decorative Frame"); self.frame_cb.setChecked(True)
        self.frame_cb.toggled.connect(lambda v:self.card.set_values(show_frame=v))
        self.heart_cb=QCheckBox("Heart Icons"); self.heart_cb.setChecked(True)
        self.heart_cb.toggled.connect(lambda v:self.card.set_values(show_hearts=v))
        self.custom_cb=QCheckBox("Custom Logo/Text")
        self.custom_cb.toggled.connect(self.custom_toggled)
        ev2.addWidget(self.bg_cb,0,0); ev2.addWidget(self.frame_cb,1,0)
        ev2.addWidget(self.heart_cb,2,0); ev2.addWidget(self.custom_cb,3,0)
        logo=QPushButton("▣  Add Your Logo / Text")
        logo.clicked.connect(self.add_custom)
        ev2.addWidget(logo,3,1)
        rv.addWidget(elem)

        rv.addStretch()
        splitter.addWidget(rightpanel)
        splitter.setSizes([370, 650, 450])
        root.addWidget(splitter, 1)

        # TEMPLATES
        templbox = self.section("Card Templates  (Click to apply)", "#f4f8ff")
        tg=QHBoxLayout(templbox)
        for name,key in TEMPLATES:
            b=QPushButton(name)
            b.setMinimumWidth(95); b.setMinimumHeight(45)
            b.clicked.connect(lambda _, k=key: self.apply_template(k))
            tg.addWidget(b)
        scrollt=QScrollArea(); scrollt.setWidgetResizable(True); scrollt.setFixedHeight(78)
        tw=QWidget(); twl=QHBoxLayout(tw)
        for name,key in TEMPLATES:
            b=QPushButton(name); b.setMinimumWidth(100); b.setMinimumHeight(45)
            b.clicked.connect(lambda _, k=key: self.apply_template(k))
            twl.addWidget(b)
        twl.addStretch(); scrollt.setWidget(tw)
        tg.addWidget(scrollt,1)
        root.addWidget(templbox)

        # bottom actions
        actions=QHBoxLayout()
        load=QPushButton("▧  Load Background...")
        load.clicked.connect(self.load_background)
        save=QPushButton("▣  Save Card")
        save.clicked.connect(self.save_card)
        copy=QPushButton("▣  Copy to Clipboard")
        copy.clicked.connect(self.copy_clipboard)
        share=QPushButton("↗  Share / Export...")
        share.clicked.connect(self.save_card)
        new=QPushButton("⟳  Generate New Card")
        new.clicked.connect(self.new_card)
        new.setStyleSheet("background:#e92963;color:white;font-weight:700;padding:9px 18px;")
        for b in [load,save,copy,share]:
            actions.addWidget(b)
        actions.addStretch(); actions.addWidget(new)
        root.addLayout(actions)

        self.setStyleSheet("""
            QWidget { font-family: "Segoe UI"; font-size: 14px; }
            QPushButton { padding: 7px 12px; border:1px solid #d3d9e3;
                          border-radius:6px; background:#fff; }
            QPushButton:hover { background:#eef5ff; border-color:#8cb0e8; }
            QLineEdit,QTextEdit,QComboBox,QSpinBox {
                background:white; border:1px solid #cfd6e1; border-radius:5px; padding:5px;
            }
            QCheckBox { spacing:7px; }
        """)

    def sync_text(self):
        text=self.text_edit.toPlainText()
        if len(text)>500:
            text=text[:500]
            self.text_edit.blockSignals(True)
            self.text_edit.setPlainText(text)
            self.text_edit.blockSignals(False)
        self.count.setText(f"{len(text)}/500")
        self.card.mizo_text=text or "Ka hmangaih che"
        self.card.update()

    def use_phrase(self, phrase):
        self.text_edit.setPlainText(phrase)
        self.focus_text()
        self.statusBar().showMessage(f"Phrase added: {phrase}")

    def focus_text(self):
        self.text_edit.setFocus()
        self.text_edit.selectAll()

    def theme_changed(self):
        key=self.theme_combo.currentData()
        if key:
            self.apply_theme(key)

    def apply_theme(self,key):
        self.card.theme=key
        self.card.template=key
        idx=self.theme_combo.findData(key)
        if idx>=0:
            self.theme_combo.blockSignals(True)
            self.theme_combo.setCurrentIndex(idx)
            self.theme_combo.blockSignals(False)
        # choose readable defaults
        if key=="elegant":
            self.card.text_color=QColor("#f1d17b")
        elif key in ("mountain","nature","blue"):
            self.card.text_color=QColor("#173a65")
        else:
            self.card.text_color=QColor("#8b0717")
        self.color_btn.color = QColor(self.card.text_color)
        self.color_btn.refresh()
        self.color_hex.setText(self.card.text_color.name().upper())
        self.card.update()

    def apply_template(self,key):
        self.card.template=key
        mapping={
            "rose":"romantic","floral":"flowers","night":"elegant",
            "blue":"mountain","golden":"vintage","letters":"blossom"
        }
        self.card.theme=mapping.get(key,key)
        idx=self.theme_combo.findData(self.card.theme)
        if idx>=0:
            self.theme_combo.blockSignals(True); self.theme_combo.setCurrentIndex(idx); self.theme_combo.blockSignals(False)
        self.card.update()
        self.statusBar().showMessage(f"Template applied: {key.title()}")

    def font_changed(self,v):
        self.card.font_name=safe_font(v)
        self.card.update()

    def size_changed(self,v):
        self.size_slider.blockSignals(True); self.size_slider.setValue(v); self.size_slider.blockSignals(False)
        self.card.font_size=v
        self.card.update()

    def apply_color(self, c):
        self.card.text_color = QColor(c)
        self.color_btn.color = QColor(c)
        self.color_btn.refresh()
        self.color_hex.setText(self.card.text_color.name().upper())
        self.card.update()
        self.card.repaint()
        self.statusBar().showMessage(
            f"Text colour changed to {self.card.text_color.name().upper()}"
        )

    def custom_toggled(self,v):
        self.card.show_custom=v
        if v and not self.card.custom_text:
            self.add_custom()

    def add_custom(self):
        from PySide6.QtWidgets import QInputDialog
        text,ok=QInputDialog.getText(self,"Custom Logo / Text","Enter custom text:")
        if ok:
            self.card.custom_text=text
            self.custom_cb.setChecked(bool(text))
            self.card.show_custom=bool(text)
            self.card.update()

    def load_background(self):
        fn,_=QFileDialog.getOpenFileName(self,"Load Background Image","",
                                          "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if fn:
            self.card.background=fn
            self.bg_cb.setChecked(True)
            self.card.update()
            self.statusBar().showMessage("Background loaded")

    def save_card(self):
        fn,_=QFileDialog.getSaveFileName(self,"Save Mizo Love Card",
                                          "mizo_love_card.png","PNG Image (*.png)")
        if not fn:
            return
        if not fn.lower().endswith(".png"):
            fn += ".png"
        image=self.card.render_image(1200,1560)
        if image.save(fn,"PNG"):
            self.statusBar().showMessage(f"Saved: {fn}")
            QMessageBox.information(self,"Card Saved",f"Love card saved successfully.\n\n{fn}")
        else:
            QMessageBox.warning(self,"Save Failed","Could not save the card.")

    def copy_clipboard(self):
        image=self.card.render_image(1000,1300)
        QApplication.clipboard().setImage(image)
        self.statusBar().showMessage("Card copied to clipboard")

    def random_design(self):
        name,key=random.choice(THEMES)
        self.apply_theme(key)
        self.card.template=random.choice([x[1] for x in TEMPLATES])
        self.card.font_name=safe_font(random.choice(FONT_OPTIONS))
        self.card.font_size=random.randint(32,62)
        self.card.italic=random.choice([True,True,False])
        self.card.bold=random.choice([False,False,True])
        colors=["#8b0717","#9b1d45","#5a174c","#173a65","#7a4b15","#f4e4a3"]
        self.card.text_color = QColor(random.choice(colors))
        self.color_btn.color = QColor(self.card.text_color)
        self.color_btn.refresh()
        self.color_hex.setText(self.card.text_color.name().upper())
        self.font_combo.setCurrentText(self.card.font_name)
        self.size_spin.setValue(self.card.font_size)
        self.bold_cb.setChecked(self.card.bold)
        self.italic_cb.setChecked(self.card.italic)
        self.card.update()
        self.statusBar().showMessage("Random love-card design generated")

    def new_card(self):
        self.text_edit.setPlainText(random.choice(PHRASES))
        self.card.background=None
        self.apply_theme(random.choice(THEMES)[1])
        self.random_design()

    def keyPressEvent(self,event):
        if event.key()==Qt.Key_F5:
            self.random_design()
        elif event.key()==Qt.Key_Escape:
            self.text_edit.clearFocus()
        super().keyPressEvent(event)


def main():
    app=QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    win=MainWindow()
    win.show()
    return app.exec()


if __name__=="__main__":
    raise SystemExit(main())
