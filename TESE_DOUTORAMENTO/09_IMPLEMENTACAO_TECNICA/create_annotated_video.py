"""
Script to create annotated video with detection boxes for your Boavista analysis
This will overlay detection boxes on your original video
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import cv2
import numpy as np
from database import get_db
import json
from pathlib import Path

def create_annotated_video(analysis_id=None, output_path=None):
    """Create annotated video with detection overlays"""
    
    db = get_db()
    
    # If no analysis_id provided, find the latest Boavista analysis
    if not analysis_id:
        query = """
        SELECT va.analysis_id, va.video_path, s.adversario
        FROM video_analysis va
        JOIN sessoes s ON va.session_id = s.id
        WHERE (s.adversario ILIKE '%boavista%' OR s.adversario ILIKE '%boa vista%')
          AND va.status = 'completed'
        ORDER BY va.completed_at DESC
        LIMIT 1;
        """
        
        result = db.query_to_dict(query)
        if not result:
            print("❌ No completed Boavista analysis found!")
            return False
        
        analysis_id = result[0]['analysis_id']
        video_path = result[0]['video_path']
        opponent = result[0]['adversario']
        
        print(f"🎯 Found analysis: {analysis_id}")
        print(f"📹 Video: {video_path}")
        print(f"🆚 Opponent: {opponent}")
    else:
        # Get video path for specific analysis
        query = """
        SELECT va.video_path, s.adversario
        FROM video_analysis va
        JOIN sessoes s ON va.session_id = s.id
        WHERE va.analysis_id = %s
        """
        result = db.query_to_dict(query, (analysis_id,))
        if not result:
            print(f"❌ Analysis {analysis_id} not found!")
            return False
        
        video_path = result[0]['video_path']
        opponent = result[0]['adversario']
    
    # Check if video file exists
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    # Get all detections for this analysis
    detections_query = """
    SELECT 
        frame_number,
        timestamp_seconds,
        object_class,
        confidence,
        bbox_x1, bbox_y1, bbox_x2, bbox_y2,
        center_x, center_y
    FROM video_detections 
    WHERE analysis_id = %s
    ORDER BY frame_number, object_class;
    """
    
    detections = db.query_to_dict(detections_query, (analysis_id,))
    
    if not detections:
        print(f"❌ No detections found for analysis {analysis_id}")
        return False
    
    print(f"✅ Found {len(detections)} detections")
    
    # Group detections by frame
    detections_by_frame = {}
    for det in detections:
        frame_num = det['frame_number']
        if frame_num not in detections_by_frame:
            detections_by_frame[frame_num] = []
        detections_by_frame[frame_num].append(det)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Could not open video: {video_path}")
        return False
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"📊 Video Info: {width}x{height} @ {fps}fps, {total_frames} frames")
    
    # Set output path
    if not output_path:
        video_name = Path(video_path).stem
        output_path = f"uploads/processed/{video_name}_annotated_{analysis_id[:8]}.mp4"
    
    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"🎬 Creating annotated video: {output_path}")
    print("⏳ Processing frames...")
    
    # Color map for different object classes
    colors = {
        'ball': (0, 255, 0),        # Green
        'player': (255, 0, 0),      # Blue
        'goalkeeper': (0, 0, 255),  # Red
        'referee': (255, 255, 0)    # Cyan
    }
    
    frame_count = 0
    processed_frames = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Draw detections for this frame
        if frame_count in detections_by_frame:
            frame_detections = detections_by_frame[frame_count]
            
            for det in frame_detections:
                # Get bounding box coordinates
                x1, y1, x2, y2 = int(det['bbox_x1']), int(det['bbox_y1']), int(det['bbox_x2']), int(det['bbox_y2'])
                
                # Get color for this object class
                color = colors.get(det['object_class'], (128, 128, 128))
                
                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label with confidence
                label = f"{det['object_class']}: {det['confidence']:.2f}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                
                # Draw label background
                cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                             (x1 + label_size[0], y1), color, -1)
                
                # Draw label text
                cv2.putText(frame, label, (x1, y1 - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            processed_frames += 1
        
        # Add timestamp and frame info
        timestamp = frame_count / fps
        info_text = f"Frame: {frame_count} | Time: {timestamp:.1f}s | Detections: {len(detections_by_frame.get(frame_count, []))}"
        cv2.putText(frame, info_text, (10, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Write frame
        out.write(frame)
        
        frame_count += 1
        
        # Progress update
        if frame_count % (total_frames // 10) == 0:
            progress = (frame_count / total_frames) * 100
            print(f"   Progress: {progress:.1f}% ({frame_count}/{total_frames} frames)")
    
    # Cleanup
    cap.release()
    out.release()
    
    print(f"✅ Annotated video created successfully!")
    print(f"📁 Output: {output_path}")
    print(f"📊 Processed {processed_frames} frames with detections out of {total_frames} total frames")
    
    # Show summary
    show_detection_summary(detections)
    
    return output_path

def show_detection_summary(detections):
    """Show summary of detections in the video"""
    
    print(f"\n📈 DETECTION SUMMARY:")
    
    # Count by object class
    class_counts = {}
    confidence_sums = {}
    
    for det in detections:
        obj_class = det['object_class']
        if obj_class not in class_counts:
            class_counts[obj_class] = 0
            confidence_sums[obj_class] = 0
        
        class_counts[obj_class] += 1
        confidence_sums[obj_class] += det['confidence']
    
    for obj_class in sorted(class_counts.keys()):
        count = class_counts[obj_class]
        avg_conf = confidence_sums[obj_class] / count
        emoji = get_object_emoji(obj_class)
        print(f"   {emoji} {obj_class.title()}: {count} detections (avg confidence: {avg_conf:.2f})")

def get_object_emoji(object_class):
    """Get emoji for detected object class"""
    emojis = {
        'ball': '⚽',
        'player': '👤', 
        'goalkeeper': '🥅',
        'referee': '👨‍⚖️'
    }
    return emojis.get(object_class, '❓')

if __name__ == "__main__":
    print("🎬 Creating Annotated Video for Boavista Analysis")
    print("=" * 50)
    
    try:
        # You can specify analysis_id if you know it, otherwise it will find the latest Boavista analysis
        output_file = create_annotated_video()
        
        if output_file:
            print(f"\n🎉 SUCCESS! Your annotated video is ready:")
            print(f"📁 {os.path.abspath(output_file)}")
            print(f"\n💡 The video shows:")
            print(f"   ⚽ Green boxes: Ball detections")
            print(f"   👤 Blue boxes: Player detections") 
            print(f"   🥅 Red boxes: Goalkeeper detections")
            print(f"   👨‍⚖️ Cyan boxes: Referee detections")
            print(f"   📊 Frame info and timestamp at bottom")
        
    except Exception as e:
        print(f"❌ Error creating annotated video: {e}")
        import traceback
        traceback.print_exc()
