# ProductivityFlow Deployment Guide

## 🎯 Overview

This guide covers the deployment of both the desktop applications (DMG files) and the backend service for ProductivityFlow.

## 📦 Desktop Applications (DMG Files)

### ✅ Successfully Built Applications

#### 1. Employee Tracker
- **File**: `ProductivityFlow Employee Tracker v3.1.0_3.1.0_x64.dmg`
- **Size**: 3.9 MB
- **Purpose**: Employee activity tracking and productivity monitoring
- **Features**: System monitoring, activity tracking, team collaboration

#### 2. Manager Dashboard
- **File**: `ProductivityFlow Manager Dashboard v3.1.0_3.1.0_x64.dmg`
- **Size**: 3.8 MB
- **Purpose**: Team management and analytics dashboard
- **Features**: Team overview, analytics, employee monitoring

### 📁 File Locations
```
Latest DMG Files/2025-07-24/
├── ProductivityFlow Employee Tracker v3.1.0_3.1.0_x64.dmg
└── ProductivityFlow Manager Dashboard v3.1.0_3.1.0_x64.dmg
```

### 🚀 Installation Instructions

1. **Download DMG Files**
   - Copy the DMG files to your distribution location
   - Ensure files are accessible to end users

2. **Installation Process**
   - Double-click the DMG file
   - Drag the application to the Applications folder
   - Launch the application from Applications

3. **First Run**
   - Applications will request necessary permissions
   - Grant accessibility permissions for system monitoring
   - Sign in with your account credentials

## 🔧 Backend Service

### Current Status
- **Local Status**: ✅ Working correctly
- **Cloud Status**: ⚠️ Needs attention (404 on health endpoint)
- **URL**: https://productivityflow-backend.onrender.com

### Backend Configuration

#### Environment Variables
The backend requires these environment variables (automatically generated on Render):
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT token signing key
- `ENCRYPTION_KEY`: Data encryption key
- `DATABASE_URL`: PostgreSQL connection string (Render provides)

#### Health Check
- **Endpoint**: `/health`
- **Expected Response**: `{"database":"connected","status":"healthy","timestamp":"..."}`

### 🔍 Backend Troubleshooting

#### Local Testing
```bash
cd backend
python -c "from application import application; app = application.test_client(); print(app.get('/health').data.decode())"
```

#### Cloud Deployment Issues
1. **404 Error**: Check Render deployment logs
2. **Database Connection**: Verify DATABASE_URL environment variable
3. **Environment Variables**: Ensure all required variables are set

### 🚀 Backend Deployment Steps

#### 1. Verify Local Functionality
```bash
cd backend
python test_deployment_local.py
```

#### 2. Deploy to Render
1. Push code to Git repository
2. Render will automatically detect changes
3. Monitor deployment logs in Render dashboard
4. Test health endpoint: `curl https://productivityflow-backend.onrender.com/health`

#### 3. Environment Setup
Ensure these environment variables are set in Render:
- `FLASK_ENV=production`
- `SECRET_KEY` (auto-generated)
- `JWT_SECRET_KEY` (auto-generated)
- `ENCRYPTION_KEY` (auto-generated)
- `DATABASE_URL` (provided by Render)

## 📋 Testing Checklist

### Desktop Applications
- [ ] DMG files open correctly
- [ ] Applications install without errors
- [ ] Applications launch successfully
- [ ] System permissions are requested
- [ ] Login functionality works
- [ ] Core features are accessible

### Backend Service
- [ ] Health endpoint responds (200 OK)
- [ ] Database connection established
- [ ] Authentication endpoints work
- [ ] API endpoints respond correctly
- [ ] CORS is properly configured

## 🔐 Security Considerations

### Desktop Applications
- Applications are not code-signed (development builds)
- Users may need to allow apps from unidentified developers
- System permissions required for monitoring functionality

### Backend Service
- JWT tokens for authentication
- Encrypted data storage
- CORS configured for desktop applications
- Environment variables for sensitive data

## 📞 Support Information

### Health Checks
```bash
# Backend health
curl https://productivityflow-backend.onrender.com/health

# Local backend test
cd backend && python -c "from application import application; app = application.test_client(); print(app.get('/health').data.decode())"
```

### Log Locations
- **Desktop Apps**: Console.app → User Reports
- **Backend**: Render dashboard → Logs

### Common Issues
1. **Backend 404**: Check Render deployment status
2. **Permission Denied**: Grant accessibility permissions
3. **Connection Failed**: Verify backend URL in desktop apps

## 🎉 Success Criteria

### Desktop Applications
- ✅ DMG files built successfully
- ✅ Applications install and run
- ✅ Core functionality accessible

### Backend Service
- ⚠️ Local functionality confirmed
- ⚠️ Cloud deployment needs attention
- ⚠️ Health endpoint should return 200 OK

---

**Status**: Desktop applications ready for distribution. Backend needs deployment verification. 