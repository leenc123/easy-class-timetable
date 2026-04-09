"""
PDF 导出服务
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import date
from typing import List

from app.models.schedule import ClassSession


def generate_schedule_pdf(sessions: List[ClassSession], start_date: date, end_date: date) -> bytes:
    """生成课表 PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1*cm,
        rightMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # 标题
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=1,
        spaceAfter=20
    )
    elements.append(Paragraph(f"课程表 ({start_date} ~ {end_date})", title_style))
    elements.append(Spacer(1, 0.5*cm))

    # 表格数据
    data = [['日期', '时间', '课程', '教师', '教室', '学生数', '状态']]

    for session in sessions:
        time_slot = session.time_slot
        data.append([
            str(session.session_date),
            f"{time_slot.start_time}-{time_slot.end_time}" if time_slot else "",
            session.course.name if session.course else "",
            session.teacher.name if session.teacher else "",
            session.classroom.name if session.classroom else "",
            str(len(session.student_attendances)) if session.student_attendances else "0",
            session.status.value
        ])

    # 创建表格
    table = Table(data, colWidths=[2.5*cm, 3*cm, 4*cm, 2.5*cm, 2.5*cm, 1.5*cm, 2*cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWHEIGHT', (0, 0), (-1, -1), 0.6*cm),
    ]))

    elements.append(table)
    doc.build(elements)

    return buffer.getvalue()