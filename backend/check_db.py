from database import SessionLocal, engine
import models
from sqlalchemy import text, func
from datetime import datetime

db = SessionLocal()
try:
    print(f"DB URL: {engine.url}")
    
    # Check operations with IDs
    ops = db.query(models.Operacao).all()
    for op in ops:
        print(f"Op ID: {op.id}, Name: {op.nome}")
        # Count messages for this op
        count = db.query(models.Mensagem).filter(models.Mensagem.operacao_id == op.id).count()
        print(f"  Total Msgs: {count}")
        
        # Count for Oct 14 2024
        start = datetime(2024, 10, 14, 0, 0, 0)
        end = datetime(2024, 10, 14, 23, 59, 59)
        count_oct = db.query(models.Mensagem).filter(
            models.Mensagem.operacao_id == op.id,
            models.Mensagem.data_hora >= start,
            models.Mensagem.data_hora <= end
        ).count()
        print(f"  Msgs on 2024-10-14: {count_oct}")
        
        # Check geolocated IPs for this op
        geo_count = db.query(models.IP).join(models.Mensagem).filter(
            models.Mensagem.operacao_id == op.id,
            models.IP.latitude.isnot(None)
        ).distinct().count()
        print(f"  Geolocated IPs: {geo_count}")

except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
