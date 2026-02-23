import os
import json

DATA_DIR = 'datoscandidatos/candidatos'

# Mapeo manual basado en conocimiento político y el texto de los JSON
IDEOLOGIAS = {
    # IZQUIERDA (Estado fuerte, Servicios públicos, Social)
    "vladimir-roy-cerr-n-rojas": { "eco": 1, "seg": 5, "env": 8, "edu": 1, "sal": 1, "cor": 9, "des": 8 },
    "ronald-darwin-atencio-sotomayor": { "eco": 2, "seg": 4, "env": 9, "edu": 2, "sal": 1, "cor": 9, "des": 7 },
    "roberto-helbert-s-nchez-palomino": { "eco": 3, "seg": 5, "env": 8, "edu": 2, "sal": 2, "cor": 8, "des": 7 },
    "yonhy-lescano-ancieta": { "eco": 3, "seg": 6, "env": 8, "edu": 2, "sal": 2, "cor": 8, "des": 6 },
    "alfonso-l-pez-chau-nava": { "eco": 4, "seg": 6, "env": 8, "edu": 3, "sal": 3, "cor": 8, "des": 7 },
    
    # DERECHA (Mano dura, Libre mercado, Privado)
    "keiko-fujimori-higuchi": { "eco": 9, "seg": 9, "env": 3, "edu": 7, "sal": 7, "cor": 6, "des": 4 },
    "rafael-bernardo-l-pez-aliaga-cazorla": { "eco": 9, "seg": 10, "env": 4, "edu": 8, "sal": 8, "cor": 9, "des": 5 },
    "jose-daniel-williams-zapata": { "eco": 8, "seg": 9, "env": 5, "edu": 7, "sal": 7, "cor": 7, "des": 4 },
    "roberto-enrique-chiabra-le-n": { "eco": 7, "seg": 10, "env": 4, "edu": 6, "sal": 6, "cor": 8, "des": 5 },
    "george-patrick-forsyth-sommer": { "eco": 8, "seg": 8, "env": 6, "edu": 7, "sal": 7, "cor": 7, "des": 4 },
    "avanzapais": { "eco": 9, "seg": 8, "env": 4, "edu": 9, "sal": 9, "cor": 7, "des": 4 },

    # CENTRO / CENTRO-DERECHA
    "antonio-ortiz": { "eco": 6, "seg": 7, "env": 8, "edu": 5, "sal": 5, "cor": 8, "des": 6 },
    "jorge-nieto-montesinos": { "eco": 5, "seg": 6, "env": 7, "edu": 4, "sal": 4, "cor": 8, "des": 7 },
    "mesias-antonio-guevara-amasifuen": { "eco": 4, "seg": 5, "env": 8, "edu": 4, "sal": 4, "cor": 8, "des": 8 },
    "marisol-perez-tello": { "eco": 6, "seg": 6, "env": 8, "edu": 5, "sal": 5, "cor": 9, "des": 6 },
}

def get_profile(data):
    slug = data.get('slug')
    if slug in IDEOLOGIAS:
        return IDEOLOGIAS[slug]
    
    # Fallback por posicion declarada
    pos = data.get('posicion_politica', '').lower()
    if 'izquierda' in pos:
        return { "eco": 3, "seg": 5, "env": 8, "edu": 3, "sal": 2, "cor": 8, "des": 7 }
    if 'derecha' in pos:
        return { "eco": 8, "seg": 8, "env": 4, "edu": 7, "sal": 7, "cor": 7, "des": 4 }
    return { "eco": 5, "seg": 6, "env": 6, "edu": 5, "sal": 5, "cor": 7, "des": 6 }

def main():
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith('.json'):
            continue
            
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Si NO tiene propuestas ni resumen, 0 absoluto
        has_propuestas = len(data.get('propuestas', [])) > 0
        has_resumen = len(data.get('resumen_propuestas', '')) > 20
        
        if not has_propuestas and not has_resumen:
            data['scores'] = {
                "score_economia": 0, "score_seguridad": 0, "score_medio_ambiente": 0,
                "score_educacion": 0, "score_salud": 0, "score_corrupcion": 0, "score_descentralizacion": 0
            }
        else:
            profile = get_profile(data)
            data['scores'] = {
                "score_economia": profile['eco'],
                "score_seguridad": profile['seg'],
                "score_medio_ambiente": profile['env'],
                "score_educacion": profile['edu'],
                "score_salud": profile['sal'],
                "score_corrupcion": profile['cor'],
                "score_descentralizacion": profile['des']
            }
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
