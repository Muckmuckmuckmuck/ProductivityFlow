# 🚀 ProductivityFlow - Quick Start Guide

## **IMMEDIATE SETUP (5 minutes)**

### **1. Start the Backend**
```bash
cd /Users/jayreddy/Desktop/ProductivityFlow
python3 start_working_backend_with_reset.py
```

### **2. Start the CORS Proxy**
```bash
node cors_proxy.js
```

### **3. Install the Apps**
- **Manager Dashboard**: `WorkFlow-Manager-Console-v2.7_2.7.0_x64.dmg`
- **Employee Tracker**: `WorkFlow-Employee-Monitor-v2.3_2.3.0_x64.dmg`

---

## **✅ WHAT'S WORKING RIGHT NOW**

### **Email Verification**
- ✅ Registration sends verification emails
- ✅ Click links in emails to verify accounts
- ✅ Login works after verification

### **Password Reset**
- ✅ Reset passwords via email
- ✅ Professional email templates
- ✅ Secure token-based reset

### **Authentication**
- ✅ JWT tokens with 1-hour expiry
- ✅ Secure password hashing
- ✅ Input validation and sanitization

---

## **📧 EMAIL SYSTEM**

**Gmail Account**: `infoproductivityflows@gmail.com`
**Status**: ✅ Configured and working
**Features**: 
- Verification emails
- Password reset emails
- Professional HTML templates

---

## **🔧 TROUBLESHOOTING**

### **If apps can't connect:**
1. Check backend is running: `curl http://localhost:5000/health`
2. Check proxy is running: `curl http://localhost:3001/health`
3. Restart both services

### **If emails not received:**
1. Check spam folder
2. Verify Gmail app password is correct
3. Check backend logs for email errors

### **If login fails:**
1. Verify email first (check inbox)
2. Use password reset if needed
3. Check password strength requirements

---

## **🎯 READY TO USE**

**The system is fully functional and ready for immediate use!**

- ✅ Backend: Working with email verification
- ✅ Apps: Built and tested
- ✅ Security: All features implemented
- ✅ Email: Gmail SMTP configured

**Start the backend and install the apps to begin using ProductivityFlow! 🚀** 