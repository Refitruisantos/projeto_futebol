from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from database import get_db, DatabaseConnection

router = APIRouter()


class OpponentCreate(BaseModel):
    opponent_name: str
    league_position: int
    recent_form_points: int
    home_advantage: bool
    head_to_head_record: str
    key_players_available: int
    tactical_difficulty: int
    physical_intensity: int
    overall_rating: float
    explanation: Optional[str] = None
    detailed_breakdown: Optional[str] = None


class OpponentUpdate(BaseModel):
    opponent_name: Optional[str] = None
    league_position: Optional[int] = None
    recent_form_points: Optional[int] = None
    home_advantage: Optional[bool] = None
    head_to_head_record: Optional[str] = None
    key_players_available: Optional[int] = None
    tactical_difficulty: Optional[int] = None
    physical_intensity: Optional[int] = None
    overall_rating: Optional[float] = None
    explanation: Optional[str] = None
    detailed_breakdown: Optional[str] = None


@router.get("/", response_model=List[Dict[str, Any]])
def list_opponents(
    db: DatabaseConnection = Depends(get_db)
):
    """Get all opponents with their characteristics"""
    
    query = """
        SELECT 
            id, opponent_name, league_position, recent_form_points,
            home_advantage, head_to_head_record, key_players_available,
            tactical_difficulty, physical_intensity, overall_rating,
            explanation, detailed_breakdown, created_at
        FROM opponent_difficulty_details
        ORDER BY overall_rating DESC, opponent_name
    """
    
    return db.query_to_dict(query)


@router.get("/{opponent_id}", response_model=Dict[str, Any])
def get_opponent(
    opponent_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    """Get specific opponent details"""
    
    query = """
        SELECT 
            id, opponent_name, league_position, recent_form_points,
            home_advantage, head_to_head_record, key_players_available,
            tactical_difficulty, physical_intensity, overall_rating,
            explanation, detailed_breakdown, created_at
        FROM opponent_difficulty_details
        WHERE id = %s
    """
    
    result = db.query_to_dict(query, (opponent_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Opponent not found")
    
    return result[0]


@router.post("/", response_model=Dict[str, Any])
def create_opponent(
    opponent: OpponentCreate,
    db: DatabaseConnection = Depends(get_db)
):
    """Create a new opponent profile"""
    
    # Check if opponent already exists
    check_query = "SELECT id FROM opponent_difficulty_details WHERE opponent_name = %s"
    existing = db.query_to_dict(check_query, (opponent.opponent_name,))
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Opponent '{opponent.opponent_name}' already exists")
    
    try:
        insert_query = """
            INSERT INTO opponent_difficulty_details (
                opponent_name, league_position, recent_form_points, home_advantage,
                head_to_head_record, key_players_available, tactical_difficulty,
                physical_intensity, overall_rating, explanation, detailed_breakdown,
                created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
            RETURNING id, opponent_name, league_position, recent_form_points,
                     home_advantage, head_to_head_record, key_players_available,
                     tactical_difficulty, physical_intensity, overall_rating,
                     explanation, created_at
        """
        
        result = db.query_to_dict(insert_query, (
            opponent.opponent_name,
            opponent.league_position,
            opponent.recent_form_points,
            opponent.home_advantage,
            opponent.head_to_head_record,
            opponent.key_players_available,
            opponent.tactical_difficulty,
            opponent.physical_intensity,
            opponent.overall_rating,
            opponent.explanation,
            opponent.detailed_breakdown
        ))
        
        if result:
            return result[0]
        else:
            raise HTTPException(status_code=500, detail="Failed to create opponent")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating opponent: {str(e)}")


@router.put("/{opponent_id}", response_model=Dict[str, Any])
def update_opponent(
    opponent_id: int,
    opponent_update: OpponentUpdate,
    db: DatabaseConnection = Depends(get_db)
):
    """Update an existing opponent"""
    
    # Check if opponent exists
    check_query = "SELECT id FROM opponent_difficulty_details WHERE id = %s"
    existing = db.query_to_dict(check_query, (opponent_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="Opponent not found")
    
    # Build dynamic update query
    update_fields = []
    update_values = []
    
    for field, value in opponent_update.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            update_values.append(value)
    
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Check for name conflicts if updating opponent_name
    if opponent_update.opponent_name:
        conflict_query = "SELECT id FROM opponent_difficulty_details WHERE opponent_name = %s AND id != %s"
        conflict = db.query_to_dict(conflict_query, (opponent_update.opponent_name, opponent_id))
        if conflict:
            raise HTTPException(status_code=400, detail=f"Opponent name '{opponent_update.opponent_name}' already exists")
    
    try:
        update_values.append(opponent_id)
        
        update_query = f"""
            UPDATE opponent_difficulty_details 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, opponent_name, league_position, recent_form_points,
                     home_advantage, head_to_head_record, key_players_available,
                     tactical_difficulty, physical_intensity, overall_rating,
                     explanation, detailed_breakdown
        """
        
        result = db.query_to_dict(update_query, update_values)
        
        if result:
            return result[0]
        else:
            raise HTTPException(status_code=500, detail="Failed to update opponent")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating opponent: {str(e)}")


@router.delete("/{opponent_id}")
def delete_opponent(
    opponent_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    """Delete an opponent"""
    
    # Check if opponent exists
    check_query = "SELECT id, opponent_name FROM opponent_difficulty_details WHERE id = %s"
    existing = db.query_to_dict(check_query, (opponent_id,))
    
    if not existing:
        raise HTTPException(status_code=404, detail="Opponent not found")
    
    opponent_info = existing[0]
    
    # Check if opponent is referenced in sessions
    sessions_query = """
        SELECT COUNT(*) as count 
        FROM sessoes 
        WHERE adversario = %s
    """
    sessions_count = db.query_to_dict(sessions_query, (opponent_info['opponent_name'],))[0]['count']
    
    try:
        if sessions_count > 0:
            # Don't delete if referenced in sessions, just return warning
            return {
                "status": "warning",
                "message": f"Cannot delete opponent '{opponent_info['opponent_name']}' - referenced in {sessions_count} sessions",
                "opponent_id": opponent_id,
                "sessions_count": sessions_count,
                "suggestion": "Update sessions to use different opponent name first, or keep this opponent profile"
            }
        else:
            # Safe to delete
            delete_query = "DELETE FROM opponent_difficulty_details WHERE id = %s"
            db.execute_query(delete_query, (opponent_id,))
            
            return {
                "status": "deleted",
                "message": f"Opponent '{opponent_info['opponent_name']}' deleted successfully",
                "opponent_id": opponent_id
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting opponent: {str(e)}")


@router.get("/{opponent_id}/sessions")
def get_opponent_sessions(
    opponent_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    """Get all sessions against this opponent"""
    
    # Get opponent name first
    opponent_query = "SELECT opponent_name FROM opponent_difficulty_details WHERE id = %s"
    opponent_result = db.query_to_dict(opponent_query, (opponent_id,))
    
    if not opponent_result:
        raise HTTPException(status_code=404, detail="Opponent not found")
    
    opponent_name = opponent_result[0]['opponent_name']
    
    # Get sessions against this opponent
    sessions_query = """
        SELECT 
            s.id, s.data, s.tipo, s.jornada, s.resultado, s.local,
            s.dificuldade_adversario, s.duracao_min, s.competicao,
            COUNT(DISTINCT dg.atleta_id) as gps_players,
            COUNT(DISTINCT dp.atleta_id) as pse_players,
            AVG(dp.carga_total) as avg_load
        FROM sessoes s
        LEFT JOIN dados_gps dg ON s.id = dg.sessao_id
        LEFT JOIN dados_pse dp ON s.id = dp.sessao_id
        WHERE s.adversario = %s
        GROUP BY s.id, s.data, s.tipo, s.jornada, s.resultado, s.local,
                 s.dificuldade_adversario, s.duracao_min, s.competicao
        ORDER BY s.data DESC
    """
    
    sessions = db.query_to_dict(sessions_query, (opponent_name,))
    
    return {
        "opponent_id": opponent_id,
        "opponent_name": opponent_name,
        "total_sessions": len(sessions),
        "sessions": sessions
    }


@router.get("/search/{search_term}")
def search_opponents(
    search_term: str,
    db: DatabaseConnection = Depends(get_db)
):
    """Search opponents by name"""
    
    query = """
        SELECT 
            id, opponent_name, league_position, overall_rating,
            tactical_difficulty, physical_intensity
        FROM opponent_difficulty_details
        WHERE opponent_name ILIKE %s
        ORDER BY overall_rating DESC
        LIMIT 10
    """
    
    search_pattern = f"%{search_term}%"
    results = db.query_to_dict(query, (search_pattern,))
    
    return {
        "search_term": search_term,
        "results": results
    }
