import requests
import time
from sqlalchemy.orm import Session
import backend.models as models

def geolocate_ips(operacao_id: int, db: Session):
    # Buscar IPs da operação que ainda não têm geolocalização
    # IPs estão na tabela 'ips', ligados a mensagens da operação
    
    # Subquery para pegar IPs da operação
    ips_to_update = db.query(models.IP).join(models.Mensagem).filter(
        models.Mensagem.operacao_id == operacao_id,
        models.IP.latitude.is_(None) # Assumindo que se tem lat, já foi processado
    ).distinct().all()
    
    updated_count = 0
    
    for ip in ips_to_update:
        try:
            # ip-api.com (free, 45 req/min)
            response = requests.get(f"http://ip-api.com/json/{ip.endereco}")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    ip.pais = data.get('country')
                    ip.cidade = data.get('city')
                    ip.latitude = data.get('lat')
                    ip.longitude = data.get('lon')
                    ip.provedor = data.get('isp')
                    updated_count += 1
            
            # Respeitar rate limit (simples sleep)
            time.sleep(1.5) 
            
        except Exception as e:
            print(f"Erro ao geolocalizar IP {ip.endereco}: {e}")
            continue
            
    db.commit()
    return updated_count
