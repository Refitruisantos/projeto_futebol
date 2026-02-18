"""
Advanced Tactical Football Analysis
- Distance calculations between players
- Pressure level analysis
- Defensive formation analysis
- Sector and corridor alignment measurements
"""

import cv2
import numpy as np
import json
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import math
from collections import defaultdict

@dataclass
class PlayerPosition:
    """Player position with tactical information"""
    player_id: int
    team: str
    position: Tuple[float, float]  # x, y coordinates
    jersey_number: Optional[int]
    role: str  # 'defender', 'midfielder', 'forward', 'goalkeeper'
    
@dataclass
class TacticalMetrics:
    """Tactical analysis metrics"""
    pressure_levels: Dict[str, float]
    formation_analysis: Dict[str, any]
    distance_metrics: Dict[str, float]
    alignment_scores: Dict[str, float]
    sector_analysis: Dict[str, any]

class TacticalAnalyzer:
    """Advanced tactical analysis for football videos"""
    
    def __init__(self, field_length=105, field_width=68):
        # Standard football field dimensions in meters
        self.field_length = field_length
        self.field_width = field_width
        
        # Define tactical zones
        self.defensive_third = field_length / 3
        self.middle_third = field_length / 3
        self.attacking_third = field_length / 3
        
        # Corridor definitions (left, center, right)
        self.corridor_width = field_width / 3
        
    def calculate_player_distances(self, players: List[PlayerPosition]) -> Dict[str, float]:
        """Calculate distances between players for pressure analysis"""
        distances = {}
        
        # Calculate distances between all players
        for i, player1 in enumerate(players):
            for j, player2 in enumerate(players[i+1:], i+1):
                key = f"player_{player1.player_id}_to_{player2.player_id}"
                distance = self._euclidean_distance(player1.position, player2.position)
                distances[key] = distance
        
        return distances
    
    def analyze_pressure_levels(self, players: List[PlayerPosition], ball_position: Tuple[float, float]) -> Dict[str, float]:
        """Analyze pressure levels around the ball and key areas"""
        pressure_metrics = {}
        
        # Find players near the ball (within 10 meters)
        ball_pressure_radius = 10.0
        players_near_ball = []
        all_distances_to_ball = []
        
        for player in players:
            distance_to_ball = self._euclidean_distance(player.position, ball_position)
            all_distances_to_ball.append(distance_to_ball)
            if distance_to_ball <= ball_pressure_radius:
                players_near_ball.append((player, distance_to_ball))
        
        # Calculate pressure intensity and distances
        pressure_metrics['ball_pressure_intensity'] = len(players_near_ball)
        pressure_metrics['avg_distance_to_ball'] = round(np.mean([d for _, d in players_near_ball]), 2) if players_near_ball else 0
        pressure_metrics['min_distance_to_ball'] = round(min(all_distances_to_ball), 2) if all_distances_to_ball else 0
        pressure_metrics['max_distance_to_ball'] = round(max(all_distances_to_ball), 2) if all_distances_to_ball else 0
        pressure_metrics['avg_all_distances_to_ball'] = round(np.mean(all_distances_to_ball), 2) if all_distances_to_ball else 0
        
        # Team-specific pressure
        home_pressure = len([p for p, d in players_near_ball if p.team == 'home'])
        away_pressure = len([p for p, d in players_near_ball if p.team == 'away'])
        
        pressure_metrics['home_team_pressure'] = home_pressure
        pressure_metrics['away_team_pressure'] = away_pressure
        pressure_metrics['pressure_ratio'] = round(home_pressure / max(away_pressure, 1), 2)
        
        # Calculate pressure distance averages by team
        home_distances = [d for p, d in players_near_ball if p.team == 'home']
        away_distances = [d for p, d in players_near_ball if p.team == 'away']
        
        pressure_metrics['home_avg_pressure_distance'] = round(np.mean(home_distances), 2) if home_distances else 0
        pressure_metrics['away_avg_pressure_distance'] = round(np.mean(away_distances), 2) if away_distances else 0
        
        # Additional pressure metrics
        pressure_metrics['pressure_density'] = round(len(players_near_ball) / (ball_pressure_radius ** 2), 4)
        pressure_metrics['total_players_analyzed'] = len(players)
        
        return pressure_metrics
    
    def analyze_defensive_formation(self, defensive_players: List[PlayerPosition]) -> Dict[str, any]:
        """Analyze defensive formation and alignment"""
        if len(defensive_players) < 3:
            return {"error": "Not enough defensive players for analysis"}
        
        formation_analysis = {}
        
        # Sort defenders by x-position (depth)
        sorted_defenders = sorted(defensive_players, key=lambda p: p.position[0])
        
        # Calculate defensive line depth consistency
        x_positions = [p.position[0] for p in sorted_defenders]
        formation_analysis['defensive_line_depth_avg'] = round(np.mean(x_positions), 2)
        formation_analysis['defensive_line_depth_std'] = round(np.std(x_positions), 2)
        formation_analysis['defensive_line_compactness'] = round(max(x_positions) - min(x_positions), 2)
        formation_analysis['defensive_line_min_depth'] = round(min(x_positions), 2)
        formation_analysis['defensive_line_max_depth'] = round(max(x_positions), 2)
        
        # Calculate width of defensive line
        y_positions = [p.position[1] for p in sorted_defenders]
        formation_analysis['defensive_width'] = round(max(y_positions) - min(y_positions), 2)
        formation_analysis['defensive_width_avg'] = round(np.mean(y_positions), 2)
        formation_analysis['defensive_width_std'] = round(np.std(y_positions), 2)
        formation_analysis['defensive_left_position'] = round(min(y_positions), 2)
        formation_analysis['defensive_right_position'] = round(max(y_positions), 2)
        
        # Analyze gaps between defenders
        gaps = []
        sorted_by_width = sorted(defensive_players, key=lambda p: p.position[1])
        for i in range(len(sorted_by_width) - 1):
            gap = abs(sorted_by_width[i+1].position[1] - sorted_by_width[i].position[1])
            gaps.append(gap)
        
        formation_analysis['avg_gap_between_defenders'] = round(np.mean(gaps), 2) if gaps else 0
        formation_analysis['min_gap_between_defenders'] = round(min(gaps), 2) if gaps else 0
        formation_analysis['max_gap_between_defenders'] = round(max(gaps), 2) if gaps else 0
        formation_analysis['total_defensive_gaps'] = len(gaps)
        formation_analysis['gap_consistency'] = round(np.std(gaps), 2) if gaps else 0
        
        return formation_analysis
    
    def analyze_sectors_and_corridors(self, players: List[PlayerPosition]) -> Dict[str, any]:
        """Analyze player distribution across field sectors and corridors"""
        sector_analysis = {
            'defensive_third': {'home': 0, 'away': 0, 'players': []},
            'middle_third': {'home': 0, 'away': 0, 'players': []},
            'attacking_third': {'home': 0, 'away': 0, 'players': []},
            'left_corridor': {'home': 0, 'away': 0, 'players': []},
            'center_corridor': {'home': 0, 'away': 0, 'players': []},
            'right_corridor': {'home': 0, 'away': 0, 'players': []}
        }
        
        for player in players:
            x, y = player.position
            
            # Determine sector (thirds of the field)
            if x < self.defensive_third:
                sector = 'defensive_third'
            elif x < self.defensive_third + self.middle_third:
                sector = 'middle_third'
            else:
                sector = 'attacking_third'
            
            sector_analysis[sector][player.team] += 1
            sector_analysis[sector]['players'].append(player.player_id)
            
            # Determine corridor
            if y < self.corridor_width:
                corridor = 'left_corridor'
            elif y < self.corridor_width * 2:
                corridor = 'center_corridor'
            else:
                corridor = 'right_corridor'
            
            sector_analysis[corridor][player.team] += 1
            sector_analysis[corridor]['players'].append(player.player_id)
        
        return sector_analysis
    
    def calculate_alignment_metrics(self, players: List[PlayerPosition]) -> Dict[str, float]:
        """Calculate team alignment and formation metrics"""
        home_players = [p for p in players if p.team == 'home']
        away_players = [p for p in players if p.team == 'away']
        
        alignment_metrics = {}
        
        for team_name, team_players in [('home', home_players), ('away', away_players)]:
            if len(team_players) < 3:
                continue
                
            # Calculate team compactness (average distance between players)
            distances = []
            for i, p1 in enumerate(team_players):
                for p2 in team_players[i+1:]:
                    distances.append(self._euclidean_distance(p1.position, p2.position))
            
            alignment_metrics[f'{team_name}_team_compactness'] = np.mean(distances) if distances else 0
            alignment_metrics[f'{team_name}_team_spread'] = np.std(distances) if distances else 0
            
            # Calculate formation width and depth
            x_positions = [p.position[0] for p in team_players]
            y_positions = [p.position[1] for p in team_players]
            
            alignment_metrics[f'{team_name}_formation_width'] = max(y_positions) - min(y_positions)
            alignment_metrics[f'{team_name}_formation_depth'] = max(x_positions) - min(x_positions)
            
            # Calculate center of mass
            alignment_metrics[f'{team_name}_center_x'] = np.mean(x_positions)
            alignment_metrics[f'{team_name}_center_y'] = np.mean(y_positions)
        
        return alignment_metrics
    
    def generate_tactical_report(self, players: List[PlayerPosition], ball_position: Tuple[float, float]) -> TacticalMetrics:
        """Generate comprehensive tactical analysis report"""
        
        # Separate defensive players (assuming defenders are in defensive third)
        defensive_players = [p for p in players if p.position[0] < self.defensive_third and p.team in ['home', 'away']]
        
        # Calculate all metrics
        pressure_levels = self.analyze_pressure_levels(players, ball_position)
        formation_analysis = self.analyze_defensive_formation(defensive_players)
        distance_metrics = self.calculate_player_distances(players)
        alignment_scores = self.calculate_alignment_metrics(players)
        sector_analysis = self.analyze_sectors_and_corridors(players)
        
        return TacticalMetrics(
            pressure_levels=pressure_levels,
            formation_analysis=formation_analysis,
            distance_metrics=distance_metrics,
            alignment_scores=alignment_scores,
            sector_analysis=sector_analysis
        )
    
    def _euclidean_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two positions"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

class VideoTacticalVisualizer:
    """Visualize tactical analysis on video frames"""
    
    def __init__(self, tactical_analyzer: TacticalAnalyzer):
        self.analyzer = tactical_analyzer
        
    def draw_tactical_overlay(self, frame: np.ndarray, players: List[PlayerPosition], 
                            ball_position: Tuple[float, float], metrics: TacticalMetrics) -> np.ndarray:
        """Draw comprehensive tactical overlay on video frame"""
        
        height, width = frame.shape[:2]
        overlay = frame.copy()
        
        # Convert field coordinates to pixel coordinates
        def field_to_pixel(field_pos):
            x_ratio = field_pos[0] / self.analyzer.field_length
            y_ratio = field_pos[1] / self.analyzer.field_width
            return (int(x_ratio * width), int(y_ratio * height))
        
        # Draw field sectors
        self._draw_field_sectors(overlay, width, height)
        
        # Draw players with enhanced information
        self._draw_enhanced_players(overlay, players, field_to_pixel)
        
        # Draw ball
        ball_pixel = field_to_pixel(ball_position)
        cv2.circle(overlay, ball_pixel, 8, (0, 255, 255), -1)
        
        # Draw pressure zones
        self._draw_pressure_zones(overlay, players, ball_position, field_to_pixel, metrics.pressure_levels)
        
        # Draw formation lines
        self._draw_formation_lines(overlay, players, field_to_pixel)
        
        # Draw distance measurements
        self._draw_distance_measurements(overlay, players, field_to_pixel, metrics.distance_metrics)
        
        # Add tactical information panel
        self._draw_tactical_info_panel(overlay, metrics)
        
        return overlay
    
    def _draw_field_sectors(self, frame: np.ndarray, width: int, height: int):
        """Draw field sectors and corridors"""
        # Draw thirds
        third_width = width // 3
        cv2.line(frame, (third_width, 0), (third_width, height), (100, 100, 100), 1)
        cv2.line(frame, (third_width * 2, 0), (third_width * 2, height), (100, 100, 100), 1)
        
        # Draw corridors
        corridor_height = height // 3
        cv2.line(frame, (0, corridor_height), (width, corridor_height), (100, 100, 100), 1)
        cv2.line(frame, (0, corridor_height * 2), (width, corridor_height * 2), (100, 100, 100), 1)
    
    def _draw_enhanced_players(self, frame: np.ndarray, players: List[PlayerPosition], field_to_pixel):
        """Draw players with team colors and numbers"""
        team_colors = {'home': (0, 255, 0), 'away': (0, 0, 255), 'referee': (255, 255, 0)}
        
        for player in players:
            pixel_pos = field_to_pixel(player.position)
            color = team_colors.get(player.team, (255, 255, 255))
            
            # Draw player circle
            cv2.circle(frame, pixel_pos, 15, color, -1)
            cv2.circle(frame, pixel_pos, 15, (0, 0, 0), 2)
            
            # Draw jersey number
            if player.jersey_number:
                text = str(player.jersey_number)
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
                text_pos = (pixel_pos[0] - text_size[0]//2, pixel_pos[1] + text_size[1]//2)
                cv2.putText(frame, text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def _draw_pressure_zones(self, frame: np.ndarray, players: List[PlayerPosition], 
                           ball_position: Tuple[float, float], field_to_pixel, pressure_metrics: Dict):
        """Draw pressure zones around the ball"""
        ball_pixel = field_to_pixel(ball_position)
        
        # Draw pressure circle around ball
        pressure_radius = int(50)  # pixels
        cv2.circle(frame, ball_pixel, pressure_radius, (255, 100, 100), 2)
        
        # Add pressure intensity text
        intensity = pressure_metrics.get('ball_pressure_intensity', 0)
        cv2.putText(frame, f"Pressure: {intensity}", 
                   (ball_pixel[0] + 20, ball_pixel[1] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def _draw_formation_lines(self, frame: np.ndarray, players: List[PlayerPosition], field_to_pixel):
        """Draw formation lines connecting players"""
        home_players = [p for p in players if p.team == 'home']
        away_players = [p for p in players if p.team == 'away']
        
        # Draw lines between nearby teammates
        for team_players, color in [(home_players, (0, 255, 0)), (away_players, (0, 0, 255))]:
            for i, p1 in enumerate(team_players):
                for p2 in team_players[i+1:]:
                    distance = self.analyzer._euclidean_distance(p1.position, p2.position)
                    if distance < 15:  # Only draw lines for nearby players
                        pos1 = field_to_pixel(p1.position)
                        pos2 = field_to_pixel(p2.position)
                        cv2.line(frame, pos1, pos2, color, 1)
    
    def _draw_distance_measurements(self, frame: np.ndarray, players: List[PlayerPosition], 
                                  field_to_pixel, distance_metrics: Dict):
        """Draw distance measurements between key players"""
        # Show distances for closest opposing players
        home_players = [p for p in players if p.team == 'home']
        away_players = [p for p in players if p.team == 'away']
        
        for home_player in home_players[:3]:  # Limit to avoid clutter
            closest_away = min(away_players, 
                             key=lambda p: self.analyzer._euclidean_distance(home_player.position, p.position),
                             default=None)
            if closest_away:
                distance = self.analyzer._euclidean_distance(home_player.position, closest_away.position)
                
                pos1 = field_to_pixel(home_player.position)
                pos2 = field_to_pixel(closest_away.position)
                
                # Draw distance line
                cv2.line(frame, pos1, pos2, (255, 255, 0), 1)
                
                # Draw distance text
                mid_point = ((pos1[0] + pos2[0]) // 2, (pos1[1] + pos2[1]) // 2)
                cv2.putText(frame, f"{distance:.1f}m", mid_point,
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    def _draw_tactical_info_panel(self, frame: np.ndarray, metrics: TacticalMetrics):
        """Draw tactical information panel"""
        height, width = frame.shape[:2]
        
        # Create semi-transparent panel
        panel_height = 150
        panel_width = 300
        panel_x = width - panel_width - 10
        panel_y = 10
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Add text information
        y_offset = panel_y + 20
        line_height = 18
        
        info_lines = [
            f"Ball Pressure: {metrics.pressure_levels.get('ball_pressure_intensity', 0)}",
            f"Home Pressure: {metrics.pressure_levels.get('home_team_pressure', 0)}",
            f"Away Pressure: {metrics.pressure_levels.get('away_team_pressure', 0)}",
            f"Def. Line Depth: {metrics.formation_analysis.get('defensive_line_depth_avg', 0):.1f}m",
            f"Def. Width: {metrics.formation_analysis.get('defensive_width', 0):.1f}m",
            f"Max Gap: {metrics.formation_analysis.get('max_gap_between_defenders', 0):.1f}m",
            f"Home Compact: {metrics.alignment_scores.get('home_team_compactness', 0):.1f}m",
            f"Away Compact: {metrics.alignment_scores.get('away_team_compactness', 0):.1f}m"
        ]
        
        for i, line in enumerate(info_lines):
            cv2.putText(frame, line, (panel_x + 10, y_offset + i * line_height),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

# Example usage for video processing
if __name__ == "__main__":
    # Example of how this would be used
    analyzer = TacticalAnalyzer()
    visualizer = VideoTacticalVisualizer(analyzer)
    
    # This would process actual video frames
    print("Tactical analyzer ready for video processing")
