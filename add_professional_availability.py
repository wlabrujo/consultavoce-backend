#!/usr/bin/env python3
"""
Script para adicionar horários de disponibilidade para o profissional Warlley
"""
import os
import sys

# Adicionar diretório server ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server'))

from database import SessionLocal
from models import Availability, User

def add_availability():
    db = SessionLocal()
    try:
        # Buscar profissional Warlley (email: warlleylabrujo@gmail.com)
        professional = db.query(User).filter(
            User.email == 'warlleylabrujo@gmail.com',
            User.user_type == 'professional'
        ).first()
        
        if not professional:
            print("❌ Profissional não encontrado!")
            return
        
        print(f"✅ Profissional encontrado: {professional.name} (ID: {professional.id})")
        
        # Verificar se já tem disponibilidade
        existing = db.query(Availability).filter(
            Availability.professional_id == professional.id
        ).count()
        
        if existing > 0:
            print(f"⚠️  Profissional já tem {existing} horários configurados")
            response = input("Deseja remover e recriar? (s/n): ")
            if response.lower() == 's':
                db.query(Availability).filter(
                    Availability.professional_id == professional.id
                ).delete()
                db.commit()
                print("🗑️  Horários antigos removidos")
            else:
                print("❌ Operação cancelada")
                return
        
        # Criar horários padrão
        availabilities = [
            # Segunda-feira (1): 08:00 - 18:00
            Availability(professional_id=professional.id, day_of_week=1, start_time='08:00', end_time='18:00', is_active=True),
            # Terça-feira (2): 08:00 - 18:00
            Availability(professional_id=professional.id, day_of_week=2, start_time='08:00', end_time='18:00', is_active=True),
            # Quarta-feira (3): 08:00 - 18:00
            Availability(professional_id=professional.id, day_of_week=3, start_time='08:00', end_time='18:00', is_active=True),
            # Quinta-feira (4): 08:00 - 18:00
            Availability(professional_id=professional.id, day_of_week=4, start_time='08:00', end_time='18:00', is_active=True),
            # Sexta-feira (5): 08:00 - 18:00
            Availability(professional_id=professional.id, day_of_week=5, start_time='08:00', end_time='18:00', is_active=True),
            # Sábado (6): 08:00 - 12:00
            Availability(professional_id=professional.id, day_of_week=6, start_time='08:00', end_time='12:00', is_active=True),
        ]
        
        for avail in availabilities:
            db.add(avail)
        
        db.commit()
        
        print(f"\n✅ {len(availabilities)} horários adicionados com sucesso!")
        print("\n📅 Horários configurados:")
        print("  Segunda a Sexta: 08:00 - 18:00")
        print("  Sábado: 08:00 - 12:00")
        print("  Domingo: Sem atendimento")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    add_availability()
