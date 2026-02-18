-- Find your Boavista video analysis
-- Run this query to find your specific analysis

-- 1. Find the Boavista session and its analysis
SELECT 
    s.id as session_id,
    s.data as session_date,
    s.adversario as opponent,
    va.analysis_id,
    va.status,
    va.analysis_type,
    va.created_at as upload_time,
    va.started_at,
    va.completed_at,
    CASE 
        WHEN va.processing_time_seconds IS NOT NULL 
        THEN CONCAT(ROUND(va.processing_time_seconds / 60.0, 1), ' minutes')
        WHEN va.status = 'processing' AND va.started_at IS NOT NULL
        THEN CONCAT('Running for ', ROUND(EXTRACT(EPOCH FROM (NOW() - va.started_at)) / 60.0, 1), ' minutes')
        ELSE 'Not started yet'
    END as processing_time,
    va.error_message
FROM sessoes s
JOIN video_analysis va ON s.id = va.session_id
WHERE s.adversario ILIKE '%boavista%' 
   OR s.adversario ILIKE '%boa vista%'
ORDER BY va.created_at DESC;

-- 2. If analysis is completed, show the results summary
SELECT 
    vm.analysis_id,
    vm.total_frames_analyzed,
    vm.ball_visibility_percentage,
    vm.avg_players_detected,
    vm.ball_tracking_quality,
    vm.ball_activity_level,
    vm.overall_quality_score,
    vm.possession_left_third_percentage,
    vm.possession_center_third_percentage,
    vm.possession_right_third_percentage,
    vm.video_coverage_percentage
FROM video_metrics vm
JOIN video_analysis va ON vm.analysis_id = va.analysis_id
JOIN sessoes s ON va.session_id = s.id
WHERE (s.adversario ILIKE '%boavista%' OR s.adversario ILIKE '%boa vista%')
  AND va.status = 'completed'
ORDER BY vm.created_at DESC
LIMIT 1;

-- 3. Show detection counts for your video
SELECT 
    vd.object_class,
    COUNT(*) as total_detections,
    ROUND(AVG(vd.confidence), 2) as avg_confidence,
    ROUND(MIN(vd.confidence), 2) as min_confidence,
    ROUND(MAX(vd.confidence), 2) as max_confidence
FROM video_detections vd
JOIN video_analysis va ON vd.analysis_id = va.analysis_id
JOIN sessoes s ON va.session_id = s.id
WHERE (s.adversario ILIKE '%boavista%' OR s.adversario ILIKE '%boa vista%')
  AND va.status = 'completed'
GROUP BY vd.object_class
ORDER BY total_detections DESC;
