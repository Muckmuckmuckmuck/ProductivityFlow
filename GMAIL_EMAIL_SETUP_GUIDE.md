# 📧 **Gmail Email Setup Guide for ProductivityFlow**

## 🎯 **The Problem**
Gmail has strict security settings that prevent "less secure apps" from sending emails. You need to set up an **App Password** instead of using your regular Gmail password.

---

## 🔧 **Step-by-Step Setup**

### **Step 1: Enable 2-Factor Authentication**
1. Go to your **Google Account settings**: https://myaccount.google.com/
2. Click on **"Security"** in the left sidebar
3. Find **"2-Step Verification"** and click **"Get started"**
4. Follow the setup process (usually involves your phone number)
5. **Complete the 2FA setup**

### **Step 2: Generate an App Password**
1. Go to your **Google Account settings**: https://myaccount.google.com/
2. Click on **"Security"** in the left sidebar
3. Find **"App passwords"** (under "2-Step Verification")
4. Click **"App passwords"**
5. Select **"Mail"** as the app
6. Select **"Other (Custom name)"** as the device
7. Enter a name like **"ProductivityFlow Backend"**
8. Click **"Generate"**
9. **Copy the 16-character password** (it looks like: `abcd efgh ijkl mnop`)

### **Step 3: Set Environment Variables**
In your Railway dashboard, set these environment variables:

```bash
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_DEFAULT_SENDER=your-gmail@gmail.com
```

**Important Notes:**
- Use your **regular Gmail address** for `MAIL_USERNAME`
- Use the **16-character app password** (not your regular Gmail password) for `MAIL_PASSWORD`
- Remove spaces from the app password when setting it in Railway

---

## 🧪 **Testing the Email Setup**

### **Test Email Endpoint**
Once you've set the environment variables, you can test email sending by calling this endpoint:

```bash
curl -X POST https://your-railway-app.railway.app/api/test-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "test@example.com",
    "subject": "Test Email",
    "body": "This is a test email from ProductivityFlow"
  }'
```

### **Expected Response**
```json
{
  "success": true,
  "message": "Email sent successfully"
}
```

---

## 🚨 **Common Issues & Solutions**

### **Issue 1: "Invalid credentials"**
**Solution:**
- Make sure you're using the **16-character app password**, not your regular Gmail password
- Remove any spaces from the app password in the environment variable
- Verify 2FA is enabled on your Google account

### **Issue 2: "Username and Password not accepted"**
**Solution:**
- Double-check that `MAIL_USERNAME` is your complete Gmail address (e.g., `john.doe@gmail.com`)
- Ensure the app password was generated correctly
- Try regenerating the app password

### **Issue 3: "Connection refused"**
**Solution:**
- Verify `MAIL_SERVER=smtp.gmail.com` and `MAIL_PORT=587`
- Check that your Railway app can make outbound connections
- Ensure no firewall is blocking SMTP traffic

### **Issue 4: "Authentication required"**
**Solution:**
- Make sure you've enabled 2FA on your Google account
- Generate a fresh app password
- Wait a few minutes after generating the app password before testing

---

## 🔒 **Security Best Practices**

### **App Password Security**
- **Never share** your app password
- **Regenerate** the app password if you suspect it's compromised
- **Use different** app passwords for different services
- **Delete unused** app passwords regularly

### **Environment Variable Security**
- **Never commit** environment variables to your code repository
- **Use Railway's** secure environment variable storage
- **Rotate** app passwords periodically
- **Monitor** email sending logs for unusual activity

---

## 📋 **Complete Environment Variables Checklist**

Make sure you have ALL these environment variables set in Railway:

```bash
# Essential (Required)
DATABASE_URL=postgresql://...  # Auto-configured by Railway
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key
FLASK_ENV=production
ENABLE_RATE_LIMITING=true

# Email (Gmail Setup)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-gmail@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_DEFAULT_SENDER=your-gmail@gmail.com

# Payment (Stripe)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# AI (Claude)
CLAUDE_API_KEY=sk-ant-...

# Optional
REDIS_URL=redis://...
```

---

## 🎉 **Success Indicators**

When email is working correctly, you should see:

1. **No errors** in Railway logs when sending emails
2. **Successful delivery** of test emails
3. **Proper formatting** of ProductivityFlow emails
4. **Fast response times** from email endpoints

---

## 📞 **Need Help?**

If you're still having issues:

1. **Check Railway logs** for specific error messages
2. **Verify all environment variables** are set correctly
3. **Test with a simple email** first
4. **Ensure your Gmail account** is in good standing
5. **Try regenerating** the app password

**Remember:** The key is using the **16-character app password**, not your regular Gmail password! 