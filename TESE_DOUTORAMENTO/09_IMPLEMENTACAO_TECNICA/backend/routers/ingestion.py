from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import Dict, Any
import pandas as pd
import io
from datetime import datetime, date
import hashlib
from database import get_db, DatabaseConnection
from PIL import Image
import base64
import tempfile
import os

router = APIRouter()


def match_player_name(csv_name: str, db: DatabaseConnection) -> int:
    """Match CSV player name to database athlete ID"""
    
    clean_name = csv_name.strip().lower()
    
    query = """
        SELECT id, nome_completo, jogador_id
        FROM atletas
        WHERE LOWER(nome_completo) = %s OR LOWER(jogador_id) = %s
        ORDER BY ativo DESC
        LIMIT 1
    """
    result = db.query_to_dict(query, (clean_name, clean_name))
    
    if result:
        return result[0]['id']
    
    similarity_query = """
        SELECT id, nome_completo
        FROM atletas
        WHERE similarity(LOWER(nome_completo), %s) > 0.6
        ORDER BY similarity(LOWER(nome_completo), %s) DESC
        LIMIT 1
    """
    similar = db.query_to_dict(similarity_query, (clean_name, clean_name))
    
    if similar:
        return similar[0]['id']
    
    raise ValueError(f"Player not found: {csv_name}")


async def handle_non_csv_upload(
    file: UploadFile,
    jornada: int,
    session_date: str,
    db: DatabaseConnection,
    data_type: str
) -> Dict[str, Any]:
    """
    Handle PDF and image file uploads
    For now, stores the file and returns metadata for manual processing
    """
    
    try:
        contents = await file.read()
        file_hash = hashlib.sha256(contents).hexdigest()
        
        if session_date:
            parsed_date = datetime.strptime(session_date, "%Y-%m-%d").date()
        else:
            parsed_date = date.today()
        
        session_id = create_or_get_session(jornada, parsed_date, db, file.filename)
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with unique name
        file_ext = os.path.splitext(file.filename.lower())[1]
        safe_filename = f"{data_type}_jornada{jornada}_{parsed_date}_{file_hash[:8]}{file_ext}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # For images, try to get basic info
        file_info = {
            "filename": file.filename,
            "safe_filename": safe_filename,
            "file_path": file_path,
            "file_size": len(contents),
            "file_type": file_ext
        }
        
        if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
            try:
                with Image.open(io.BytesIO(contents)) as img:
                    file_info.update({
                        "image_width": img.width,
                        "image_height": img.height,
                        "image_mode": img.mode
                    })
            except Exception as e:
                file_info["image_error"] = str(e)
        
        # Store file metadata in database for tracking
        metadata_query = """
            INSERT INTO file_uploads (
                sessao_id, filename, file_path, file_hash, 
                file_type, data_type, jornada, upload_date, 
                file_size, metadata, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
            ON CONFLICT DO NOTHING
        """
        
        try:
            db.execute_query(metadata_query, (
                session_id,
                file.filename,
                file_path,
                file_hash,
                file_ext,
                data_type,
                jornada,
                parsed_date,
                len(contents),
                str(file_info)
            ))
        except Exception as db_error:
            # If table doesn't exist, continue without storing metadata
            print(f"Warning: Could not store file metadata: {db_error}")
        
        return {
            "status": "uploaded",
            "message": f"File uploaded successfully. Manual processing required for {file_ext} files.",
            "file": file.filename,
            "file_hash": file_hash,
            "file_path": file_path,
            "jornada": jornada,
            "session_id": session_id,
            "session_date": str(parsed_date),
            "data_type": data_type,
            "file_info": file_info,
            "next_steps": [
                "File has been saved for manual processing",
                "Extract data from the file manually or using OCR tools",
                "Use the CSV upload endpoint to import the extracted data"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing {file_ext} file: {str(e)}")


def create_or_get_session(jornada: int, session_date: date, db: DatabaseConnection, filename: str = None) -> int:
    """Create or get session for a jornada with training type from filename"""
    
    # Check for existing session (any type) for this jornada and date
    check_query = """
        SELECT id FROM sessoes
        WHERE jornada = %s AND data = %s
        ORDER BY created_at DESC
        LIMIT 1
    """
    existing = db.query_to_dict(check_query, (jornada, session_date))
    
    if existing:
        return existing[0]['id']
    
    # Extract training type from filename - use only valid database values
    training_type = "treino"  # default
    description = "Training Session"  # default
    
    if filename:
        filename_lower = filename.lower()
        if "recovery" in filename_lower:
            training_type = "recuperacao"
            description = "Recovery Training"
        elif "match" in filename_lower:
            training_type = "jogo"
            description = "Match"
        elif any(word in filename_lower for word in ["technical", "tactical", "physical", "prematch"]):
            training_type = "treino"
            # Set specific descriptions while keeping valid database type
            if "technical" in filename_lower:
                description = "Technical Training"
            elif "tactical" in filename_lower:
                description = "Tactical Training"
            elif "physical" in filename_lower:
                description = "Physical Training"
            elif "prematch" in filename_lower:
                description = "Pre-Match Training"
        else:
            # Try to extract day pattern (day1, day2, etc.)
            import re
            day_match = re.search(r'day(\d+)', filename_lower)
            if day_match:
                day_num = int(day_match.group(1))
                if day_num == 1 or day_num == 7:
                    training_type = "recuperacao"
                    description = "Recovery Training"
                elif day_num == 6:
                    training_type = "jogo"
                    description = "Match"
                else:
                    training_type = "treino"
                    if day_num == 2:
                        description = "Technical Training"
                    elif day_num == 3:
                        description = "Tactical Training"
                    elif day_num == 4:
                        description = "Physical Training"
                    elif day_num == 5:
                        description = "Pre-Match Training"
    
    # Create new session with proper training type using proper transaction handling
    try:
        # Use execute_query for the insert (which commits)
        insert_query = """
            INSERT INTO sessoes (data, tipo, duracao_min, jornada, competicao, created_at)
            VALUES (%s, %s, 90, %s, %s, NOW())
        """
        db.execute_query(insert_query, (session_date, training_type, jornada, description))
        
        # Then get the session ID with a separate query
        get_id_query = """
            SELECT id FROM sessoes
            WHERE jornada = %s AND data = %s AND tipo = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        result = db.query_to_dict(get_id_query, (jornada, session_date, training_type))
        
        if result:
            return result[0]['id']
        else:
            raise Exception("Failed to retrieve created session ID")
            
    except Exception as e:
        raise Exception(f"Failed to create session: {str(e)}")


@router.post("/catapult")
async def ingest_catapult_csv(
    file: UploadFile = File(...),
    jornada: int = 1,
    session_date: str = None,
    db: DatabaseConnection = Depends(get_db)
):
    """
    Ingest Catapult CSV export
    Expected columns: player, total_distance_m, max_velocity_kmh, etc.
    """
    
    # Accept CSV, PDF, and image files
    allowed_extensions = ['.csv', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    file_ext = os.path.splitext(file.filename.lower())[1]
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File must be one of: {', '.join(allowed_extensions)}")
    
    # Handle non-CSV files
    if file_ext != '.csv':
        return await handle_non_csv_upload(file, jornada, session_date, db, 'gps')
    
    try:
        contents = await file.read()
        file_hash = hashlib.sha256(contents).hexdigest()
        
        df = pd.read_csv(io.BytesIO(contents))
        
        required_cols = ['player', 'total_distance_m', 'max_velocity_kmh']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing}"
            )
        
        if session_date:
            parsed_date = datetime.strptime(session_date, "%Y-%m-%d").date()
        else:
            parsed_date = date.today()
        
        session_id = create_or_get_session(jornada, parsed_date, db, file.filename)
        
        inserted_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                athlete_id = match_player_name(row['player'], db)
                
                insert_query = """
                    INSERT INTO dados_gps (
                        time, atleta_id, sessao_id,
                        distancia_total, velocidade_max,
                        aceleracoes, desaceleracoes,
                        effs_19_8_kmh, dist_19_8_kmh,
                        effs_25_2_kmh,
                        fonte, created_at
                    ) VALUES (
                        %s, %s, %s,
                        %s, %s,
                        %s, %s,
                        %s, %s,
                        %s,
                        %s, NOW()
                    )
                    ON CONFLICT DO NOTHING
                """
                
                db.execute_query(insert_query, (
                    datetime.combine(parsed_date, datetime.min.time()),
                    athlete_id,
                    session_id,
                    float(row['total_distance_m']) if pd.notna(row.get('total_distance_m')) else None,
                    float(row['max_velocity_kmh']) if pd.notna(row.get('max_velocity_kmh')) else None,
                    int(row['acc_b1_3_total_efforts']) if pd.notna(row.get('acc_b1_3_total_efforts')) else None,
                    int(row['decel_b1_3_total_efforts']) if pd.notna(row.get('decel_b1_3_total_efforts')) else None,
                    int(row['efforts_over_19_8_kmh']) if pd.notna(row.get('efforts_over_19_8_kmh')) else None,
                    float(row['distance_over_19_8_kmh']) if pd.notna(row.get('distance_over_19_8_kmh')) else None,
                    int(row['efforts_over_25_2_kmh']) if pd.notna(row.get('efforts_over_25_2_kmh')) else None,
                    f'catapult_csv_{file.filename}'
                ))
                
                inserted_count += 1
                
            except ValueError as e:
                errors.append(f"Row {idx}: {str(e)}")
            except Exception as e:
                errors.append(f"Row {idx}: Unexpected error - {str(e)}")
        
        return {
            "status": "success",
            "file": file.filename,
            "file_hash": file_hash,
            "jornada": jornada,
            "session_id": session_id,
            "session_date": str(parsed_date),
            "total_rows": len(df),
            "inserted": inserted_count,
            "errors": errors
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Upload error: {str(e)}")
        print(f"❌ Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/pse")
async def ingest_pse_csv(
    file: UploadFile = File(...),
    jornada: int = 1,
    session_date: str = None,
    db: DatabaseConnection = Depends(get_db)
):
    """
    Ingest PSE/Wellness CSV export
    Expected columns: Nome, Pos, Sono, Stress, Fadiga, DOMS, VOLUME, Rpe, CARGA
    """
    
    # Accept CSV, PDF, and image files
    allowed_extensions = ['.csv', '.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    file_ext = os.path.splitext(file.filename.lower())[1]
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File must be one of: {', '.join(allowed_extensions)}")
    
    # Handle non-CSV files
    if file_ext != '.csv':
        return await handle_non_csv_upload(file, jornada, session_date, db, 'pse')
    
    try:
        contents = await file.read()
        file_hash = hashlib.sha256(contents).hexdigest()
        
        df = pd.read_csv(io.BytesIO(contents))
        
        required_cols = ['Nome', 'Sono', 'Stress', 'Fadiga', 'DOMS', 'VOLUME', 'Rpe', 'CARGA']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {missing}"
            )
        
        if session_date:
            parsed_date = datetime.strptime(session_date, "%Y-%m-%d").date()
        else:
            parsed_date = date.today()
        
        session_id = create_or_get_session(jornada, parsed_date, db, file.filename)
        
        inserted_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                athlete_id = match_player_name(row['Nome'], db)
                
                # Normalize values to fit database constraints - sleep quality must be 1-5 (NOT 1-10!)
                sono_raw = row['Sono'] if pd.notna(row['Sono']) else 3
                sono = max(1, min(5, int(float(sono_raw))))
                
                stress_raw = row['Stress'] if pd.notna(row['Stress']) else 3
                stress = max(1, min(5, int(float(stress_raw))))
                
                fadiga_raw = row['Fadiga'] if pd.notna(row['Fadiga']) else 3
                fadiga = max(1, min(5, int(float(fadiga_raw))))
                
                doms_raw = row['DOMS'] if pd.notna(row['DOMS']) else 2
                doms = max(1, min(5, int(float(doms_raw))))
                
                duracao = int(float(row['VOLUME'])) if pd.notna(row['VOLUME']) else 90
                
                rpe_raw = row['Rpe'] if pd.notna(row['Rpe']) else 5
                rpe = max(1, min(10, int(float(rpe_raw))))
                
                carga = int(float(row['CARGA'])) if pd.notna(row['CARGA']) else (duracao * rpe)
                
                # Handle optional muscle pain column
                dores_musculares = 2  # default
                if 'DORES MUSCULARES' in row and pd.notna(row['DORES MUSCULARES']):
                    dores_musculares = max(1, min(5, int(row['DORES MUSCULARES'])))
                
                insert_query = """
                    INSERT INTO dados_pse (
                        time, atleta_id, sessao_id,
                        qualidade_sono, stress, fadiga, dor_muscular,
                        duracao_min, pse, carga_total,
                        fonte, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    )
                    ON CONFLICT DO NOTHING
                """
                
                db.execute_query(insert_query, (
                    datetime.combine(parsed_date, datetime.min.time()),
                    athlete_id,
                    session_id,
                    sono,
                    stress,
                    fadiga,
                    dores_musculares,
                    duracao,
                    rpe,
                    carga,
                    file.filename
                ))
                
                inserted_count += 1
                
            except ValueError as e:
                errors.append(f"Row {idx}: {str(e)}")
            except Exception as e:
                errors.append(f"Row {idx}: Unexpected error - {str(e)}")
        
        return {
            "status": "success",
            "file": file.filename,
            "file_hash": file_hash,
            "jornada": jornada,
            "session_id": session_id,
            "session_date": str(parsed_date),
            "total_rows": len(df),
            "inserted": inserted_count,
            "errors": errors
        }
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ PSE Upload error: {str(e)}")
        print(f"❌ Full traceback: {error_details}")
        raise HTTPException(status_code=500, detail=f"Error processing PSE file: {str(e)}")


@router.get("/history")
def get_ingestion_history(
    limit: int = 20,
    db: DatabaseConnection = Depends(get_db)
):
    """Get recent ingestion history"""
    
    try:
        # Combined query to show both GPS and PSE uploads
        query = """
            (
                SELECT DISTINCT
                    COALESCE(fonte, 'unknown') as fonte,
                    sessao_id,
                    DATE(time) as data,
                    COUNT(*) as num_records,
                    MIN(created_at) as ingested_at,
                    'GPS' as tipo_dados
                FROM dados_gps
                WHERE fonte IS NOT NULL
                GROUP BY fonte, sessao_id, DATE(time)
            )
            UNION ALL
            (
                SELECT DISTINCT
                    COALESCE(fonte, 'pse_upload') as fonte,
                    sessao_id,
                    DATE(time) as data,
                    COUNT(*) as num_records,
                    MIN(created_at) as ingested_at,
                    'PSE' as tipo_dados
                FROM dados_pse
                WHERE sessao_id IS NOT NULL
                GROUP BY fonte, sessao_id, DATE(time)
            )
            ORDER BY ingested_at DESC
            LIMIT %s
        """
        
        return db.query_to_dict(query, (limit,))
    except Exception as e:
        # Fallback query if there are issues - show GPS data only
        fallback_query = """
            SELECT DISTINCT
                'gps_data' as fonte,
                sessao_id,
                DATE(time) as data,
                COUNT(*) as num_records,
                MIN(time) as ingested_at,
                'GPS' as tipo_dados
            FROM dados_gps
            GROUP BY sessao_id, DATE(time)
            ORDER BY ingested_at DESC
            LIMIT %s
        """
        return db.query_to_dict(fallback_query, (limit,))


@router.get("/session/{session_id}/data")
def get_session_data(
    session_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    """Get detailed data for a specific session"""
    
    try:
        # Get session info
        session_query = """
            SELECT id, data, tipo, jornada, duracao_min, competicao, created_at
            FROM sessoes
            WHERE id = %s
        """
        session_info = db.query_to_dict(session_query, (session_id,))
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get GPS data count
        gps_query = """
            SELECT COUNT(*) as count
            FROM dados_gps
            WHERE sessao_id = %s
        """
        gps_count = db.query_to_dict(gps_query, (session_id,))[0]['count']
        
        # Get PSE data count
        pse_query = """
            SELECT COUNT(*) as count
            FROM dados_pse
            WHERE sessao_id = %s
        """
        pse_count = db.query_to_dict(pse_query, (session_id,))[0]['count']
        
        # Get sample GPS data (first 5 records)
        gps_sample_query = """
            SELECT a.nome_completo, g.distancia_total, g.velocidade_max, g.aceleracoes, g.desaceleracoes
            FROM dados_gps g
            JOIN atletas a ON g.atleta_id = a.id
            WHERE g.sessao_id = %s
            ORDER BY a.nome_completo
            LIMIT 5
        """
        gps_sample = db.query_to_dict(gps_sample_query, (session_id,))
        
        # Get sample PSE data (first 5 records)
        pse_sample_query = """
            SELECT a.nome_completo, p.qualidade_sono, p.stress, p.fadiga, p.pse, p.carga_total
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session data: {str(e)}")


@router.post("/gps-journey-image")
async def ingest_gps_journey_image(
    file: UploadFile = File(...),
    jornada: int = 1,
    session_date: str = None,
    db: DatabaseConnection = Depends(get_db)
):
    """
    Upload GPS journey image/PDF for manual data extraction
    Specifically designed for Catapult team metrics reports like JOGO_2ªJORNADA
    """
    
    allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
    file_ext = os.path.splitext(file.filename.lower())[1]
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File must be an image or PDF: {', '.join(allowed_extensions)}")
    
    try:
        contents = await file.read()
        file_hash = hashlib.sha256(contents).hexdigest()
        
        if session_date:
            parsed_date = datetime.strptime(session_date, "%Y-%m-%d").date()
        else:
            parsed_date = date.today()
        
        session_id = create_or_get_session(jornada, parsed_date, db, file.filename)
        
        # Create uploads directory
        upload_dir = "uploads/gps_journeys"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with descriptive name
        safe_filename = f"gps_journey_jornada{jornada}_{parsed_date}_{file_hash[:8]}{file_ext}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Get image info if it's an image
        file_info = {
            "filename": file.filename,
            "safe_filename": safe_filename,
            "file_path": file_path,
            "file_size": len(contents),
            "file_type": file_ext
        }
        
        if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
            try:
                with Image.open(io.BytesIO(contents)) as img:
                    file_info.update({
                        "image_width": img.width,
                        "image_height": img.height,
                        "image_mode": img.mode
                    })
            except Exception as e:
                file_info["image_error"] = str(e)
        
        return {
            "status": "uploaded",
            "message": "GPS journey file uploaded successfully. Ready for manual data extraction.",
            "file": file.filename,
            "file_hash": file_hash,
            "file_path": file_path,
            "jornada": jornada,
            "session_id": session_id,
            "session_date": str(parsed_date),
            "file_info": file_info,
            "instructions": [
                "1. View the uploaded file to extract team metrics data",
                "2. Create a CSV file with the following columns:",
                "   - jogador_id (player name)",
                "   - tot_dist_m (total distance in meters)",
                "   - max_vel_kmh (max velocity in km/h)",
                "   - acc_b1_3_tot (total accelerations)",
                "   - decel_b1_3_tot_effs_gen2 (total decelerations)",
                "   - effs_415_4_kmh (efforts >19.8 km/h)",
                "   - dist_415_8_kmh (distance in high velocity zone)",
                "   - effs_425_2_kmh (efforts >25.2 km/h)",
                "   - vel_b3_tot_effs_gen2 (total velocity efforts/sprints)",
                "3. Upload the CSV using the regular /catapult endpoint"
            ],
            "example_script": f"Use the script 'carregar_jornada_gps.py' as a template for data extraction"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing GPS journey file: {str(e)}")


@router.get("/uploaded-files")
def get_uploaded_files(
    limit: int = 20,
    data_type: str = None,
    db: DatabaseConnection = Depends(get_db)
):
    """Get list of uploaded PDF/image files"""
    
    try:
        # List files from uploads directory
        upload_dirs = ["uploads", "uploads/gps_journeys"]
        files = []
        
        for upload_dir in upload_dirs:
            if os.path.exists(upload_dir):
                for filename in os.listdir(upload_dir):
                    file_path = os.path.join(upload_dir, filename)
                    if os.path.isfile(file_path):
                        stat = os.stat(file_path)
                        files.append({
                            "filename": filename,
                            "file_path": file_path,
                            "file_size": stat.st_size,
                            "upload_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "directory": upload_dir
                        })
        
        # Sort by upload time (newest first)
        files.sort(key=lambda x: x["upload_time"], reverse=True)
        
        # Apply limit
        if limit:
            files = files[:limit]
        
        return {
            "status": "success",
            "files": files,
            "total_files": len(files)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing uploaded files: {str(e)}")


@router.delete("/session/{session_id}")
def delete_session(
    session_id: int,
    db: DatabaseConnection = Depends(get_db)
):
    """Delete a session and all its associated data"""
    
    try:
        # Check if session exists
        session_query = "SELECT id, jornada, data FROM sessoes WHERE id = %s"
        session_info = db.query_to_dict(session_query, (session_id,))
        
        if not session_info:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_info[0]
        
        # Count records before deletion
        gps_count_query = "SELECT COUNT(*) as count FROM dados_gps WHERE sessao_id = %s"
        pse_count_query = "SELECT COUNT(*) as count FROM dados_pse WHERE sessao_id = %s"
        
        gps_count = db.query_to_dict(gps_count_query, (session_id,))[0]['count']
        pse_count = db.query_to_dict(pse_count_query, (session_id,))[0]['count']
        
        # Delete in correct order (foreign key constraints)
        db.execute_query("DELETE FROM dados_gps WHERE sessao_id = %s", (session_id,))
        db.execute_query("DELETE FROM dados_pse WHERE sessao_id = %s", (session_id,))
        db.execute_query("DELETE FROM sessoes WHERE id = %s", (session_id,))
        
        return {
            "status": "success",
            "message": f"Session {session_id} deleted successfully",
            "session": {
                "id": session['id'],
                "jornada": session['jornada'],
                "data": str(session['data'])
            },
            "deleted_records": {
                "gps": gps_count,
                "pse": pse_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")
