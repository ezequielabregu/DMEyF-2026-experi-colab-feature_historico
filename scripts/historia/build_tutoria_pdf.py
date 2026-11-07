"""PDF paginado del reporte grupal en Markdown, con tablas repetidas y fuentes Unicode."""
import argparse
import html
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'tmp/pdfdeps'))
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
from reportlab.pdfgen.canvas import Canvas


def markup(text):
    text = text.replace('–', '-').replace('—', '-').replace('\u2011', '-')
    text = html.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#2563a6">\1</link>', text)
    text = re.sub(r'`(.+?)`', r'<font color="#40536a">\1</font>', text)
    return text


class NumberedCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self.pages)
        for state in self.pages:
            self.__dict__.update(state)
            self.setFont('Arial', 8)
            self.setFillColor(colors.HexColor('#64748b'))
            self.drawString(42, 25, 'Cierre del 7 de noviembre de 2026 | Evaluación exploratoria')
            self.drawRightString(A4[0] - 42, 25, f'{self._pageNumber} / {total}')
            super().showPage()
        super().save()


def build(source, target):
    pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
    pdfmetrics.registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial', boldItalic='Arial-Bold')
    body = ParagraphStyle('body', fontName='Arial', fontSize=9, leading=13, spaceAfter=8, textColor=colors.HexColor('#172a3e'))
    small = ParagraphStyle('small', parent=body, fontSize=7.7, leading=10.3, spaceAfter=0)
    caption = ParagraphStyle('caption', parent=body, fontSize=8, leading=11, textColor=colors.HexColor('#526070'))
    styles = {level: ParagraphStyle(f'h{level}', parent=body, fontName='Arial-Bold',
                 fontSize={1: 23, 2: 16, 3: 12, 4: 10}[level],
                 leading={1: 28, 2: 20, 3: 16, 4: 14}[level],
                 spaceBefore=14 if level > 1 else 0, spaceAfter=9, keepWithNext=True)
              for level in range(1, 5)}
    width = A4[0] - 84
    target.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(target), pagesize=A4, leftMargin=42, rightMargin=42,
                                 topMargin=47, bottomMargin=45,
                                 title='Experimento feature histórico - Informe grupal actualizado',
                                 author='Tomás Henseler, Clara M. Rodríguez y Ezequiel Abregú')
    story = []
    lines = source.read_text(encoding='utf-8').splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('|'):
            raw = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [cell.strip() for cell in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', cell) for cell in cells):
                    raw.append(cells)
                i += 1
            count = len(raw[0])
            if any(len(row) != count for row in raw):
                raise ValueError('Tabla irregular')
            if 'Grupo' in raw[0]:
                weights = [92, 68, 34, 64, 71, 66, 73]
            elif 'Prioridad' in raw[0]:
                weights = [29, 183, 218, 75]
            elif count == 2:
                weights = [130, 375]
            elif count == 3:
                weights = [100, 150, 255]
            else:
                weights = [110] + [395 / (count - 1)] * (count - 1)
            col_widths = [width * weight / sum(weights) for weight in weights]
            table = Table([[Paragraph(markup(cell), small) for cell in row] for row in raw],
                          colWidths=col_widths, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8eef5')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7f9fb')]),
                ('LINEBELOW', (0, 0), (-1, 0), .6, colors.HexColor('#8797a8')),
                ('LINEBELOW', (0, 1), (-1, -1), .3, colors.HexColor('#d8e0e8')),
                ('LEFTPADDING', (0, 0), (-1, -1), 5), ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.extend([Spacer(1, 5), table, Spacer(1, 12)])
            continue
        image = re.fullmatch(r'!\[(.*?)\]\((.*?)\)', line)
        if image:
            picture = Image(str(source.parent / image.group(2)))
            scale = min(width / picture.imageWidth, 270 / picture.imageHeight)
            picture.drawWidth = picture.imageWidth * scale
            picture.drawHeight = picture.imageHeight * scale
            story.append(KeepTogether([picture, Spacer(1, 5), Paragraph(markup(image.group(1)), caption)]))
        elif re.match(r'^#{1,4} ', line):
            level = len(line.split(' ', 1)[0])
            if line[level + 1:] == 'Preguntas para Alejandro Bolaños':
                story.append(PageBreak())
            story.append(Paragraph(markup(line[level + 1:]), styles[level]))
        elif line.startswith('- '):
            story.append(Paragraph(markup(line[2:]), body, bulletText='-'))
        else:
            story.append(Paragraph(markup(line), body))
        i += 1

    def header(canvas, doc):
        canvas.setFont('Arial-Bold', 8)
        canvas.setFillColor(colors.HexColor('#526070'))
        canvas.drawString(42, A4[1] - 27, 'FEATURE HISTÓRICO | DMEyF 2026 | INFORME GRUPAL')
    document.build(story, onFirstPage=header, onLaterPages=header, canvasmaker=NumberedCanvas)
    print(target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path('docs/estado_grupal_para_tutoria.md'))
    parser.add_argument('--out', type=Path, default=Path('output/pdf/informe_ezequiel_actualizado_20261107.pdf'))
    args = parser.parse_args()
    build(args.source, args.out)
