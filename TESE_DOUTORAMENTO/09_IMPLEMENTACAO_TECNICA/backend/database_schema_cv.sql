-- Database schema for Computer Vision module
-- Add this to your existing database

-- Table to store video analysis records
CREATE TABLE IF NOT EXISTS video_analysis (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(36) UNIQUE NOT NULL,
    session_id INTEGER REFERENCES sessoes(id) ON DELETE CASCADE,
    video_path TEXT NOT NULL,
    analysis_type VARCHAR(50) DEFAULT 'full',
    confidence_threshold FLOAT DEFAULT 0.5,
    sample_rate INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'queued', -- queued, processing, completed, failed
    results JSONB,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    processing_time_seconds FLOAT,
    
    -- Indexes for better performance
    INDEX idx_video_analysis_session_id (session_id),
    INDEX idx_video_analysis_status (status),
    INDEX idx_video_analysis_created_at (created_at)
);

-- Table to store detected objects from video frames
CREATE TABLE IF NOT EXISTS video_detections (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(36) REFERENCES video_analysis(analysis_id) ON DELETE CASCADE,
    frame_number INTEGER NOT NULL,
    timestamp_seconds FLOAT NOT NULL,
    object_class VARCHAR(20) NOT NULL, -- ball, player, goalkeeper, referee
    confidence FLOAT NOT NULL,
    bbox_x1 FLOAT NOT NULL,
    bbox_y1 FLOAT NOT NULL,
    bbox_x2 FLOAT NOT NULL,
    bbox_y2 FLOAT NOT NULL,
    center_x FLOAT NOT NULL,
    center_y FLOAT NOT NULL,
    area FLOAT NOT NULL,
    
    -- Indexes for efficient querying
    INDEX idx_detections_analysis_id (analysis_id),
    INDEX idx_detections_frame (frame_number),
    INDEX idx_detections_class (object_class),
    INDEX idx_detections_timestamp (timestamp_seconds)
);

-- Table to store calculated metrics from video analysis
CREATE TABLE IF NOT EXISTS video_metrics (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(36) REFERENCES video_analysis(analysis_id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES sessoes(id) ON DELETE CASCADE,
    
    -- Basic detection stats
    total_frames_analyzed INTEGER,
    ball_visibility_percentage FLOAT,
    avg_players_detected FLOAT,
    goalkeeper_visibility_percentage FLOAT,
    
    -- Ball metrics
    ball_tracking_quality VARCHAR(20),
    total_ball_detections INTEGER,
    avg_ball_movement_per_frame FLOAT,
    max_ball_movement FLOAT,
    ball_activity_level VARCHAR(20),
    
    -- Player metrics
    avg_players_visible FLOAT,
    max_players_detected INTEGER,
    min_players_detected INTEGER,
    player_detection_consistency FLOAT,
    
    -- Possession metrics (simplified)
    possession_left_third_percentage FLOAT,
    possession_center_third_percentage FLOAT,
    possession_right_third_percentage FLOAT,
    
    -- Video quality assessment
    overall_quality_score VARCHAR(20),
    video_coverage_percentage FLOAT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_video_metrics_session_id (session_id),
    INDEX idx_video_metrics_analysis_id (analysis_id)
);

-- View to combine session data with computer vision metrics
CREATE OR REPLACE VIEW session_with_cv_metrics AS
SELECT 
    s.*,
    va.analysis_id,
    va.status as cv_status,
    va.created_at as cv_analysis_date,
    va.processing_time_seconds,
    vm.ball_visibility_percentage,
    vm.avg_players_detected,
    vm.ball_activity_level,
    vm.overall_quality_score,
    vm.possession_center_third_percentage
FROM sessoes s
LEFT JOIN video_analysis va ON s.id = va.session_id AND va.status = 'completed'
LEFT JOIN video_metrics vm ON va.analysis_id = vm.analysis_id;

-- Function to get session computer vision summary
CREATE OR REPLACE FUNCTION get_session_cv_summary(session_id_param INTEGER)
RETURNS TABLE (
    session_id INTEGER,
    total_analyses BIGINT,
    completed_analyses BIGINT,
    latest_analysis_date TIMESTAMP,
    best_ball_visibility FLOAT,
    avg_players_detected FLOAT,
    overall_quality VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        session_id_param,
        COUNT(va.id) as total_analyses,
        COUNT(CASE WHEN va.status = 'completed' THEN 1 END) as completed_analyses,
        MAX(va.completed_at) as latest_analysis_date,
        MAX(vm.ball_visibility_percentage) as best_ball_visibility,
        AVG(vm.avg_players_detected) as avg_players_detected,
        (ARRAY_AGG(vm.overall_quality_score ORDER BY va.completed_at DESC))[1] as overall_quality
    FROM video_analysis va
    LEFT JOIN video_metrics vm ON va.analysis_id = vm.analysis_id
    WHERE va.session_id = session_id_param;
END;
$$ LANGUAGE plpgsql;
