from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import date
from database import get_db, DatabaseConnection

router = APIRouter()


class SessionCreate(BaseModel):
    data: date
    tipo: str
    adversario: Optional[str] = None
    jornada: Optional[int] = None
    resultado: Optional[str] = None
    duracao_min: Optional[int] = 90
    local: Optional[str] = "Casa"
    competicao: Optional[str] = None


class SessionUpdate(BaseModel):
    data: Optional[date] = None
    tipo: Optional[str] = None
    adversario: Optional[str] = None
    jornada: Optional[int] = None
    resultado: Optional[str] = None
    duracao_min: Optional[int] = None
    local: Optional[str] = None
    competicao: Optional[str] = None


@router.get("/", response_model=List[Dict[str, Any]])
def list_sessions(
    tipo: Optional[str] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limit: int = Query(200, le=500),
    db: DatabaseConnection = Depends(get_db)
):
    conditions = []
    params = []
    
    if tipo:
        conditions.append("tipo = %s")
        params.append(tipo)
    
    if data_inicio:
        conditions.append("data >= %s")
        params.append(data_inicio)
    
    if data_fim:
        conditions.append("data <= %s")
        params.append(data_fim)
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    query = f"""
        SELECT 
            id, data, hora_inicio, tipo, duracao_min, training_type,
            adversario, local, competicao, jornada, resultado,
            condicoes_meteorologicas, temperatura_celsius, observacoes
        FROM sessoes
        {where_clause}
        ORDER BY data DESC, hora_inicio DESC
        LIMIT %s
    """
    params.append(limit)
    
    return db.query_to_dict(query, tuple(params))


@router.get("/{session_id}", response_model=Dict[str, Any])
def get_session(
    session_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    query = """
        SELECT 
            id, data, hora_inicio, tipo, duracao_min, training_type,
            adversario, local, competicao, jornada, resultado,
            condicoes_meteorologicas, temperatura_celsius, observacoes
        FROM sessoes
        WHERE id = %s
    """
    result = db.query_to_dict(query, (session_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    
    gps_query = """
        SELECT 
            g.atleta_id,
            a.nome_completo,
            a.posicao,
            g.distancia_total,
            g.velocidade_max,
            g.velocidade_media,
            g.sprints,
            g.aceleracoes,
            g.desaceleracoes,
            g.player_load,
            g.dist_19_8_kmh,
            g.dist_25_2_kmh,
            g.effs_19_8_kmh,
            g.effs_25_2_kmh
        FROM dados_gps g
        JOIN atletas a ON g.atleta_id = a.id
        WHERE g.sessao_id = %s
        ORDER BY a.nome_completo
    """
    gps_data = db.query_to_dict(gps_query, (session_id,))
    
    session = result[0]
    session['gps_data'] = gps_data
    
    return session


@router.post("/", response_model=Dict[str, Any])
def create_session(
    session: SessionCreate,
    db: DatabaseConnection = Depends(get_db)
):
    """Create a new session"""
    
    try:
        insert_query = """
            INSERT INTO sessoes (
                data, tipo, adversario, jornada, resultado, 
                duracao_min, local, competicao, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
            RETURNING id, data, tipo, adversario, jornada, resultado,
                     duracao_min, local, competicao, created_at
        """
        
        result = db.query_to_dict(insert_query, (
            session.data,
            session.tipo,
            session.adversario,
            session.jornada,
            session.resultado,
            session.duracao_min,
            session.local,
            session.competicao
        ))
        
        if result:
            return result[0]
        else:
            raise HTTPException(status_code=500, detail="Failed to create session")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.put("/{session_id}", response_model=Dict[str, Any])
def update_session(
    session_id: int,
    session_update: SessionUpdate,
    db: DatabaseConnection = Depends(get_db)
):
    """Update an existing session"""
    
    # Check if session exists
    check_query = "SELECT id FROM sessoes WHERE id = %s"
    existing = db.query_to_dict(check_query, (session_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Build dynamic update query
    update_fields = []
    update_values = []
    
    for field, value in session_update.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            update_values.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    try:
        update_values.append(session_id)
        
        update_query = f"""
            UPDATE sessoes 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, data, tipo, adversario, jornada, resultado,
                     duracao_min, local, competicao
        """
        
        result = db.query_to_dict(update_query, update_values)
        
        if result:
            return result[0]
        else:
            raise HTTPException(status_code=500, detail="Failed to update session")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")


@router.delete("/{session_id}")
def delete_session(
    session_id: int,
    permanent: bool = False,
    db: DatabaseConnection = Depends(get_db)
):
    """Delete a session and all its associated data"""
    
    # Check if session exists
    check_query = "SELECT id, data, tipo, jornada, adversario FROM sessoes WHERE id = %s"
    existing = db.query_to_dict(check_query, (session_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_info = existing[0]
    
    # Count associated data
    data_check_query = """
        SELECT 
            (SELECT COUNT(*) FROM dados_gps WHERE sessao_id = %s) as gps_count,
            (SELECT COUNT(*) FROM dados_pse WHERE sessao_id = %s) as pse_count
    """
    data_counts = db.query_to_dict(data_check_query, (session_id, session_id))[0]
    
    try:
        # Delete associated data first (foreign key constraints)
        db.execute_query("DELETE FROM dados_gps WHERE sessao_id = %s", (session_id,))
        db.execute_query("DELETE FROM dados_pse WHERE sessao_id = %s", (session_id,))
        
        # Delete the session
        db.execute_query("DELETE FROM sessoes WHERE id = %s", (session_id,))
        
        return {
            "status": "deleted",
            "message": f"Session {session_id} deleted successfully",
            "session": {
                "id": session_info['id'],
                "data": str(session_info['data']),
                "tipo": session_info['tipo'],
                "jornada": session_info['jornada'],
                "adversario": session_info['adversario']
            },
            "deleted_records": {
                "gps": data_counts['gps_count'],
                "pse": data_counts['pse_count']
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


@router.get("/{session_id}/data")
def get_session_detailed_data(
    session_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    """Get detailed data for a specific session including PSE data"""
    
    # Get session info
    session_query = """
        SELECT 
            id, data, tipo, jornada, duracao_min, adversario, local,
            competicao, resultado, created_at
        FROM sessoes
        WHERE id = %s
    """
    session_info = db.query_to_dict(session_query, (session_id,))
    
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get GPS data count
    gps_query = "SELECT COUNT(*) as count FROM dados_gps WHERE sessao_id = %s"
    gps_count = db.query_to_dict(gps_query, (session_id,))[0]['count']
    
    # Get PSE data count
    pse_query = "SELECT COUNT(*) as count FROM dados_pse WHERE sessao_id = %s"
    pse_count = db.query_to_dict(pse_query, (session_id,))[0]['count']
    
    # Get sample GPS data (first 5 records)
    gps_sample_query = """
        SELECT a.nome_completo, g.distancia_total, g.velocidade_max, 
               g.aceleracoes, g.desaceleracoes
        FROM dados_gps g
        JOIN atletas a ON g.atleta_id = a.id
        WHERE g.sessao_id = %s
        ORDER BY a.nome_completo
        LIMIT 5
    """
    gps_sample = db.query_to_dict(gps_sample_query, (session_id,))
    
    # Get sample PSE data (first 5 records)
    pse_sample_query = """
        SELECT a.nome_completo, p.qualidade_sono, p.stress, p.fadiga, 
               p.pse, p.carga_total
        FROM dados_pse p
        JOIN atletas a ON p.atleta_id = a.id
        WHERE p.sessao_id = %s
        ORDER BY a.nome_completo
        LIMIT 5
    """
    pse_sample = db.query_to_dict(pse_sample_query, (session_id,))
    
    return {
        "session": session_info[0],
        "gps_count": gps_count,
        "pse_count": pse_count,
        "gps_sample": gps_sample,
        "pse_sample": pse_sample
    }
