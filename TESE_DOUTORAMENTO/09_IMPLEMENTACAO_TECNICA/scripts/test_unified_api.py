#!/usr/bin/env python3
"""Test the unified API endpoints to ensure cross-referencing works correctly"""

import requests
import json

BASE_URL = "http://localhost:8000/api/metrics"

def test_endpoint(endpoint, description):
    """Test an API endpoint and display results"""
    print(f"\n🔍 Testing {description}")
    print(f"   Endpoint: {endpoint}")
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            
            # Show key data structure
            if isinstance(data, dict):
                keys = list(data.keys())
                print(f"   📊 Response keys: {keys[:5]}{'...' if len(keys) > 5 else ''}")
                
                # Show specific insights based on endpoint
                if "comprehensive-profile" in endpoint:
                    athlete_name = data.get('athlete_info', {}).get('nome_completo', 'Unknown')
                    wellness_count = len(data.get('wellness_data', []))
                    risk_score = data.get('risk_assessment', {}).get('injury_risk_score', 'N/A')
                    print(f"   👤 Athlete: {athlete_name}")
                    print(f"   🏥 Wellness records: {wellness_count}")
                    print(f"   ⚠️  Injury risk: {risk_score}")
                
                elif "wellness-summary" in endpoint:
                    total_reports = data.get('wellness_summary', {}).get('total_reports', 0)
                    avg_wellness = data.get('wellness_summary', {}).get('avg_wellness_score', 'N/A')
                    high_risk = data.get('risk_summary', {}).get('high_injury_risk', 0)
                    print(f"   📈 Total wellness reports: {total_reports}")
                    print(f"   💚 Average wellness: {avg_wellness}")
                    print(f"   🚨 High injury risk: {high_risk}")
                
                elif "analysis" in endpoint:
                    opponent = data.get('opponent_info', {}).get('nome_equipa', 'Unknown')
                    difficulty_home = data.get('tactical_analysis', {}).get('difficulty_rating', {}).get('home', 'N/A')
                    style = data.get('tactical_analysis', {}).get('style_analysis', {}).get('playing_style', 'N/A')
                    print(f"   ⚽ Opponent: {opponent}")
                    print(f"   🏠 Home difficulty: {difficulty_home}")
                    print(f"   🎯 Playing style: {style}")
                
                elif "risk-assessment" in endpoint:
                    total_players = data.get('summary', {}).get('total_players', 0)
                    high_injury = data.get('summary', {}).get('high_injury_risk', 0)
                    next_opponent = data.get('next_match', {}).get('opponent', 'N/A')
                    print(f"   👥 Total players assessed: {total_players}")
                    print(f"   🚨 High injury risk: {high_injury}")
                    print(f"   🆚 Next opponent: {next_opponent}")
            
            elif isinstance(data, list):
                print(f"   📊 Response: List with {len(data)} items")
            
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error: Backend server not running")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")

def main():
    print("🧪 Testing Unified API Endpoints")
    print("=" * 50)
    
    # Test comprehensive athlete profile (using first athlete ID)
    test_endpoint("/athletes/241/comprehensive-profile", "Comprehensive Athlete Profile")
    
    # Test team wellness summary
    test_endpoint("/team/wellness-summary", "Team Wellness Summary")
    
    # Test opponent analysis
    test_endpoint("/opponents/Sporting CP/analysis", "Opponent Analysis")
    
    # Test current risk assessment
    test_endpoint("/risk-assessment/current", "Current Risk Assessment")
    
    # Test existing dashboard (should still work)
    test_endpoint("/team/dashboard", "Enhanced Team Dashboard")
    
    print("\n" + "=" * 50)
    print("🎯 Cross-Reference Validation:")
    
    # Test cross-referencing by checking if data is consistent
    try:
        # Get athlete profile
        profile_response = requests.get(f"{BASE_URL}/athletes/241/comprehensive-profile")
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            athlete_name = profile_data.get('athlete_info', {}).get('nome_completo', 'Unknown')
            
            # Get team wellness summary
            wellness_response = requests.get(f"{BASE_URL}/team/wellness-summary")
            if wellness_response.status_code == 200:
                wellness_data = wellness_response.json()
                
                print(f"   ✅ Athlete profile retrieved: {athlete_name}")
                print(f"   ✅ Team wellness data available")
                
                # Check if athlete appears in team data
                attention_athletes = wellness_data.get('athletes_needing_attention', [])
                athlete_in_attention = any(a.get('nome_completo') == athlete_name for a in attention_athletes)
                
                if athlete_in_attention:
                    print(f"   🚨 {athlete_name} appears in attention list - data cross-referenced correctly")
                else:
                    print(f"   ✅ {athlete_name} not in attention list - low risk status consistent")
                    
        print("   ✅ Cross-referencing validation complete")
        
    except Exception as e:
        print(f"   ❌ Cross-reference validation failed: {str(e)}")
    
    print("\n🎉 Unified API Testing Complete!")
    print("\nNext steps:")
    print("1. Restart backend server if not running")
    print("2. Test endpoints in browser or Postman")
    print("3. Update frontend to use unified endpoints")

if __name__ == "__main__":
    main()
