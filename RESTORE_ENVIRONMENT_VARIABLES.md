# 🔧 **Restore Environment Variables for ProductivityFlow Backend**

## 🎯 **Current Situation**
Your Railway deployment `productivityflow-backend-00007-ktn` has only 3 environment variables, but it needs 14 for full functionality. Let's restore all the missing ones.

---

## 📋 **Complete Environment Variables List**

### **Step 1: Go to Railway Dashboard**
1. Visit: https://railway.app/dashboard
2. Click on your project: `productivityflow-backend-00007-ktn`
3. Click on your web service
4. Go to the **"Variables"** tab

### **Step 2: Add These Environment Variables**

#### **🔐 Essential (Required) - Add These First**
```bash
# Database (Auto-configured by Railway)
DATABASE_URL=postgresql://...  # Railway should provide this automatically

# Security Keys (Generate these)
SECRET_KEY=XobdcXDmjtFK2IvJ&oRM^ldxH8GSMpzO
JWT_SECRET_KEY=R6Sslj1bP7zr7c1WD-6YgE5J6NjNzxBOmJbYtZrfHQIVMi3sA6lRWgTO7NGE01CvFUuYLncxwvuk0c2HJKbF8w
ENCRYPTION_KEY=o3B2vTvUugVaJxjym70g7TlTt_T076QPHrvjctwVV9s=

# Production Settings
FLASK_ENV=production
ENABLE_RATE_LIMITING=true
```

#### **📧 Email Configuration (Your Gmail Setup)**
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=infoproductivityflows@gmail.com
MAIL_PASSWORD=vyeibhluijxd
MAIL_DEFAULT_SENDER=infoproductivityflows@gmail.com
```

#### **💳 Payment Processing (Stripe)**
```bash
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
```

#### **🤖 AI Integration (Claude)**
```bash
CLAUDE_API_KEY=sk-ant-...
```

#### **⚡ Optional (Redis)**
```bash
REDIS_URL=redis://...
```

---

## 🔧 **How to Add Environment Variables in Railway**

### **Method 1: Railway Dashboard**
1. In your Railway project, click on your web service
2. Go to **"Variables"** tab
3. Click **"New Variable"**
4. Add each variable one by one:
   - **Name**: `SECRET_KEY`
   - **Value**: `XobdcXDmjtFK2IvJ&oRM^ldxH8GSMpzO`
   - Click **"Add"**
5. Repeat for all variables

### **Method 2: Bulk Import (Recommended)**
1. In Railway dashboard, go to **"Variables"** tab
2. Click **"Add Variables"** button
3. Paste this entire block:

```bash
SECRET_KEY=XobdcXDmjtFK2IvJ&oRM^ldxH8GSMpzO
JWT_SECRET_KEY=R6Sslj1bP7zr7c1WD-6YgE5J6NjNzxBOmJbYtZrfHQIVMi3sA6lRWgTO7NGE01CvFUuYLncxwvuk0c2HJKbF8w
ENCRYPTION_KEY=o3B2vTvUugVaJxjym70g7TlTt_T076QPHrvjctwVV9s=
FLASK_ENV=production
ENABLE_RATE_LIMITING=true
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=infoproductivityflows@gmail.com
MAIL_PASSWORD=vyeibhluijxd
MAIL_DEFAULT_SENDER=infoproductivityflows@gmail.com
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
CLAUDE_API_KEY=sk-ant-...
REDIS_URL=redis://...
```

4. Click **"Add Variables"**

---

## 🎯 **Required Variables You Need to Set**

### **✅ Already Provided (Use These)**
- `MAIL_USERNAME=infoproductivityflows@gmail.com`
- `MAIL_PASSWORD=vyeibhluijxd`
- `MAIL_SERVER=smtp.gmail.com`
- `MAIL_PORT=587`
- `MAIL_DEFAULT_SENDER=infoproductivityflows@gmail.com`

### **🔑 Security Keys (Use These Generated Ones)**
- `SECRET_KEY=XobdcXDmjtFK2IvJ&oRM^ldxH8GSMpzO`
- `JWT_SECRET_KEY=R6Sslj1bP7zr7c1WD-6YgE5J6NjNzxBOmJbYtZrfHQIVMi3sA6lRWgTO7NGE01CvFUuYLncxwvuk0c2HJKbF8w`
- `ENCRYPTION_KEY=o3B2vTvUugVaJxjym70g7TlTt_T076QPHrvjctwVV9s=`

### **⚙️ Production Settings (Use These)**
- `FLASK_ENV=production`
- `ENABLE_RATE_LIMITING=true`

### **💳 Payment Keys (You Need to Get These)**
- `STRIPE_SECRET_KEY=sk_live_...` (Get from Stripe dashboard)
- `STRIPE_PUBLISHABLE_KEY=pk_live_...` (Get from Stripe dashboard)

### **🤖 AI Key (You Need to Get This)**
- `CLAUDE_API_KEY=sk-ant-...` (Get from Anthropic dashboard)

### **⚡ Optional (Can Skip for Now)**
- `REDIS_URL=redis://...` (Optional for rate limiting)

---

## 🚀 **After Adding Variables**

### **Step 1: Redeploy**
1. After adding all variables, go to **"Deployments"** tab
2. Click **"Deploy"** to trigger a new deployment
3. Wait for deployment to complete

### **Step 2: Test Email**
1. Once deployed, test email sending:
```bash
curl -X POST https://productivityflow-backend-00007-ktn.railway.app/api/test-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "test@example.com",
    "subject": "Test Email",
    "body": "This is a test email from ProductivityFlow"
  }'
```

### **Step 3: Verify All Features**
1. **Team Creation**: Should work with email notifications
2. **User Registration**: Should send welcome emails
3. **Password Reset**: Should send reset emails
4. **Activity Tracking**: Should work with all features
5. **AI Reports**: Should work with Claude integration

---

## 📊 **Expected Result**

After adding all variables, you should have **14 environment variables** total:

1. `DATABASE_URL` (Auto-configured by Railway)
2. `SECRET_KEY`
3. `JWT_SECRET_KEY`
4. `ENCRYPTION_KEY`
5. `FLASK_ENV`
6. `ENABLE_RATE_LIMITING`
7. `MAIL_SERVER`
8. `MAIL_PORT`
9. `MAIL_USERNAME`
10. `MAIL_PASSWORD`
11. `MAIL_DEFAULT_SENDER`
12. `STRIPE_SECRET_KEY`
13. `STRIPE_PUBLISHABLE_KEY`
14. `CLAUDE_API_KEY`
15. `REDIS_URL` (Optional)

---

## 🎉 **Success Indicators**

When all variables are set correctly:
- ✅ Email sending works
- ✅ Team creation with email notifications
- ✅ User registration with welcome emails
- ✅ Password reset functionality
- ✅ AI-powered reports generation
- ✅ Payment processing (if Stripe keys are set)
- ✅ All ProductivityFlow features working

**Remember:** The key is using your **16-character app password** (`vyeibhluijxd`) for the email configuration, which you already have correct! 