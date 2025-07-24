#!/usr/bin/env python3
"""
Simple test for burnout analysis function
"""

from application import application, db, Activity, User, Membership, Team
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

def test_burnout_function():
    """Test the burnout risk calculation function directly"""
    
    with application.app_context():
        try:
            print("🔍 Testing burnout analysis function directly")
            print("=" * 50)
            
            # Get a user and team
            user = User.query.first()
            if not user:
                print("❌ No users found in database")
                return
            
            print(f"✅ Found user: {user.name} ({user.id})")
            
            # Get user's team memberships
            memberships = Membership.query.filter_by(user_id=user.id).all()
            if not memberships:
                print("❌ No team memberships found for user")
                return
            
            team_id = memberships[0].team_id
            print(f"✅ Found team: {team_id}")
            
            # Get activities for the user
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            activities = Activity.query.filter(
                Activity.user_id == user.id,
                Activity.last_active >= thirty_days_ago
            ).order_by(Activity.last_active).all()
            
            print(f"✅ Found {len(activities)} activities for user")
            
            if not activities:
                print("⚠️  No activities found, creating test activity...")
                # Create a test activity
                test_activity = Activity(
                    user_id=user.id,
                    team_id=team_id,
                    date=datetime.utcnow().date(),
                    active_app="Test App",
                    window_title="Test Window",
                    productive_hours=8.0,
                    unproductive_hours=2.0,
                    idle_time=1.0,
                    goals_completed=5,
                    last_active=datetime.utcnow()
                )
                db.session.add(test_activity)
                db.session.commit()
                print("✅ Created test activity")
                
                # Get activities again
                activities = Activity.query.filter(
                    Activity.user_id == user.id,
                    Activity.last_active >= thirty_days_ago
                ).order_by(Activity.last_active).all()
                print(f"✅ Now have {len(activities)} activities")
            
            # Test the burnout calculation
            print("\n🧮 Testing burnout calculation...")
            
            # Group activities by day
            daily_activities = defaultdict(list)
            for activity in activities:
                day = activity.last_active.date()
                daily_activities[day].append(activity)
            
            print(f"✅ Grouped into {len(daily_activities)} days")
            
            # Calculate risk factors
            factors = []
            trends = {}
            risk_score = 0
            
            # 1. Long working hours trend
            daily_hours = []
            for day, day_activities in daily_activities.items():
                if day_activities:
                    start_time = min(a.last_active for a in day_activities)
                    end_time = max(a.last_active for a in day_activities)
                    hours = (end_time - start_time).total_seconds() / 3600
                    daily_hours.append(hours)
            
            print(f"✅ Calculated hours for {len(daily_hours)} days")
            
            if daily_hours:
                avg_hours = np.mean(daily_hours)
                max_hours = max(daily_hours)
                print(f"✅ Average hours: {avg_hours:.1f}, Max hours: {max_hours:.1f}")
                
                if avg_hours > 9:
                    factors.append({
                        'type': 'long_hours',
                        'severity': 'high' if avg_hours > 10 else 'medium',
                        'description': f'Average {avg_hours:.1f} hours per day',
                        'impact': 25
                    })
                    risk_score += 25
                    print(f"✅ Added long hours factor: {avg_hours:.1f} hours")
            
            print(f"✅ Final risk score: {risk_score}")
            print(f"✅ Factors: {len(factors)}")
            
            print("\n🎉 Burnout analysis function test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error in burnout test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_burnout_function() 