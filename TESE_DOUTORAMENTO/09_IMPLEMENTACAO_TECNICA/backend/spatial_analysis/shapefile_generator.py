"""
Shapefile Generator for Football Tactical Analysis
Converts tactical analysis results into spatial data structures and shapefiles
"""

import numpy as np
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import tempfile
import os

try:
    import geopandas as gpd
    import shapely
    from shapely.geometry import Point, Polygon, LineString, MultiPoint
    from shapely.ops import convex_hull
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False
    print("GeoPandas not available. Install with: pip install geopandas")
    # Create dummy classes for when GeoPandas is not available
    class Point:
        def __init__(self, x, y): pass
        def buffer(self, radius): return None
    class Polygon:
        def __init__(self, coords): pass
        @property
        def area(self): return 0
    class LineString:
        def __init__(self, coords): pass
        @property
        def length(self): return 0

@dataclass
class SpatialPlayerPosition:
    """Spatial representation of a player position"""
    player_id: int
    team: str
    position: Tuple[float, float]  # (x, y) in meters
    jersey_number: int
    role: str
    timestamp: float = 0.0

class FootballFieldGeometry:
    """Standard football field geometry and coordinate system"""
    
    def __init__(self):
        # FIFA standard field dimensions (meters)
        self.field_length = 105.0  # Length (x-axis)
        self.field_width = 68.0    # Width (y-axis)
        
        # Goal dimensions
        self.goal_width = 7.32
        self.goal_depth = 2.44
        
        # Penalty area dimensions
        self.penalty_area_length = 16.5
        self.penalty_area_width = 40.32
        
        # Goal area dimensions
        self.goal_area_length = 5.5
        self.goal_area_width = 18.32
        
        # Center circle radius
        self.center_circle_radius = 9.15
        
    def create_field_boundary(self) -> Polygon:
        """Create field boundary polygon"""
        return Polygon([
            (0, 0),
            (self.field_length, 0),
            (self.field_length, self.field_width),
            (0, self.field_width),
            (0, 0)
        ])
    
    def create_penalty_areas(self) -> List[Polygon]:
        """Create penalty area polygons"""
        # Left penalty area
        left_penalty = Polygon([
            (0, (self.field_width - self.penalty_area_width) / 2),
            (self.penalty_area_length, (self.field_width - self.penalty_area_width) / 2),
            (self.penalty_area_length, (self.field_width + self.penalty_area_width) / 2),
            (0, (self.field_width + self.penalty_area_width) / 2),
            (0, (self.field_width - self.penalty_area_width) / 2)
        ])
        
        # Right penalty area
        right_penalty = Polygon([
            (self.field_length - self.penalty_area_length, (self.field_width - self.penalty_area_width) / 2),
            (self.field_length, (self.field_width - self.penalty_area_width) / 2),
            (self.field_length, (self.field_width + self.penalty_area_width) / 2),
            (self.field_length - self.penalty_area_length, (self.field_width + self.penalty_area_width) / 2),
            (self.field_length - self.penalty_area_length, (self.field_width - self.penalty_area_width) / 2)
        ])
        
        return [left_penalty, right_penalty]
    
    def create_field_thirds(self) -> List[Polygon]:
        """Create field third zones for tactical analysis"""
        third_length = self.field_length / 3
        
        defensive_third = Polygon([
            (0, 0),
            (third_length, 0),
            (third_length, self.field_width),
            (0, self.field_width),
            (0, 0)
        ])
        
        middle_third = Polygon([
            (third_length, 0),
            (2 * third_length, 0),
            (2 * third_length, self.field_width),
            (third_length, self.field_width),
            (third_length, 0)
        ])
        
        attacking_third = Polygon([
            (2 * third_length, 0),
            (self.field_length, 0),
            (self.field_length, self.field_width),
            (2 * third_length, self.field_width),
            (2 * third_length, 0)
        ])
        
        return [defensive_third, middle_third, attacking_third]

class TacticalShapefileGenerator:
    """Generate shapefiles from tactical analysis results"""
    
    def __init__(self):
        self.field_geometry = FootballFieldGeometry()
        
    def create_player_points_shapefile(self, players: List[SpatialPlayerPosition]) -> Dict[str, Any]:
        """Create point shapefile for player positions"""
        if not GEOPANDAS_AVAILABLE:
            return self._create_geojson_alternative(players)
        
        # Create points for each player
        geometries = []
        attributes = []
        
        for player in players:
            point = Point(player.position[0], player.position[1])
            geometries.append(point)
            
            attributes.append({
                'player_id': player.player_id,
                'team': player.team,
                'jersey_num': player.jersey_number,
                'role': player.role,
                'x_coord': player.position[0],
                'y_coord': player.position[1],
                'timestamp': player.timestamp
            })
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(attributes, geometry=geometries)
        gdf.crs = "EPSG:3857"  # Web Mercator for visualization
        
        return {
            'type': 'shapefile',
            'data': gdf,
            'geometry_type': 'Point',
            'feature_count': len(players)
        }
    
    def create_pressure_zones_shapefile(self, players: List[SpatialPlayerPosition], 
                                      ball_position: Tuple[float, float],
                                      pressure_radius: float = 10.0) -> Dict[str, Any]:
        """Create polygon shapefile for pressure zones"""
        if not GEOPANDAS_AVAILABLE:
            return self._create_pressure_zones_geojson(players, ball_position, pressure_radius)
        
        geometries = []
        attributes = []
        
        # Ball pressure zone
        ball_circle = Point(ball_position).buffer(pressure_radius)
        geometries.append(ball_circle)
        attributes.append({
            'zone_type': 'ball_pressure',
            'radius': pressure_radius,
            'center_x': ball_position[0],
            'center_y': ball_position[1],
            'area': ball_circle.area
        })
        
        # Individual player pressure zones
        for player in players:
            player_circle = Point(player.position).buffer(pressure_radius / 2)
            geometries.append(player_circle)
            attributes.append({
                'zone_type': 'player_influence',
                'player_id': player.player_id,
                'team': player.team,
                'radius': pressure_radius / 2,
                'center_x': player.position[0],
                'center_y': player.position[1],
                'area': player_circle.area
            })
        
        gdf = gpd.GeoDataFrame(attributes, geometry=geometries)
        gdf.crs = "EPSG:3857"
        
        return {
            'type': 'shapefile',
            'data': gdf,
            'geometry_type': 'Polygon',
            'feature_count': len(geometries)
        }
    
    def create_formation_lines_shapefile(self, players: List[SpatialPlayerPosition]) -> Dict[str, Any]:
        """Create line shapefile for formation analysis"""
        if not GEOPANDAS_AVAILABLE:
            return self._create_formation_lines_geojson(players)
        
        geometries = []
        attributes = []
        
        # Group players by team
        teams = {}
        for player in players:
            if player.team not in teams:
                teams[player.team] = []
            teams[player.team].append(player)
        
        for team_name, team_players in teams.items():
            if len(team_players) < 2:
                continue
                
            # Sort players by position for formation lines
            sorted_players = sorted(team_players, key=lambda p: p.position[0])
            
            # Create defensive line
            defenders = [p for p in sorted_players if p.role == 'defender']
            if len(defenders) >= 2:
                defender_points = [Point(p.position) for p in defenders]
                if len(defender_points) >= 2:
                    # Create line connecting defenders
                    coords = [(p.position[0], p.position[1]) for p in defenders]
                    coords.sort(key=lambda x: x[1])  # Sort by y-coordinate
                    
                    if len(coords) >= 2:
                        line = LineString(coords)
                        geometries.append(line)
                        attributes.append({
                            'line_type': 'defensive_line',
                            'team': team_name,
                            'player_count': len(defenders),
                            'length': line.length,
                            'avg_depth': np.mean([p.position[0] for p in defenders])
                        })
            
            # Create midfield line
            midfielders = [p for p in sorted_players if p.role == 'midfielder']
            if len(midfielders) >= 2:
                coords = [(p.position[0], p.position[1]) for p in midfielders]
                coords.sort(key=lambda x: x[1])
                
                if len(coords) >= 2:
                    line = LineString(coords)
                    geometries.append(line)
                    attributes.append({
                        'line_type': 'midfield_line',
                        'team': team_name,
                        'player_count': len(midfielders),
                        'length': line.length,
                        'avg_depth': np.mean([p.position[0] for p in midfielders])
                    })
        
        if not geometries:
            return {'type': 'empty', 'message': 'No formation lines could be created'}
        
        gdf = gpd.GeoDataFrame(attributes, geometry=geometries)
        gdf.crs = "EPSG:3857"
        
        return {
            'type': 'shapefile',
            'data': gdf,
            'geometry_type': 'LineString',
            'feature_count': len(geometries)
        }
    
    def create_tactical_zones_shapefile(self) -> Dict[str, Any]:
        """Create polygon shapefile for tactical field zones"""
        if not GEOPANDAS_AVAILABLE:
            return self._create_tactical_zones_geojson()
        
        geometries = []
        attributes = []
        
        # Field boundary
        field_boundary = self.field_geometry.create_field_boundary()
        geometries.append(field_boundary)
        attributes.append({
            'zone_type': 'field_boundary',
            'zone_name': 'Full Field',
            'area': field_boundary.area,
            'length': self.field_geometry.field_length,
            'width': self.field_geometry.field_width
        })
        
        # Field thirds
        thirds = self.field_geometry.create_field_thirds()
        zone_names = ['Defensive Third', 'Middle Third', 'Attacking Third']
        
        for i, third in enumerate(thirds):
            geometries.append(third)
            attributes.append({
                'zone_type': 'field_third',
                'zone_name': zone_names[i],
                'area': third.area,
                'third_number': i + 1
            })
        
        # Penalty areas
        penalty_areas = self.field_geometry.create_penalty_areas()
        penalty_names = ['Left Penalty Area', 'Right Penalty Area']
        
        for i, penalty in enumerate(penalty_areas):
            geometries.append(penalty)
            attributes.append({
                'zone_type': 'penalty_area',
                'zone_name': penalty_names[i],
                'area': penalty.area,
                'side': 'left' if i == 0 else 'right'
            })
        
        gdf = gpd.GeoDataFrame(attributes, geometry=geometries)
        gdf.crs = "EPSG:3857"
        
        return {
            'type': 'shapefile',
            'data': gdf,
            'geometry_type': 'Polygon',
            'feature_count': len(geometries)
        }
    
    def export_shapefile(self, shapefile_data: Dict[str, Any], output_path: str) -> str:
        """Export shapefile data to file"""
        if not GEOPANDAS_AVAILABLE or shapefile_data.get('type') != 'shapefile':
            # Export as GeoJSON instead
            return self._export_geojson(shapefile_data, output_path)
        
        gdf = shapefile_data['data']
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Export to shapefile
        gdf.to_file(output_path, driver='ESRI Shapefile')
        
        return output_path
    
    def _create_geojson_alternative(self, players: List[SpatialPlayerPosition]) -> Dict[str, Any]:
        """Create GeoJSON alternative when GeoPandas is not available"""
        features = []
        
        for player in players:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [player.position[0], player.position[1]]
                },
                "properties": {
                    "player_id": player.player_id,
                    "team": player.team,
                    "jersey_number": player.jersey_number,
                    "role": player.role,
                    "timestamp": player.timestamp
                }
            }
            features.append(feature)
        
        return {
            'type': 'geojson',
            'data': {
                "type": "FeatureCollection",
                "features": features
            },
            'geometry_type': 'Point',
            'feature_count': len(features)
        }
    
    def _create_pressure_zones_geojson(self, players: List[SpatialPlayerPosition], 
                                     ball_position: Tuple[float, float],
                                     pressure_radius: float) -> Dict[str, Any]:
        """Create GeoJSON for pressure zones"""
        features = []
        
        # Ball pressure zone (circle approximation with polygon)
        def create_circle_coords(center, radius, num_points=32):
            angles = np.linspace(0, 2 * np.pi, num_points)
            coords = []
            for angle in angles:
                x = center[0] + radius * np.cos(angle)
                y = center[1] + radius * np.sin(angle)
                coords.append([x, y])
            coords.append(coords[0])  # Close the polygon
            return coords
        
        # Ball pressure zone
        ball_coords = create_circle_coords(ball_position, pressure_radius)
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [ball_coords]
            },
            "properties": {
                "zone_type": "ball_pressure",
                "radius": pressure_radius,
                "center_x": ball_position[0],
                "center_y": ball_position[1]
            }
        })
        
        return {
            'type': 'geojson',
            'data': {
                "type": "FeatureCollection",
                "features": features
            },
            'geometry_type': 'Polygon',
            'feature_count': len(features)
        }
    
    def _create_formation_lines_geojson(self, players: List[SpatialPlayerPosition]) -> Dict[str, Any]:
        """Create GeoJSON for formation lines"""
        features = []
        
        # Group players by team and role
        teams = {}
        for player in players:
            if player.team not in teams:
                teams[player.team] = {'defenders': [], 'midfielders': [], 'forwards': []}
            
            if player.role == 'defender':
                teams[player.team]['defenders'].append(player)
            elif player.role == 'midfielder':
                teams[player.team]['midfielders'].append(player)
            elif player.role == 'forward':
                teams[player.team]['forwards'].append(player)
        
        for team_name, roles in teams.items():
            for role_name, role_players in roles.items():
                if len(role_players) >= 2:
                    # Sort by y-coordinate for line creation
                    sorted_players = sorted(role_players, key=lambda p: p.position[1])
                    coords = [[p.position[0], p.position[1]] for p in sorted_players]
                    
                    features.append({
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": coords
                        },
                        "properties": {
                            "line_type": f"{role_name}_line",
                            "team": team_name,
                            "player_count": len(role_players)
                        }
                    })
        
        return {
            'type': 'geojson',
            'data': {
                "type": "FeatureCollection",
                "features": features
            },
            'geometry_type': 'LineString',
            'feature_count': len(features)
        }
    
    def _create_tactical_zones_geojson(self) -> Dict[str, Any]:
        """Create GeoJSON for tactical zones"""
        features = []
        
        # Field boundary
        field_coords = [
            [0, 0],
            [self.field_geometry.field_length, 0],
            [self.field_geometry.field_length, self.field_geometry.field_width],
            [0, self.field_geometry.field_width],
            [0, 0]
        ]
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [field_coords]
            },
            "properties": {
                "zone_type": "field_boundary",
                "zone_name": "Full Field",
                "length": self.field_geometry.field_length,
                "width": self.field_geometry.field_width
            }
        })
        
        # Field thirds
        third_length = self.field_geometry.field_length / 3
        thirds_data = [
            ("Defensive Third", 0, third_length),
            ("Middle Third", third_length, 2 * third_length),
            ("Attacking Third", 2 * third_length, self.field_geometry.field_length)
        ]
        
        for name, start_x, end_x in thirds_data:
            coords = [
                [start_x, 0],
                [end_x, 0],
                [end_x, self.field_geometry.field_width],
                [start_x, self.field_geometry.field_width],
                [start_x, 0]
            ]
            
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                },
                "properties": {
                    "zone_type": "field_third",
                    "zone_name": name
                }
            })
        
        return {
            'type': 'geojson',
            'data': {
                "type": "FeatureCollection",
                "features": features
            },
            'geometry_type': 'Polygon',
            'feature_count': len(features)
        }
    
    def _export_geojson(self, geojson_data: Dict[str, Any], output_path: str) -> str:
        """Export GeoJSON data to file"""
        # Change extension to .geojson
        if output_path.endswith('.shp'):
            output_path = output_path.replace('.shp', '.geojson')
        elif not output_path.endswith('.geojson'):
            output_path += '.geojson'
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(geojson_data['data'], f, indent=2)
        
        return output_path

def generate_tactical_shapefiles_from_analysis(analysis_results: Dict[str, Any], 
                                             output_dir: str) -> Dict[str, str]:
    """Generate all tactical shapefiles from analysis results"""
    
    generator = TacticalShapefileGenerator()
    output_files = {}
    
    # Handle None or empty analysis results
    if not analysis_results:
        analysis_results = {}
    
    # Extract player positions from analysis results
    players = []
    if 'player_tracking' in analysis_results:
        # Convert analysis results to spatial player positions
        # This would be populated from actual analysis data
        pass
    
    # Generate sample data for demonstration
    sample_players = [
        SpatialPlayerPosition(1, 'home', (20, 15), 1, 'defender'),
        SpatialPlayerPosition(2, 'home', (25, 25), 2, 'defender'),
        SpatialPlayerPosition(3, 'home', (25, 43), 3, 'defender'),
        SpatialPlayerPosition(4, 'home', (20, 53), 4, 'defender'),
        SpatialPlayerPosition(5, 'home', (45, 20), 5, 'midfielder'),
        SpatialPlayerPosition(6, 'home', (45, 48), 6, 'midfielder'),
        SpatialPlayerPosition(7, 'home', (65, 34), 7, 'forward'),
        
        SpatialPlayerPosition(8, 'away', (85, 34), 8, 'defender'),
        SpatialPlayerPosition(9, 'away', (80, 20), 9, 'defender'),
        SpatialPlayerPosition(10, 'away', (80, 48), 10, 'defender'),
        SpatialPlayerPosition(11, 'away', (60, 25), 11, 'midfielder'),
        SpatialPlayerPosition(12, 'away', (60, 43), 12, 'midfielder'),
        SpatialPlayerPosition(13, 'away', (40, 34), 13, 'forward'),
    ]
    
    ball_position = (52.5, 34)  # Center of field
    
    try:
        # Generate player positions shapefile
        player_shapefile = generator.create_player_points_shapefile(sample_players)
        player_output = os.path.join(output_dir, 'player_positions.shp')
        output_files['players'] = generator.export_shapefile(player_shapefile, player_output)
        
        # Generate pressure zones shapefile
        pressure_shapefile = generator.create_pressure_zones_shapefile(sample_players, ball_position)
        pressure_output = os.path.join(output_dir, 'pressure_zones.shp')
        output_files['pressure_zones'] = generator.export_shapefile(pressure_shapefile, pressure_output)
        
        # Generate formation lines shapefile
        formation_shapefile = generator.create_formation_lines_shapefile(sample_players)
        formation_output = os.path.join(output_dir, 'formation_lines.shp')
        output_files['formation_lines'] = generator.export_shapefile(formation_shapefile, formation_output)
        
        # Generate tactical zones shapefile
        zones_shapefile = generator.create_tactical_zones_shapefile()
        zones_output = os.path.join(output_dir, 'tactical_zones.shp')
        output_files['tactical_zones'] = generator.export_shapefile(zones_shapefile, zones_output)
        
    except Exception as e:
        print(f"Error generating shapefiles: {e}")
        return {}
    
    return output_files
