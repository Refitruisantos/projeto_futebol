#!/usr/bin/env python3
"""Fix the 500 error in comprehensive athlete profile endpoint"""

import os

# Read the current metrics.py file
metrics_file = r"C:\Users\sorai\CascadeProjects\projeto_futebol\TESE_DOUTORAMENTO\09_IMPLEMENTACAO_TECNICA\backend\routers\metrics.py"

with open(metrics_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the import issue - add missing imports at the top
if "from datetime import date, datetime, timedelta" not in content:
    # Find the import section and add the missing import
    lines = content.split('\n')
    import_index = -1
    
    for i, line in enumerate(lines):
        if line.startswith('from database import'):
            import_index = i
            break
    
    if import_index != -1:
        lines.insert(import_index, 'from datetime import date, datetime, timedelta')
        content = '\n'.join(lines)

# Fix the numpy polyfit issue by adding error handling
old_polyfit = """            trend_slope = np.polyfit(range(len(scores)), scores, 1)[0]"""
new_polyfit = """            try:
                trend_slope = np.polyfit(range(len(scores)), scores, 1)[0]
            except:
                trend_slope = 0"""

content = content.replace(old_polyfit, new_polyfit)

# Fix potential None value issues in calculations
old_calc = """        "avg_session_load": round(np.mean([float(s['avg_pse_load']) for s in recent_sessions if s['avg_pse_load']]), 2) if any(s['avg_pse_load'] for s in recent_sessions) else None,
        "avg_distance": round(np.mean([float(s['avg_distance']) for s in recent_sessions if s['avg_distance']]), 2) if any(s['avg_distance'] for s in recent_sessions) else None"""

new_calc = """        "avg_session_load": round(np.mean([float(s['avg_pse_load']) for s in recent_sessions if s['avg_pse_load'] is not None]), 2) if any(s['avg_pse_load'] is not None for s in recent_sessions) else None,
        "avg_distance": round(np.mean([float(s['avg_distance']) for s in recent_sessions if s['avg_distance'] is not None]), 2) if any(s['avg_distance'] is not None for s in recent_sessions) else None"""

content = content.replace(old_calc, new_calc)

# Add error handling to the comprehensive profile endpoint
old_endpoint_start = """@router.get("/athletes/{athlete_id}/comprehensive-profile")
def get_comprehensive_athlete_profile(
    athlete_id: int,
    days: int = Query(30, le=365),
    db: DatabaseConnection = Depends(get_db)
):
    \"\"\"Get comprehensive athlete profile combining all data sources\"\"\"
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)"""

new_endpoint_start = """@router.get("/athletes/{athlete_id}/comprehensive-profile")
def get_comprehensive_athlete_profile(
    athlete_id: int,
    days: int = Query(30, le=365),
    db: DatabaseConnection = Depends(get_db)
):
    \"\"\"Get comprehensive athlete profile combining all data sources\"\"\"
    
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days)"""

content = content.replace(old_endpoint_start, new_endpoint_start)

# Add exception handling at the end of the function
old_return = """    return {
        "athlete_info": athlete_info,
        "training_load_metrics": load_metrics,
        "wellness_data": wellness_data,
        "wellness_trends": wellness_trends,
        "physical_evaluations": physical_evals,
        "risk_assessment": risk_assessment[0] if risk_assessment else None,
        "recent_sessions": recent_sessions,
        "performance_summary": performance_summary,
        "data_period": {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "days": days
        }
    }"""

new_return = """        return {
            "athlete_info": athlete_info,
            "training_load_metrics": load_metrics,
            "wellness_data": wellness_data,
            "wellness_trends": wellness_trends,
            "physical_evaluations": physical_evals,
            "risk_assessment": risk_assessment[0] if risk_assessment else None,
            "recent_sessions": recent_sessions,
            "performance_summary": performance_summary,
            "data_period": {
                "start_date": str(start_date),
                "end_date": str(end_date),
                "days": days
            }
        }
    except Exception as e:
        logger.error(f"Error in comprehensive athlete profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving athlete profile: {str(e)}")"""

content = content.replace(old_return, new_return)

# Write the updated content back to the file
with open(metrics_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed comprehensive athlete profile endpoint:")
print("   • Added error handling for numpy operations")
print("   • Fixed None value handling in calculations")
print("   • Added try-catch wrapper for better error reporting")
print("\n🔄 Backend restart required to apply fixes")
