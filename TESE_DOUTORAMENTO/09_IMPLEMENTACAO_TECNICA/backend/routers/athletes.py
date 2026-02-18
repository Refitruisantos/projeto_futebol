from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import date
from database import get_db, DatabaseConnection

router = APIRouter()


class AthleteCreate(BaseModel):
    jogador_id: str
    nome_completo: str
    data_nascimento: Optional[date] = None
    posicao: Optional[str] = None
    numero_camisola: Optional[int] = None
    pe_dominante: Optional[str] = None
    altura_cm: Optional[int] = None
    massa_kg: Optional[float] = None


class AthleteUpdate(BaseModel):
    jogador_id: Optional[str] = None
    nome_completo: Optional[str] = None
    data_nascimento: Optional[date] = None
    posicao: Optional[str] = None
    numero_camisola: Optional[int] = None
    pe_dominante: Optional[str] = None
    altura_cm: Optional[int] = None
    massa_kg: Optional[float] = None
    ativo: Optional[bool] = None


@router.get("/", response_model=List[Dict[str, Any]])
def list_athletes(
    ativo: bool = True,
    db: DatabaseConnection = Depends(get_db)
):
    query = """
        SELECT 
            id, jogador_id, nome_completo, data_nascimento,
            posicao, numero_camisola, pe_dominante,
            altura_cm, massa_kg, ativo
        FROM atletas
        WHERE ativo = %s OR %s IS NULL
        ORDER BY nome_completo
    """
    return db.query_to_dict(query, (ativo, None if ativo else ativo))


@router.get("/{athlete_id}", response_model=Dict[str, Any])
def get_athlete(
    athlete_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    query = """
        SELECT 
            id, jogador_id, nome_completo, data_nascimento,
            posicao, numero_camisola, pe_dominante,
            altura_cm, massa_kg, ativo, created_at, updated_at
        FROM atletas
        WHERE id = %s
    """
    result = db.query_to_dict(query, (athlete_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Athlete not found")
    return result[0]


@router.get("/{athlete_id}/metrics")
def get_athlete_metrics(
    athlete_id: int,
    days: int = 365,  # Default to 1 year to show all historical data
    db: DatabaseConnection = Depends(get_db)
):
    # Get athlete summary metrics from ALL GPS data
    metrics_query = """
        SELECT 
            COUNT(DISTINCT g.sessao_id) as total_sessions,
            ROUND(AVG(g.distancia_total)::numeric, 2) as avg_distance,
            ROUND(MAX(g.velocidade_max)::numeric, 2) as max_speed,
            ROUND(AVG(g.aceleracoes)::numeric, 2) as avg_accelerations,
            ROUND(AVG(g.effs_19_8_kmh)::numeric, 2) as avg_high_intensity_efforts,
            ROUND(AVG(p.pse)::numeric, 2) as avg_rpe,
            ROUND(AVG(p.carga_total)::numeric, 2) as avg_load
        FROM dados_gps g
        LEFT JOIN dados_pse p ON p.sessao_id = g.sessao_id AND p.atleta_id = g.atleta_id
        WHERE g.atleta_id = %s
    """
    metrics_result = db.query_to_dict(metrics_query, (athlete_id,))
    metrics = metrics_result[0] if metrics_result else {}
    
    # Get unique sessions with aggregated GPS and PSE data (handle duplicate PSE records)
    recent_sessions_query = """
        SELECT 
            s.id, s.data, s.tipo, s.duracao_min, s.jornada,
            MAX(g.distancia_total) as distancia_total,
            MAX(g.velocidade_max) as velocidade_max,
            MAX(g.aceleracoes) as aceleracoes,
            MAX(g.desaceleracoes) as desaceleracoes,
            MAX(g.effs_19_8_kmh) as effs_19_8_kmh,
            MAX(g.dist_19_8_kmh) as dist_19_8_kmh,
            AVG(p.pse) as pse,
            AVG(p.carga_total) as carga_total,
            AVG(p.qualidade_sono) as qualidade_sono,
            AVG(p.stress) as stress,
            AVG(p.fadiga) as fadiga
        FROM sessoes s
        LEFT JOIN dados_gps g ON g.sessao_id = s.id AND g.atleta_id = %s
        LEFT JOIN dados_pse p ON p.sessao_id = s.id AND p.atleta_id = %s
        WHERE g.atleta_id IS NOT NULL OR p.atleta_id IS NOT NULL
        GROUP BY s.id, s.data, s.tipo, s.duracao_min, s.jornada
        ORDER BY s.data DESC
        LIMIT 50
    """
    recent = db.query_to_dict(recent_sessions_query, (athlete_id, athlete_id))
    
    return {
        "athlete_id": athlete_id,
        "metrics": metrics,
        "recent_sessions": recent
    }


@router.post("/", response_model=Dict[str, Any])
def create_athlete(
    athlete: AthleteCreate,
    db: DatabaseConnection = Depends(get_db)
):
    """Create a new athlete"""
    
    # Check if jogador_id already exists
    check_query = "SELECT id FROM atletas WHERE jogador_id = %s"
    existing = db.query_to_dict(check_query, (athlete.jogador_id,))
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Athlete with ID {athlete.jogador_id} already exists")
    
    # Check if numero_camisola is already taken (if provided)
    if athlete.numero_camisola:
        number_query = "SELECT id FROM atletas WHERE numero_camisola = %s AND ativo = true"
        existing_number = db.query_to_dict(number_query, (athlete.numero_camisola,))
        
        if existing_number:
            raise HTTPException(status_code=400, detail=f"Jersey number {athlete.numero_camisola} is already taken")
    
    try:
        insert_query = """
            INSERT INTO atletas (
                jogador_id, nome_completo, data_nascimento, posicao,
                numero_camisola, pe_dominante, altura_cm, massa_kg,
                ativo, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW()
            )
            RETURNING id, jogador_id, nome_completo, data_nascimento,
                     posicao, numero_camisola, pe_dominante,
                     altura_cm, massa_kg, ativo, created_at
        """
        
        result = db.query_to_dict(insert_query, (
            athlete.jogador_id,
            athlete.nome_completo,
            athlete.data_nascimento,
            athlete.posicao,
            athlete.numero_camisola,
            athlete.pe_dominante,
            athlete.altura_cm,
            athlete.massa_kg
        ))
        
        if result:
            return result[0]
        else:
            raise HTTPException(status_code=500, detail="Failed to create athlete")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating athlete: {str(e)}")


@router.put("/{athlete_id}", response_model=Dict[str, Any])
def update_athlete(
    athlete_id: int,
    athlete_update: AthleteUpdate,
    db: DatabaseConnection = Depends(get_db)
):
    """Update an existing athlete"""
    
    # Check if athlete exists
    check_query = "SELECT id FROM atletas WHERE id = %s"
    existing = db.query_to_dict(check_query, (athlete_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    # Build dynamic update query
    update_fields = []
    update_values = []
    
    for field, value in athlete_update.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            update_values.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Check for conflicts
    if athlete_update.jogador_id:
        conflict_query = "SELECT id FROM atletas WHERE jogador_id = %s AND id != %s"
        conflict = db.query_to_dict(conflict_query, (athlete_update.jogador_id, athlete_id))
        if conflict:
            raise HTTPException(status_code=400, detail=f"Athlete ID {athlete_update.jogador_id} already exists")
    
    if athlete_update.numero_camisola:
        number_query = "SELECT id FROM atletas WHERE numero_camisola = %s AND id != %s AND ativo = true"
        conflict = db.query_to_dict(number_query, (athlete_update.numero_camisola, athlete_id))
        if conflict:
            raise HTTPException(status_code=400, detail=f"Jersey number {athlete_update.numero_camisola} is already taken")
    
    try:
        update_fields.append("updated_at = NOW()")
        update_values.append(athlete_id)
        
        update_query = f"""
            UPDATE atletas 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, jogador_id, nome_completo, data_nascimento,
                     posicao, numero_camisola, pe_dominante,
                     altura_cm, massa_kg, ativo, updated_at
        """
        
        result = db.query_to_dict(update_query, update_values)
        
        if result:
            return result[0]
        else:
            raise HTTPException(status_code=500, detail="Failed to update athlete")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating athlete: {str(e)}")


@router.delete("/{athlete_id}")
def delete_athlete(
    athlete_id: int,
    permanent: bool = False,
    db: DatabaseConnection = Depends(get_db)
):
    """Delete or deactivate an athlete"""
    
    # Check if athlete exists
    check_query = "SELECT id, nome_completo, ativo FROM atletas WHERE id = %s"
    existing = db.query_to_dict(check_query, (athlete_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    athlete_info = existing[0]
    
    # Check if athlete has associated data
    data_check_query = """
        SELECT 
            (SELECT COUNT(*) FROM dados_gps WHERE atleta_id = %s) as gps_count,
            (SELECT COUNT(*) FROM dados_pse WHERE atleta_id = %s) as pse_count
    """
    data_counts = db.query_to_dict(data_check_query, (athlete_id, athlete_id))[0]
    
    has_data = data_counts['gps_count'] > 0 or data_counts['pse_count'] > 0
    
    try:
        if permanent and not has_data:
            # Permanent deletion only if no associated data
            delete_query = "DELETE FROM atletas WHERE id = %s"
            db.execute_query(delete_query, (athlete_id,))
            
            return {
                "status": "deleted",
                "message": f"Athlete {athlete_info['nome_completo']} permanently deleted",
                "athlete_id": athlete_id
            }
        else:
            # Soft delete (deactivate)
            deactivate_query = "UPDATE atletas SET ativo = false, updated_at = NOW() WHERE id = %s"
            db.execute_query(deactivate_query, (athlete_id,))
            
            reason = "has associated data" if has_data else "soft delete requested"
            
            return {
                "status": "deactivated",
                "message": f"Athlete {athlete_info['nome_completo']} deactivated ({reason})",
                "athlete_id": athlete_id,
                "data_preserved": {
                    "gps_records": data_counts['gps_count'],
                    "pse_records": data_counts['pse_count']
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting athlete: {str(e)}")


@router.post("/{athlete_id}/reactivate")
def reactivate_athlete(
    athlete_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    """Reactivate a deactivated athlete"""
    
    # Check if athlete exists and is inactive
    check_query = "SELECT id, nome_completo, ativo FROM atletas WHERE id = %s"
    existing = db.query_to_dict(check_query, (athlete_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    athlete_info = existing[0]
    
    if athlete_info['ativo']:
        raise HTTPException(status_code=400, detail="Athlete is already active")
    
    try:
        reactivate_query = "UPDATE atletas SET ativo = true, updated_at = NOW() WHERE id = %s"
        db.execute_query(reactivate_query, (athlete_id,))
        
        return {
            "status": "reactivated",
            "message": f"Athlete {athlete_info['nome_completo']} reactivated",
            "athlete_id": athlete_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reactivating athlete: {str(e)}")


@router.get("/{athlete_id}/sessions")
def get_athlete_sessions(
    athlete_id: int,
    limit: int = 50,
    db: DatabaseConnection = Depends(get_db)
):
    """Get detailed session history for an athlete"""
    
    # Check if athlete exists
    check_query = "SELECT nome_completo FROM atletas WHERE id = %s"
    athlete = db.query_to_dict(check_query, (athlete_id,))
    
    if not athlete:
        raise HTTPException(status_code=404, detail="Athlete not found")
    
    sessions_query = """
        SELECT DISTINCT
            s.id, s.data, s.tipo, s.duracao_min, s.jornada, s.competicao,
            g.distancia_total, g.velocidade_max, g.aceleracoes, g.desaceleracoes,
            g.effs_19_8_kmh, g.dist_19_8_kmh, g.effs_25_2_kmh,
            p.pse, p.carga_total, p.qualidade_sono, p.stress, p.fadiga, p.dor_muscular
        FROM sessoes s
        LEFT JOIN dados_gps g ON g.sessao_id = s.id AND g.atleta_id = %s
        LEFT JOIN dados_pse p ON p.sessao_id = s.id AND p.atleta_id = %s
        WHERE g.atleta_id IS NOT NULL OR p.atleta_id IS NOT NULL
        ORDER BY s.data DESC, s.id DESC
        LIMIT %s
    """
    
    sessions = db.query_to_dict(sessions_query, (athlete_id, athlete_id, limit))
    
    return {
        "athlete_id": athlete_id,
        "athlete_name": athlete[0]['nome_completo'],
        "total_sessions": len(sessions),
        "sessions": sessions
    }
