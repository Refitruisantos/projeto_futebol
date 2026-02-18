"""
Spatial Analysis Router for Football Tactical Analysis
Provides endpoints for generating and serving spatial data and shapefiles
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel
import os
import tempfile
import zipfile
import json
from pathlib import Path

from database import DatabaseConnection
from spatial_analysis.shapefile_generator import (
    TacticalShapefileGenerator, 
    SpatialPlayerPosition,
    generate_tactical_shapefiles_from_analysis
)

router = APIRouter()

class ShapefileGenerationRequest(BaseModel):
    analysis_id: str
    include_players: bool = True
    include_pressure_zones: bool = True
    include_formation_lines: bool = True
    include_tactical_zones: bool = True
    output_format: str = "shapefile"  # "shapefile" or "geojson"

class SpatialAnalysisResponse(BaseModel):
    status: str
    message: str
    files_generated: Dict[str, str]
    download_url: Optional[str] = None

@router.post("/generate-shapefiles/{analysis_id}")
async def generate_analysis_shapefiles(
    analysis_id: str,
    request: ShapefileGenerationRequest,
    background_tasks: BackgroundTasks
):
    """Generate shapefiles from tactical analysis results"""
    
    try:
        db = DatabaseConnection()
        
        # Get analysis data
        analysis = db.query_to_dict("""
            SELECT analysis_id, video_path, results, status, session_id
            FROM video_analysis 
            WHERE analysis_id = %s
        """, (analysis_id,))
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis = analysis[0]
        results = analysis.get('results', {})
        
        # Handle different result formats
        if isinstance(results, str):
            try:
                results = json.loads(results)
            except json.JSONDecodeError:
                results = {}
        elif results is None:
            results = {}
        
        # Create temporary directory for shapefiles
        temp_dir = tempfile.mkdtemp(prefix=f"tactical_shapefiles_{analysis_id[:8]}_")
        
        # Generate shapefiles
        output_files = generate_tactical_shapefiles_from_analysis(results, temp_dir)
        
        if not output_files:
            raise HTTPException(status_code=500, detail="Failed to generate shapefiles")
        
        # Create ZIP file with all shapefiles
        zip_path = os.path.join(temp_dir, f"tactical_analysis_{analysis_id[:8]}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for shapefile_type, file_path in output_files.items():
                if os.path.exists(file_path):
                    # Add the main file
                    zipf.write(file_path, os.path.basename(file_path))
                    
                    # For shapefiles, also add associated files (.shx, .dbf, .prj, etc.)
                    if file_path.endswith('.shp'):
                        base_path = file_path[:-4]  # Remove .shp extension
                        associated_extensions = ['.shx', '.dbf', '.prj', '.cpg']
                        
                        for ext in associated_extensions:
                            assoc_file = base_path + ext
                            if os.path.exists(assoc_file):
                                zipf.write(assoc_file, os.path.basename(assoc_file))
        
        return SpatialAnalysisResponse(
            status="success",
            message="Shapefiles generated successfully",
            files_generated=output_files,
            download_url=f"/api/spatial-analysis/download/{analysis_id}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/download/{analysis_id}")
async def download_shapefiles(analysis_id: str):
    """Download generated shapefiles as ZIP"""
    
    # Find the ZIP file in temp directory
    temp_dirs = [d for d in os.listdir(tempfile.gettempdir()) 
                if d.startswith(f"tactical_shapefiles_{analysis_id[:8]}_")]
    
    if not temp_dirs:
        raise HTTPException(status_code=404, detail="Shapefiles not found or expired")
    
    # Get the most recent directory
    temp_dir = os.path.join(tempfile.gettempdir(), max(temp_dirs))
    zip_path = os.path.join(temp_dir, f"tactical_analysis_{analysis_id[:8]}.zip")
    
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="ZIP file not found")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"tactical_analysis_{analysis_id[:8]}.zip"
    )

@router.get("/spatial-interpretation/{analysis_id}")
async def get_spatial_interpretation(analysis_id: str):
    """Get spatial interpretation of tactical analysis results"""
    
    try:
        db = DatabaseConnection()
        
        # Get analysis data
        analysis = db.query_to_dict("""
            SELECT analysis_id, results, status, session_id
            FROM video_analysis 
            WHERE analysis_id = %s
        """, (analysis_id,))
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        analysis = analysis[0]
        results = analysis.get('results', {})
        
        # Handle different result formats
        if isinstance(results, str):
            try:
                results = json.loads(results)
            except json.JSONDecodeError:
                results = {}
        elif results is None:
            results = {}
        
        # Generate spatial interpretation
        interpretation = generate_spatial_interpretation(results)
        
        return {
            "analysis_id": analysis_id,
            "spatial_interpretation": interpretation,
            "coordinate_system": "Field coordinates (105m x 68m)",
            "units": "meters"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    finally:
        try:
            db.close()
        except:
            pass

@router.get("/field-geometry")
async def get_field_geometry():
    """Get standard football field geometry for GIS applications"""
    
    from spatial_analysis.shapefile_generator import FootballFieldGeometry
    
    field = FootballFieldGeometry()
    
    return {
        "field_dimensions": {
            "length": field.field_length,
            "width": field.field_width,
            "units": "meters"
        },
        "coordinate_system": {
            "origin": "(0, 0) at bottom-left corner",
            "x_axis": "Field length (0-105m)",
            "y_axis": "Field width (0-68m)",
            "crs": "Local field coordinates"
        },
        "key_areas": {
            "penalty_areas": {
                "length": field.penalty_area_length,
                "width": field.penalty_area_width
            },
            "goal_areas": {
                "length": field.goal_area_length,
                "width": field.goal_area_width
            },
            "center_circle": {
                "radius": field.center_circle_radius
            }
        },
        "tactical_zones": {
            "defensive_third": {"x_range": [0, 35], "description": "Defensive zone"},
            "middle_third": {"x_range": [35, 70], "description": "Midfield zone"},
            "attacking_third": {"x_range": [70, 105], "description": "Attacking zone"}
        }
    }

def generate_spatial_interpretation(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate spatial interpretation from tactical analysis results"""
    
    interpretation = {
        "spatial_analysis": {},
        "geometric_features": {},
        "tactical_zones": {},
        "spatial_relationships": {}
    }
    
    # Handle None or empty results
    if not results:
        results = {}
    
    # Extract spatial metrics from results
    if 'tactical_analysis' in results:
        tactical = results['tactical_analysis']
        
        # Spatial distribution analysis
        interpretation["spatial_analysis"] = {
            "player_distribution": {
                "description": "Analysis of player positioning across field zones",
                "metrics": {
                    "field_coverage": "Percentage of field area covered by players",
                    "clustering_coefficient": "Measure of player grouping tendency",
                    "spatial_balance": "Left-right field balance ratio"
                }
            },
            "pressure_mapping": {
                "description": "Spatial representation of pressure zones",
                "ball_pressure_zone": {
                    "center_coordinates": [52.5, 34],  # Field center as example
                    "radius_meters": 10.0,
                    "area_coverage": 314.16,  # π * r²
                    "player_density": "Players per square meter in zone"
                }
            }
        }
    
    # Geometric feature analysis
    interpretation["geometric_features"] = {
        "formation_shapes": {
            "defensive_line": {
                "geometry_type": "LineString",
                "description": "Linear formation of defensive players",
                "spatial_properties": {
                    "length": "Width of defensive line in meters",
                    "compactness": "Standard deviation of player depths",
                    "angle": "Orientation relative to goal line"
                }
            },
            "team_convex_hull": {
                "geometry_type": "Polygon",
                "description": "Minimum area containing all team players",
                "spatial_properties": {
                    "area": "Total area occupied by team",
                    "perimeter": "Boundary length of team formation",
                    "centroid": "Geometric center of team positioning"
                }
            }
        },
        "pressure_zones": {
            "geometry_type": "Polygon (Circular)",
            "description": "Areas of high player concentration",
            "spatial_properties": {
                "overlap_analysis": "Intersection of team pressure zones",
                "coverage_efficiency": "Ratio of covered to total field area"
            }
        }
    }
    
    # Tactical zone analysis
    interpretation["tactical_zones"] = {
        "field_thirds": {
            "defensive_third": {
                "coordinates": [[0, 0], [35, 0], [35, 68], [0, 68]],
                "player_count_home": "Number of home team players in zone",
                "player_count_away": "Number of away team players in zone",
                "control_percentage": "Relative team control of zone"
            },
            "middle_third": {
                "coordinates": [[35, 0], [70, 0], [70, 68], [35, 68]],
                "description": "Primary contest zone for midfield control"
            },
            "attacking_third": {
                "coordinates": [[70, 0], [105, 0], [105, 68], [70, 68]],
                "description": "Final third attacking opportunities"
            }
        },
        "corridors": {
            "left_corridor": {
                "coordinates": [[0, 0], [105, 0], [105, 22.67], [0, 22.67]],
                "description": "Left flank tactical corridor"
            },
            "central_corridor": {
                "coordinates": [[0, 22.67], [105, 22.67], [105, 45.33], [0, 45.33]],
                "description": "Central tactical corridor"
            },
            "right_corridor": {
                "coordinates": [[0, 45.33], [105, 45.33], [105, 68], [0, 68]],
                "description": "Right flank tactical corridor"
            }
        }
    }
    
    # Spatial relationships
    interpretation["spatial_relationships"] = {
        "distance_analysis": {
            "player_to_player": {
                "description": "Euclidean distances between all players",
                "applications": ["Pressure analysis", "Passing options", "Defensive coverage"]
            },
            "player_to_ball": {
                "description": "Distance from each player to ball position",
                "applications": ["Pressure intensity", "Support positioning", "Recovery runs"]
            },
            "line_to_line": {
                "description": "Distances between formation lines",
                "applications": ["Compactness analysis", "Space exploitation", "Pressing coordination"]
            }
        },
        "spatial_coverage": {
            "voronoi_diagrams": {
                "description": "Areas of field responsibility for each player",
                "applications": ["Defensive coverage", "Space control", "Positioning optimization"]
            },
            "influence_zones": {
                "description": "Areas where players can effectively intervene",
                "applications": ["Interception probability", "Passing lane coverage", "Pressing effectiveness"]
            }
        }
    }
    
    return interpretation

@router.get("/gis-metadata/{analysis_id}")
async def get_gis_metadata(analysis_id: str):
    """Get GIS metadata for tactical analysis shapefiles"""
    
    return {
        "analysis_id": analysis_id,
        "coordinate_reference_system": {
            "name": "Football Field Local Coordinates",
            "type": "Projected",
            "units": "meters",
            "origin": "Bottom-left corner of field (0,0)",
            "extent": {
                "x_min": 0,
                "x_max": 105,
                "y_min": 0,
                "y_max": 68
            }
        },
        "layer_information": {
            "player_positions": {
                "geometry_type": "Point",
                "attributes": ["player_id", "team", "jersey_number", "role", "x_coord", "y_coord"],
                "description": "Individual player positions at analysis moment"
            },
            "pressure_zones": {
                "geometry_type": "Polygon",
                "attributes": ["zone_type", "radius", "center_x", "center_y", "area"],
                "description": "Circular zones representing pressure areas"
            },
            "formation_lines": {
                "geometry_type": "LineString",
                "attributes": ["line_type", "team", "player_count", "length", "avg_depth"],
                "description": "Linear formations connecting players by role"
            },
            "tactical_zones": {
                "geometry_type": "Polygon",
                "attributes": ["zone_type", "zone_name", "area"],
                "description": "Standard football field tactical zones"
            }
        },
        "spatial_analysis_capabilities": [
            "Distance calculations",
            "Area coverage analysis", 
            "Spatial clustering",
            "Proximity analysis",
            "Geometric relationship analysis",
            "Zone occupation statistics"
        ],
        "recommended_gis_software": [
            "QGIS (Open Source)",
            "ArcGIS",
            "PostGIS",
            "GeoPandas (Python)",
            "Leaflet (Web mapping)"
        ]
    }
