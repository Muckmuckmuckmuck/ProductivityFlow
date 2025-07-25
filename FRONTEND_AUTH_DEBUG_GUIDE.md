# Frontend Authentication Debug Guide

## 🎯 **Authentication Issues Fixed**

The backend authentication is now working perfectly! Here are the working test credentials:

### **Working Test Credentials**

#### **Manager Dashboard**
```
Email: manager@productivityflow.com
Password: password123
```

#### **Employee Tracker**
```
Email: employee@productivityflow.com
Password: password123
```

#### **Alternative Test User**
```
Email: test@example.com
Password: password123
```

## 🔧 **Debugging Tools**

### **1. Backend Debug Script**
```bash
cd backend
python debug_auth.py
```

### **2. Authentication Fix Script**
```bash
cd backend
python fix_auth.py
```

### **3. Manual API Testing**
```bash
# Test manager login
curl -X POST https://productivityflow-backend-496367590729.us-central1.run.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "manager@productivityflow.com", "password": "password123"}'

# Test employee login
curl -X POST https://productivityflow-backend-496367590729.us-central1.run.app/api/auth/employee-login \
  -H "Content-Type: application/json" \
  -d '{"email": "employee@productivityflow.com", "password": "password123"}'
```

## 🐛 **Common Frontend Issues & Solutions**

### **Issue 1: "Cannot connect to server"**
**Symptoms**: Network error, connection timeout
**Solutions**:
- Check internet connection
- Verify API URL is correct: `https://productivityflow-backend-496367590729.us-central1.run.app`
- Check if backend is running

### **Issue 2: "Invalid credentials"**
**Symptoms**: Login fails with wrong password error
**Solutions**:
- Use the exact credentials above
- Check for typos in email/password
- Try the test credentials provided

### **Issue 3: "User not found"**
**Symptoms**: User doesn't exist error
**Solutions**:
- Use the test credentials provided
- Register a new account first
- Check email spelling

### **Issue 4: "Team code invalid"**
**Symptoms**: Cannot join team
**Solutions**:
- Create a team first using Manager Dashboard
- Use the exact team code provided
- Check for typos in team code

## 🧪 **Step-by-Step Testing**

### **Testing Manager Dashboard**

1. **Open Manager Dashboard app**
2. **Click "Create Account"**
3. **Enter credentials**:
   - Email: `manager@productivityflow.com`
   - Password: `password123`
   - Name: `Test Manager`
4. **Click "Create Account"**
5. **Should see success message**
6. **Click "Sign In"**
7. **Enter same credentials**
8. **Should log in successfully**

### **Testing Employee Tracker**

1. **Open Employee Tracker app**
2. **Click "Create Account"**
3. **Enter credentials**:
   - Name: `Test Employee`
   - Team Code: Get from manager (or use test code)
4. **Click "Join Team"**
5. **Should see success message**
6. **Click "Sign In"**
7. **Enter generated credentials**:
   - Email: `employee@productivityflow.com`
   - Password: `password123`
8. **Should log in successfully**

## 🔍 **Debugging Steps**

### **Step 1: Check Backend Status**
```bash
curl https://productivityflow-backend-496367590729.us-central1.run.app/health
```
**Expected**: `{"status": "healthy", "database": "connected"}`

### **Step 2: Test Authentication Endpoints**
```bash
# Test registration
curl -X POST https://productivityflow-backend-496367590729.us-central1.run.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@debug.com", "password": "password123", "name": "Debug User"}'

# Test login
curl -X POST https://productivityflow-backend-496367590729.us-central1.run.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@debug.com", "password": "password123"}'
```

### **Step 3: Check Frontend Console**
1. **Open Developer Tools** (F12)
2. **Go to Console tab**
3. **Look for error messages**
4. **Check Network tab for failed requests**

### **Step 4: Verify API URLs**
Make sure all components use the correct API URL:
```javascript
const API_URL = "https://productivityflow-backend-496367590729.us-central1.run.app";
```

## 📱 **Testing in Desktop Apps**

### **Manager Dashboard Testing**
1. **Install the latest DMG**: `ProductivityFlow Manager Dashboard v3.1.0_3.1.0_x64_ALL_FIXED.dmg`
2. **Open the app**
3. **Use test credentials**: `manager@productivityflow.com` / `password123`
4. **Create a team** and get the employee code
5. **Share the code** with employees

### **Employee Tracker Testing**
1. **Install the latest DMG**: `ProductivityFlow Employee Tracker v3.1.0_3.1.0_x64_ALL_FIXED.dmg`
2. **Open the app**
3. **Use test credentials**: `employee@productivityflow.com` / `password123`
4. **Or join a team** using the code from manager

## 🚨 **Troubleshooting**

### **If Authentication Still Fails**

1. **Check the backend logs**:
   ```bash
   cd backend
   python -c "from application import application; app = application.test_client(); print('Testing login...'); response = app.post('/api/auth/login', json={'email': 'manager@productivityflow.com', 'password': 'password123'}); print(f'Status: {response.status_code}'); print(f'Response: {response.data.decode()}')"
   ```

2. **Verify database**:
   ```bash
   cd backend
   python debug_auth.py
   ```

3. **Reset test credentials**:
   ```bash
   cd backend
   python fix_auth.py
   ```

4. **Check frontend build**:
   ```bash
   cd employee-tracker-tauri
   npm run build
   ```

### **If Frontend Shows Errors**

1. **Check browser console** for JavaScript errors
2. **Verify API calls** in Network tab
3. **Check for CORS issues**
4. **Verify Tauri invoke calls** are working

## ✅ **Expected Results**

### **Successful Login Response**
```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "email": "manager@productivityflow.com",
    "id": "user_xxx",
    "name": "Test Manager"
  }
}
```

### **Successful Registration Response**
```json
{
  "message": "User registered successfully",
  "user_id": "user_xxx"
}
```

## 🎉 **Success Indicators**

- ✅ **Login successful** message appears
- ✅ **Dashboard loads** with user data
- ✅ **No error messages** in console
- ✅ **Token is stored** in local storage
- ✅ **Session persists** after app restart

---

**Status**: ✅ **Authentication system is working correctly with provided test credentials** 