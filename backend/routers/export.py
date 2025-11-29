from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime
import models
from database import get_db

router = APIRouter(
    prefix="/export",
    tags=["export"]
)

@router.get("/pdf/{operacao_id}")
def export_pdf(operacao_id: int, db: Session = Depends(get_db)):
    """Generate PDF report for an operation"""
    
    # Get operation
    operacao = db.query(models.Operacao).filter(models.Operacao.id == operacao_id).first()
    if not operacao:
        return {"error": "Operação não encontrada"}
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Container for elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph(f"Relatório Forense - {operacao.nome}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Operation info
    info_data = [
        ['Operação:', operacao.nome],
        ['Descrição:', operacao.descricao or 'N/A'],
        ['Data de Criação:', operacao.data_criacao.strftime('%d/%m/%Y %H:%M')],
        ['Gerado em:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Statistics
    total_phones = db.query(models.Telefone).filter(models.Telefone.operacao_id == operacao_id).count()
    total_messages = db.query(models.Mensagem).filter(models.Mensagem.operacao_id == operacao_id).count()
    total_ips = db.query(models.IP).distinct(models.IP.endereco).count()
    
    elements.append(Paragraph("Estatísticas Gerais", heading_style))
    
    stats_data = [
        ['Total de Telefones', str(total_phones)],
        ['Total de Mensagens', str(total_messages)],
        ['IPs Únicos', str(total_ips)]
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Top phones
    elements.append(Paragraph("Top 10 Telefones Mais Ativos", heading_style))
    
    top_phones = db.query(
        models.Telefone.numero,
        db.query(models.Mensagem).filter(
            (models.Mensagem.remetente == models.Telefone.numero) | 
            (models.Mensagem.destinatario == models.Telefone.numero)
        ).filter(models.Mensagem.operacao_id == operacao_id).count().label('total')
    ).filter(models.Telefone.operacao_id == operacao_id).limit(10).all()
    
    if top_phones:
        phone_data = [['Telefone', 'Mensagens']]
        for phone in top_phones:
            phone_data.append([phone.numero, str(phone.total)])
        
        phone_table = Table(phone_data, colWidths=[3*inch, 2*inch])
        phone_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        elements.append(phone_table)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF value
    pdf_value = buffer.getvalue()
    buffer.close()
    
    # Return as response
    return Response(
        content=pdf_value,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=relatorio_{operacao.nome}_{datetime.now().strftime('%Y%m%d')}.pdf"
        }
    )
