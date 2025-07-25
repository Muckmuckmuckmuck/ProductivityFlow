import React, { useState, useEffect } from "react";
import { Activity, Pause, LogOut, Clock, Target, TrendingUp } from "lucide-react";

const Card = ({ children }) => <div className="bg-white border rounded-lg shadow-sm">{children}</div>;
const CardHeader = ({ children }) => <div className="p-6 border-b">{children}</div>;
const CardTitle = ({ children }) => <h3 className="text-lg font-semibold">{children}</h3>;
const CardContent = ({ children }) => <div className="p-6">{children}</div>;
const Button = ({ children, ...props }) => <button className="inline-flex items-center justify-center rounded-md px-3 py-1.5 text-sm font-medium bg-red-600 text-white hover:bg-red-700" {...props}>{children}</button>;
const Switch = ({ checked, onCheckedChange }) => (
    <button onClick={() => onCheckedChange(!checked)} className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${checked ? 'bg-green-600' : 'bg-gray-300'}`}>
        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${checked ? 'translate-x-6' : 'translate-x-1'}`} />
    </button>
);

const API_URL = "https://my-home-backend-7m6d.onrender.com";

class ActivityTracker {
    constructor(session) {
        this.session = session;
        this.intervalId = null;
        this.activityData = {
            userId: session.userId,
            teamId: session.teamId,
            startTime: null,
            endTime: null,
            totalActiveTime: 0,
            totalIdleTime: 0,
            productivityScore: 0,
            activities: [],
            currentActivity: null,
            lastActivityTime: null,
            idleThreshold: 300000, // 5 minutes in milliseconds
            isIdle: false
        };
        this.onActivityUpdate = null;
        this.onError = null;
    }

    // Track user activity and detect idle state
    trackActivity() {
        const now = Date.now();
        const timeSinceLastActivity = now - (this.activityData.lastActivityTime || now);
        
        // Detect if user is idle
        const wasIdle = this.activityData.isIdle;
        this.activityData.isIdle = timeSinceLastActivity > this.activityData.idleThreshold;
        
        // Update activity data
        if (!this.activityData.isIdle) {
            this.activityData.totalActiveTime += 10000; // 10 seconds
            this.activityData.lastActivityTime = now;
            
            // Detect current application/website
            this.detectCurrentActivity();
        } else {
            this.activityData.totalIdleTime += 10000; // 10 seconds
        }

        // Calculate productivity score
        this.calculateProductivityScore();
        
        // Call update callback
        if (this.onActivityUpdate) {
            this.onActivityUpdate(this.activityData);
        }

        // Send data to backend every 5 minutes
        if (this.activityData.totalActiveTime % 300000 === 0) {
            this.sendActivityData();
        }
    }

    // Detect current application or website
    detectCurrentActivity() {
        try {
            // For web-based tracker, we can detect current tab/window
            if (document.hidden) {
                this.activityData.currentActivity = {
                    type: 'background',
                    name: 'Background Tab',
                    category: 'system'
                };
            } else {
                // Detect current website
                const currentUrl = window.location.href;
                const domain = window.location.hostname;
                
                this.activityData.currentActivity = {
                    type: 'website',
                    name: domain,
                    url: currentUrl,
                    category: this.categorizeWebsite(domain)
                };
            }
        } catch (error) {
            console.error('Error detecting activity:', error);
            this.activityData.currentActivity = {
                type: 'unknown',
                name: 'Unknown Activity',
                category: 'unknown'
            };
        }
    }

    // Categorize websites for productivity analysis
    categorizeWebsite(domain) {
        const productivityDomains = [
            'github.com', 'stackoverflow.com', 'docs.google.com', 'notion.so',
            'figma.com', 'slack.com', 'zoom.us', 'teams.microsoft.com',
            'jira.com', 'confluence.atlassian.com', 'trello.com', 'asana.com'
        ];
        
        const socialDomains = [
            'facebook.com', 'twitter.com', 'instagram.com', 'tiktok.com',
            'youtube.com', 'reddit.com', 'linkedin.com'
        ];
        
        const entertainmentDomains = [
            'netflix.com', 'spotify.com', 'twitch.tv', 'discord.com',
            'pinterest.com', 'imgur.com'
        ];

        if (productivityDomains.some(d => domain.includes(d))) {
            return 'productivity';
        } else if (socialDomains.some(d => domain.includes(d))) {
            return 'social';
        } else if (entertainmentDomains.some(d => domain.includes(d))) {
            return 'entertainment';
        } else {
            return 'other';
        }
    }

    // Calculate productivity score based on activity
    calculateProductivityScore() {
        const totalTime = this.activityData.totalActiveTime + this.activityData.totalIdleTime;
        if (totalTime === 0) return 0;

        const activeRatio = this.activityData.totalActiveTime / totalTime;
        const currentActivity = this.activityData.currentActivity;
        
        let categoryMultiplier = 1.0;
        if (currentActivity) {
            switch (currentActivity.category) {
                case 'productivity':
                    categoryMultiplier = 1.2;
                    break;
                case 'social':
                    categoryMultiplier = 0.7;
                    break;
                case 'entertainment':
                    categoryMultiplier = 0.5;
                    break;
                default:
                    categoryMultiplier = 1.0;
            }
        }

        this.activityData.productivityScore = Math.round(activeRatio * 100 * categoryMultiplier);
        this.activityData.productivityScore = Math.min(100, Math.max(0, this.activityData.productivityScore));
    }

    // Send activity data to backend
    async sendActivityData() {
        try {
            const payload = {
                user_id: this.activityData.userId,
                team_id: this.activityData.teamId,
                start_time: this.activityData.startTime,
                end_time: new Date().toISOString(),
                total_active_time: this.activityData.totalActiveTime,
                total_idle_time: this.activityData.totalIdleTime,
                productivity_score: this.activityData.productivityScore,
                current_activity: this.activityData.currentActivity,
                activities: this.activityData.activities.slice(-10) // Last 10 activities
            };

            const response = await fetch(`${API_URL}/api/activity/track`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('Activity data sent successfully:', result);
            
        } catch (error) {
            console.error('Failed to send activity data:', error);
            if (this.onError) {
                this.onError(error);
            }
        }
    }

    start() {
        console.log("▶️ Real Activity Tracking STARTED for user:", this.session.userId);
        
        this.activityData.startTime = new Date().toISOString();
        this.activityData.lastActivityTime = Date.now();
        
        // Start tracking every 10 seconds
        this.intervalId = setInterval(() => {
            this.trackActivity();
        }, 10000);
        
        // Add event listeners for user activity
        this.addActivityListeners();
    }

    stop() {
        console.log("⏹️ Activity Tracking STOPPED for user:", this.session.userId);
        
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        
        this.activityData.endTime = new Date().toISOString();
        
        // Remove event listeners
        this.removeActivityListeners();
        
        // Send final activity data
        this.sendActivityData();
    }

    addActivityListeners() {
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        this.activityListeners = events.map(event => {
            const listener = () => {
                this.activityData.lastActivityTime = Date.now();
                this.activityData.isIdle = false;
            };
            document.addEventListener(event, listener, true);
            return { event, listener };
        });
    }

    removeActivityListeners() {
        if (this.activityListeners) {
            this.activityListeners.forEach(({ event, listener }) => {
                document.removeEventListener(event, listener, true);
            });
            this.activityListeners = null;
        }
    }

    // Get current activity summary
    getActivitySummary() {
        const totalTime = this.activityData.totalActiveTime + this.activityData.totalIdleTime;
        const activeHours = Math.round((this.activityData.totalActiveTime / 3600000) * 10) / 10;
        const idleHours = Math.round((this.activityData.totalIdleTime / 3600000) * 10) / 10;
        
        return {
            activeTime: activeHours,
            idleTime: idleHours,
            productivityScore: this.activityData.productivityScore,
            currentActivity: this.activityData.currentActivity,
            isIdle: this.activityData.isIdle
        };
    }
}

export function MainTrackingView({ session, onLogout }) {
    const [isTracking, setIsTracking] = useState(false);
    const [tracker, setTracker] = useState(null);
    const [activitySummary, setActivitySummary] = useState(null);
    const [error, setError] = useState(null);

    const handleTrackingToggle = (checked) => {
        setError(null);
        setIsTracking(checked);
        
        if (checked) {
            const newTracker = new ActivityTracker(session);
            
            // Set up callbacks
            newTracker.onActivityUpdate = (data) => {
                setActivitySummary(newTracker.getActivitySummary());
            };
            
            newTracker.onError = (error) => {
                setError(`Tracking error: ${error.message}`);
            };
            
            newTracker.start();
            setTracker(newTracker);
        } else {
            if (tracker) {
                tracker.stop();
                setTracker(null);
                setActivitySummary(null);
            }
        }
    };

    useEffect(() => {
        return () => {
            if (tracker) tracker.stop();
        };
    }, [tracker]);

    const formatTime = (hours) => {
        if (hours < 1) {
            const minutes = Math.round(hours * 60);
            return `${minutes}m`;
        }
        return `${hours}h`;
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                    <Activity className="h-5 w-5 text-green-600" />
                    <span>Productivity Tracker</span>
                </CardTitle>
                <p className="text-sm text-gray-500">Team: {session.teamName}</p>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Tracking Toggle */}
                <div className="flex items-center space-x-3 justify-center bg-gray-100 p-4 rounded-lg">
                    <Switch checked={isTracking} onCheckedChange={handleTrackingToggle} />
                    <label className="text-lg font-medium">
                        {isTracking ? "Tracking ON" : "Tracking OFF"}
                    </label>
                </div>

                {/* Error Display */}
                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                        <p className="text-red-800 text-sm">{error}</p>
                    </div>
                )}

                {/* Activity Summary */}
                {isTracking && activitySummary && (
                    <div className="space-y-3">
                        <h4 className="font-medium text-gray-900">Today's Activity</h4>
                        
                        <div className="grid grid-cols-2 gap-3">
                            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                <div className="flex items-center space-x-2">
                                    <Clock className="h-4 w-4 text-green-600" />
                                    <span className="text-sm font-medium text-green-800">Active Time</span>
                                </div>
                                <p className="text-lg font-bold text-green-900">
                                    {formatTime(activitySummary.activeTime)}
                                </p>
                            </div>
                            
                            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                                <div className="flex items-center space-x-2">
                                    <Pause className="h-4 w-4 text-yellow-600" />
                                    <span className="text-sm font-medium text-yellow-800">Idle Time</span>
                                </div>
                                <p className="text-lg font-bold text-yellow-900">
                                    {formatTime(activitySummary.idleTime)}
                                </p>
                            </div>
                        </div>

                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                            <div className="flex items-center space-x-2">
                                <TrendingUp className="h-4 w-4 text-blue-600" />
                                <span className="text-sm font-medium text-blue-800">Productivity Score</span>
                            </div>
                            <div className="flex items-center space-x-2 mt-1">
                                <div className="flex-1 bg-blue-200 rounded-full h-2">
                                    <div 
                                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                        style={{ width: `${activitySummary.productivityScore}%` }}
                                    ></div>
                                </div>
                                <span className="text-lg font-bold text-blue-900">
                                    {activitySummary.productivityScore}%
                                </span>
                            </div>
                        </div>

                        {activitySummary.currentActivity && (
                            <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                                <div className="flex items-center space-x-2">
                                    <Target className="h-4 w-4 text-gray-600" />
                                    <span className="text-sm font-medium text-gray-800">Current Activity</span>
                                </div>
                                <p className="text-sm text-gray-600 mt-1">
                                    {activitySummary.currentActivity.name}
                                    {activitySummary.isIdle && (
                                        <span className="text-yellow-600 ml-2">(Idle)</span>
                                    )}
                                </p>
                            </div>
                        )}
                    </div>
                )}

                {/* Logout Button */}
                <Button onClick={onLogout} className="w-full">
                    <LogOut className="h-4 w-4 mr-2" />
                    Log Out
                </Button>
            </CardContent>
        </Card>
    );
}