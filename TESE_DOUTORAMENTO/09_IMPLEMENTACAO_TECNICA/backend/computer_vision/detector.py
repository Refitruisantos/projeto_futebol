"""
Football Computer Vision Detection Module
Based on YOLOv8 for player, ball, goalkeeper, and referee detection
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class FootballDetector:
    """
    Football object detection using YOLOv8
    Detects players, ball, goalkeeper, and referee
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the football detector
        
        Args:
            model_path: Path to trained YOLOv8 model. If None, uses default YOLOv8x
        """
        self.model_path = model_path or "yolov8x.pt"
        self.model = None
        self.class_names = {
            0: "ball",
            1: "goalkeeper", 
            2: "player",
            3: "referee"
        }
        self.load_model()
        
    def load_model(self):
        """Load the YOLOv8 model"""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Loaded YOLOv8 model from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def detect_objects(self, image: np.ndarray, confidence: float = 0.5) -> List[Dict]:
        """
        Detect objects in a single frame
        
        Args:
            image: Input image as numpy array
            confidence: Minimum confidence threshold
            
        Returns:
            List of detected objects with bounding boxes and metadata
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
            
        results = self.model(image, conf=confidence)
        detections = []
        
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Extract bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence_score = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    detection = {
                        'bbox': [float(x1), float(y1), float(x2), float(y2)],
                        'confidence': float(confidence_score),
                        'class_id': class_id,
                        'class_name': self.class_names.get(class_id, 'unknown'),
                        'center': [float((x1 + x2) / 2), float((y1 + y2) / 2)],
                        'area': float((x2 - x1) * (y2 - y1))
                    }
                    detections.append(detection)
        
        return detections
    
    def process_video(self, video_path: str, output_path: Optional[str] = None, 
                     sample_rate: int = 1, confidence: float = 0.5,
                     progress_callback: Optional[callable] = None) -> Dict:
        """
        Process entire video and extract detections
        
        Args:
            video_path: Path to input video
            output_path: Path to save annotated video (optional)
            sample_rate: Process every Nth frame (1 = every frame)
            
        Returns:
            Dictionary with frame-by-frame detections and summary statistics
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Setup video writer if output path provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_detections = {}
        frame_count = 0
        processed_frames = 0
        total_frames_to_process = max(1, total_frames // sample_rate)
        
        logger.info(f"Processing video: {total_frames} frames at {fps} FPS (processing ~{total_frames_to_process} frames)")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Process every sample_rate frames
            if frame_count % sample_rate == 0:
                detections = self.detect_objects(frame, confidence=confidence)
                frame_detections[frame_count] = {
                    'timestamp': frame_count / fps,
                    'detections': detections
                }
                
                # Draw annotations if saving output video
                if writer:
                    annotated_frame = self.draw_detections(frame, detections)
                    writer.write(annotated_frame)
                elif output_path:
                    writer.write(frame)
                    
                processed_frames += 1
                
                # Report progress every 10 frames
                if progress_callback and processed_frames % 10 == 0:
                    percentage = min(99.0, (processed_frames / total_frames_to_process) * 100)
                    progress_callback(processed_frames, total_frames_to_process, percentage)
                
                if processed_frames % 100 == 0:
                    logger.info(f"Processed {processed_frames}/{total_frames_to_process} frames ({processed_frames/total_frames_to_process*100:.1f}%)")
            
            frame_count += 1
        
        cap.release()
        if writer:
            writer.release()
        
        # Calculate summary statistics
        summary = self.calculate_video_summary(frame_detections, fps, total_frames)
        
        return {
            'video_info': {
                'path': video_path,
                'fps': fps,
                'total_frames': total_frames,
                'duration_seconds': total_frames / fps,
                'resolution': [width, height],
                'processed_frames': processed_frames
            },
            'frame_detections': frame_detections,
            'summary': summary
        }
    
    def draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on image
        
        Args:
            image: Input image
            detections: List of detections from detect_objects
            
        Returns:
            Annotated image
        """
        annotated = image.copy()
        
        # Color map for different classes
        colors = {
            'ball': (0, 255, 0),      # Green
            'player': (255, 0, 0),    # Blue  
            'goalkeeper': (0, 0, 255), # Red
            'referee': (255, 255, 0)   # Cyan
        }
        
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            class_name = detection['class_name']
            confidence = detection['confidence']
            
            color = colors.get(class_name, (128, 128, 128))
            
            # Draw bounding box
            cv2.rectangle(annotated, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(annotated, (int(x1), int(y1) - label_size[1] - 10), 
                         (int(x1) + label_size[0], int(y1)), color, -1)
            cv2.putText(annotated, label, (int(x1), int(y1) - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return annotated
    
    def calculate_video_summary(self, frame_detections: Dict, fps: int, total_frames: int) -> Dict:
        """
        Calculate summary statistics from video detections
        
        Args:
            frame_detections: Frame-by-frame detection results
            fps: Video frame rate
            total_frames: Total number of frames
            
        Returns:
            Summary statistics dictionary
        """
        if not frame_detections:
            return {}
        
        # Count detections by class
        class_counts = {name: 0 for name in self.class_names.values()}
        ball_positions = []
        player_positions = []
        
        for frame_data in frame_detections.values():
            for detection in frame_data['detections']:
                class_name = detection['class_name']
                class_counts[class_name] += 1
                
                if class_name == 'ball':
                    ball_positions.append(detection['center'])
                elif class_name == 'player':
                    player_positions.append(detection['center'])
        
        # Calculate ball possession zones (simplified)
        ball_possession_stats = self.calculate_ball_possession(ball_positions, player_positions)
        
        # Calculate average players per frame
        total_detections = sum(len(frame_data['detections']) for frame_data in frame_detections.values())
        avg_detections_per_frame = total_detections / len(frame_detections) if frame_detections else 0
        
        return {
            'detection_counts': class_counts,
            'total_detections': total_detections,
            'avg_detections_per_frame': avg_detections_per_frame,
            'ball_possession_stats': ball_possession_stats,
            'video_coverage': len(frame_detections) / total_frames * 100,
            'processed_duration': len(frame_detections) / fps
        }
    
    def calculate_ball_possession(self, ball_positions: List, player_positions: List) -> Dict:
        """
        Calculate basic ball possession statistics
        
        Args:
            ball_positions: List of ball center coordinates
            player_positions: List of player center coordinates
            
        Returns:
            Ball possession statistics
        """
        if not ball_positions:
            return {'ball_detected_frames': 0, 'possession_zones': {}}
        
        # Divide field into zones (simplified)
        zones = {
            'left_third': 0,
            'center_third': 0, 
            'right_third': 0
        }
        
        for pos in ball_positions:
            x, y = pos
            # Assuming standard field orientation
            if x < 640/3:  # Left third
                zones['left_third'] += 1
            elif x < 2*640/3:  # Center third  
                zones['center_third'] += 1
            else:  # Right third
                zones['right_third'] += 1
        
        total_ball_frames = len(ball_positions)
        possession_percentages = {
            zone: (count / total_ball_frames * 100) if total_ball_frames > 0 else 0
            for zone, count in zones.items()
        }
        
        return {
            'ball_detected_frames': total_ball_frames,
            'possession_zones': zones,
            'possession_percentages': possession_percentages
        }


class FootballMetricsCalculator:
    """
    Calculate advanced football metrics from detection data
    """
    
    def __init__(self):
        self.field_dimensions = {
            'length': 105,  # meters
            'width': 68     # meters
        }
    
    def calculate_session_metrics(self, detection_results: Dict) -> Dict:
        """
        Calculate comprehensive metrics from video analysis
        
        Args:
            detection_results: Results from FootballDetector.process_video()
            
        Returns:
            Dictionary of calculated metrics
        """
        frame_detections = detection_results.get('frame_detections', {})
        video_info = detection_results.get('video_info', {})
        
        if not frame_detections:
            return {}
        
        metrics = {
            'basic_stats': self._calculate_basic_stats(frame_detections),
            'ball_metrics': self._calculate_ball_metrics(frame_detections),
            'player_metrics': self._calculate_player_metrics(frame_detections),
            'tactical_metrics': self._calculate_tactical_metrics(frame_detections),
            'video_quality': self._assess_video_quality(detection_results)
        }
        
        return metrics
    
    def _calculate_basic_stats(self, frame_detections: Dict) -> Dict:
        """Calculate basic detection statistics"""
        total_frames = len(frame_detections)
        
        class_frame_counts = {'ball': 0, 'player': 0, 'goalkeeper': 0, 'referee': 0}
        
        for frame_data in frame_detections.values():
            frame_classes = set()
            for detection in frame_data['detections']:
                frame_classes.add(detection['class_name'])
            
            for class_name in frame_classes:
                class_frame_counts[class_name] += 1
        
        return {
            'total_analyzed_frames': total_frames,
            'ball_visibility_percentage': (class_frame_counts['ball'] / total_frames * 100) if total_frames > 0 else 0,
            'avg_players_detected': sum(len([d for d in frame_data['detections'] if d['class_name'] == 'player']) 
                                      for frame_data in frame_detections.values()) / total_frames if total_frames > 0 else 0,
            'goalkeeper_visibility_percentage': (class_frame_counts['goalkeeper'] / total_frames * 100) if total_frames > 0 else 0
        }
    
    def _calculate_ball_metrics(self, frame_detections: Dict) -> Dict:
        """Calculate ball-related metrics"""
        ball_detections = []
        
        for frame_data in frame_detections.values():
            for detection in frame_data['detections']:
                if detection['class_name'] == 'ball':
                    ball_detections.append({
                        'timestamp': frame_data['timestamp'],
                        'position': detection['center'],
                        'confidence': detection['confidence']
                    })
        
        if not ball_detections:
            return {'ball_tracking_quality': 'No ball detected'}
        
        # Calculate ball movement patterns
        distances = []
        for i in range(1, len(ball_detections)):
            prev_pos = ball_detections[i-1]['position']
            curr_pos = ball_detections[i]['position']
            distance = np.sqrt((curr_pos[0] - prev_pos[0])**2 + (curr_pos[1] - prev_pos[1])**2)
            distances.append(distance)
        
        return {
            'ball_tracking_quality': 'Good' if len(ball_detections) > len(frame_detections) * 0.3 else 'Poor',
            'total_ball_detections': len(ball_detections),
            'avg_ball_movement_per_frame': np.mean(distances) if distances else 0,
            'max_ball_movement': np.max(distances) if distances else 0,
            'ball_activity_level': 'High' if np.mean(distances) > 50 else 'Low' if distances else 'Unknown'
        }
    
    def _calculate_player_metrics(self, frame_detections: Dict) -> Dict:
        """Calculate player-related metrics"""
        player_counts_per_frame = []
        
        for frame_data in frame_detections.values():
            player_count = len([d for d in frame_data['detections'] if d['class_name'] == 'player'])
            player_counts_per_frame.append(player_count)
        
        if not player_counts_per_frame:
            return {}
        
        return {
            'avg_players_visible': np.mean(player_counts_per_frame),
            'max_players_detected': np.max(player_counts_per_frame),
            'min_players_detected': np.min(player_counts_per_frame),
            'player_detection_consistency': np.std(player_counts_per_frame),
            'estimated_team_size': 'Full teams' if np.mean(player_counts_per_frame) > 15 else 'Partial view'
        }
    
    def _calculate_tactical_metrics(self, frame_detections: Dict) -> Dict:
        """Calculate tactical and positional metrics"""
        # This is a simplified version - in practice, you'd need more sophisticated analysis
        return {
            'analysis_type': 'Basic computer vision analysis',
            'recommended_improvements': [
                'Add player tracking for individual movement analysis',
                'Implement team classification for possession analysis', 
                'Add formation detection algorithms',
                'Include heat map generation for positional analysis'
            ]
        }
    
    def _assess_video_quality(self, detection_results: Dict) -> Dict:
        """Assess the quality of video analysis"""
        summary = detection_results.get('summary', {})
        video_info = detection_results.get('video_info', {})
        
        coverage = summary.get('video_coverage', 0)
        avg_detections = summary.get('avg_detections_per_frame', 0)
        
        quality_score = 'Excellent' if coverage > 90 and avg_detections > 5 else \
                       'Good' if coverage > 70 and avg_detections > 3 else \
                       'Fair' if coverage > 50 else 'Poor'
        
        return {
            'overall_quality': quality_score,
            'video_coverage_percentage': coverage,
            'avg_detections_per_frame': avg_detections,
            'resolution': video_info.get('resolution', [0, 0]),
            'fps': video_info.get('fps', 0),
            'recommendations': self._get_quality_recommendations(quality_score)
        }
    
    def _get_quality_recommendations(self, quality_score: str) -> List[str]:
        """Get recommendations based on video quality"""
        if quality_score == 'Poor':
            return [
                'Consider using higher resolution video',
                'Ensure better lighting conditions',
                'Use a more stable camera position',
                'Check if the field is fully visible in the frame'
            ]
        elif quality_score == 'Fair':
            return [
                'Try to capture more of the playing field',
                'Improve camera stability',
                'Consider multiple camera angles'
            ]
        else:
            return ['Video quality is sufficient for analysis']
