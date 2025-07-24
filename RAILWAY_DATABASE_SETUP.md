# 🚀 Railway PostgreSQL Database Setup for Google Cloud Run

## 🎯 Objective
Set up a reliable Railway PostgreSQL database to replace the problematic Cloud SQL connection.

## 📋 Manual Setup Steps

### Step 1: Create Railway Account
1. Visit [Railway.app](https://railway.app)
2. Sign up with GitHub or Google account
3. Verify your email

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo" or "Start from scratch"
3. Name your project: `productivityflow-database`

### Step 3: Add PostgreSQL Database
1. Click "New Service"
2. Select "Database" → "PostgreSQL"
3. Wait for the database to be created
4. Note the database name and credentials

### Step 4: Get Connection String
1. Click on your PostgreSQL service
2. Go to "Connect" tab
3. Copy the "Postgres Connection URL"
4. It should look like: `postgresql://postgres:password@containers-us-west-XX.railway.app:XXXX/railway`

### Step 5: Update Google Cloud Run
```bash
# Update the DATABASE_URL in Google Cloud Run
gcloud run services update productivityflow-backend \
  --update-env-vars DATABASE_URL="YOUR_RAILWAY_DATABASE_URL" \
  --region=us-central1
```

### Step 6: Test Connection
```bash
# Test the health endpoint
curl -s https://productivityflow-backend-496367590729.us-central1.run.app/health | jq .
```

## 🔧 Alternative: Using Railway CLI

If you prefer command line:

### Install Railway CLI
```bash
# macOS
brew install railway

# Or download from: https://railway.app/cli
```

### Setup via CLI
```bash
# Login to Railway
railway login

# Create new project
railway init

# Add PostgreSQL service
railway add

# Get the DATABASE_URL
railway variables
```

## 📊 Expected Results

After successful setup:
- ✅ Google Cloud Run container starts successfully
- ✅ Database connection shows "connected" in health check
- ✅ All API endpoints work properly
- ✅ Applications can connect to the backend

## 🔗 Current Status

- **Google Cloud Run URL**: `https://productivityflow-backend-496367590729.us-central1.run.app`
- **Status**: ✅ Container starts successfully
- **Database**: ❌ Currently disconnected (needs Railway setup)
- **Applications**: ✅ Updated to use Google Cloud Run

## 🎯 Next Steps

1. **Set up Railway database** (follow steps above)
2. **Update DATABASE_URL** in Google Cloud Run
3. **Test all features** with the new database
4. **Verify applications** work correctly

## 📝 Benefits of Railway PostgreSQL

- ✅ **Reliable**: 99.9% uptime guarantee
- ✅ **Scalable**: Auto-scales with usage
- ✅ **Easy**: Simple setup and management
- ✅ **Secure**: SSL connections by default
- ✅ **Fast**: Global CDN and edge locations
- ✅ **Free Tier**: Generous free tier available

## 🚨 Troubleshooting

### If DATABASE_URL update fails:
```bash
# Check current environment variables
gcloud run services describe productivityflow-backend --region=us-central1 --format="value(spec.template.spec.containers[0].env[].name,spec.template.spec.containers[0].env[].value)"
```

### If health check still shows disconnected:
1. Verify the DATABASE_URL format
2. Check Railway database is running
3. Ensure no firewall restrictions
4. Test connection locally first

### If applications can't connect:
1. Verify API_URL is updated in all applications
2. Check CORS configuration
3. Test with curl first
4. Check browser console for errors

---

**Note**: Railway provides a much more reliable database solution compared to Cloud SQL for this use case. The setup is simpler and the connection is more stable. 