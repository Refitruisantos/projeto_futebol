-- SQL Queries to View Computer Vision Analysis Results

-- 1. View all video analyses with basic info
SELECT 
    va.analysis_id,
    va.session_id,
    s.data as session_date,
    s.tipo as session_type,
    va.analysis_type,
    va.status,
    va.created_at,
    va.completed_at,
    va.processing_time_seconds,
    CASE 
        WHEN va.processing_time_seconds IS NOT NULL 
        THEN ROUND(va.processing_time_seconds / 60.0, 2) 
        ELSE NULL 
    END as processing_time_minutes
FROM video_analysis va
LEFT JOIN sessoes s ON va.session_id = s.id
ORDER BY va.created_at DESC;

-- 2. View completed analyses with metrics summary
SELECT 
    va.analysis_id,
    s.data as session_date,
    s.adversario as opponent,
    vm.ball_visibility_percentage,
    vm.avg_players_detected,
    vm.ball_activity_level,
    vm.overall_quality_score,
    vm.possession_center_third_percentage,
    va.processing_time_seconds
FROM video_analysis va
JOIN sessoes s ON va.session_id = s.id
LEFT JOIN video_metrics vm ON va.analysis_id = vm.analysis_id
WHERE va.status = 'completed'
ORDER BY va.completed_at DESC;

-- 3. View detailed metrics for a specific analysis
-- Replace 'your-analysis-id' with actual analysis ID
SELECT 
    vm.*,
    va.analysis_type,
    va.confidence_threshold,
    va.sample_rate
FROM video_metrics vm
JOIN video_analysis va ON vm.analysis_id = va.analysis_id
WHERE va.analysis_id = 'your-analysis-id';

-- 4. View detection counts by object type for an analysis
-- Replace 'your-analysis-id' with actual analysis ID
SELECT 
    object_class,
    COUNT(*) as detection_count,
    AVG(confidence) as avg_confidence,
    MIN(confidence) as min_confidence,
    MAX(confidence) as max_confidence
FROM video_detections 
WHERE analysis_id = 'your-analysis-id'
GROUP BY object_class
ORDER BY detection_count DESC;

-- 5. View ball detections over time (for possession analysis)
-- Replace 'your-analysis-id' with actual analysis ID
SELECT 
    FLOOR(timestamp_seconds / 60) as minute,
    COUNT(*) as ball_detections,
    AVG(center_x) as avg_x_position,
    AVG(center_y) as avg_y_position
FROM video_detections 
WHERE analysis_id = 'your-analysis-id' 
AND object_class = 'ball'
GROUP BY FLOOR(timestamp_seconds / 60)
ORDER BY minute;

-- 6. View session summary with CV data
SELECT 
    s.id as session_id,
    s.data as session_date,
    s.tipo as session_type,
    s.adversario as opponent,
    COUNT(va.id) as total_analyses,
    COUNT(CASE WHEN va.status = 'completed' THEN 1 END) as completed_analyses,
    MAX(vm.ball_visibility_percentage) as best_ball_visibility,
    AVG(vm.avg_players_detected) as avg_players_detected
FROM sessoes s
LEFT JOIN video_analysis va ON s.id = va.session_id
LEFT JOIN video_metrics vm ON va.analysis_id = vm.analysis_id
GROUP BY s.id, s.data, s.tipo, s.adversario
HAVING COUNT(va.id) > 0
ORDER BY s.data DESC;

-- 7. View analysis results in JSON format (full details)
SELECT 
    analysis_id,
    session_id,
    status,
    results::json as analysis_results
FROM video_analysis 
WHERE status = 'completed' 
AND results IS NOT NULL
ORDER BY completed_at DESC;

-- 8. Check for failed analyses with error messages
SELECT 
    analysis_id,
    session_id,
    status,
    error_message,
    created_at,
    processing_time_seconds
FROM video_analysis 
WHERE status = 'failed'
ORDER BY created_at DESC;
