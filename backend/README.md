# ProductivityFlow Backend

A Flask-based backend API for the ProductivityFlow productivity tracking system.

## Environment Variables

The following environment variables are required for the backend to function properly:

### Database Configuration
- **DATABASE_URL**: PostgreSQL connection string (e.g., `postgresql://user:password@host:port/database`)
  - Required for database connectivity
  - Automatically converts `postgres://` to `postgresql://` for compatibility

### Security Configuration
- **SECRET_KEY**: Flask application secret key for session management
  - Used for Flask session encryption and security
  - Should be a strong, random string in production

- **JWT_SECRET_KEY**: Secret key for JWT token generation and validation
  - Used for user authentication tokens
  - Should be different from SECRET_KEY

- **ENCRYPTION_KEY**: Fernet encryption key for secure API key storage
  - Used to encrypt sensitive data like API keys
  - Generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

### Payment Processing (Stripe)
- **STRIPE_SECRET_KEY**: Stripe secret key for payment processing
  - Used for creating customers, subscriptions, and processing payments
  - Get from Stripe Dashboard

- **STRIPE_PUBLISHABLE_KEY**: Stripe publishable key for client-side operations
  - Used for client-side payment forms
  - Get from Stripe Dashboard

### AI Integration (Claude)
- **CLAUDE_API_KEY**: Anthropic Claude API key for AI-powered productivity analysis
  - Used for generating productivity reports and insights
  - Get from Anthropic Console

### Email Configuration
- **MAIL_SERVER**: SMTP server for sending emails (default: `smtp.gmail.com`)
  - Used for verification emails and notifications

- **MAIL_PORT**: SMTP port (default: `587`)
  - Port for SMTP server connection

- **MAIL_USERNAME**: Email username/address for sending emails
  - Email address used as sender

- **MAIL_PASSWORD**: Email password or app-specific password
  - Password for SMTP authentication

- **MAIL_DEFAULT_SENDER**: Default sender email address
  - Fallback sender address if not specified in individual emails

### Optional Configuration
- **ENABLE_RATE_LIMITING**: Enable/disable rate limiting (default: `true`)
  - Set to `false` to disable rate limiting (not recommended for production)

- **REDIS_URL**: Redis connection URL for rate limiting (optional)
  - If not provided, uses in-memory rate limiting
  - Format: `redis://host:port/database`

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   Create a `.env` file in the backend directory with all required variables:
   ```env
   DATABASE_URL=postgresql://user:password@host:port/database
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   ENCRYPTION_KEY=your-encryption-key-here
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   CLAUDE_API_KEY=sk-ant-...
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

3. **Initialize Database**:
   ```bash
   python application.py
   ```

4. **Run the Application**:
   ```bash
   gunicorn application:application
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/verify` - Verify email

### Teams
- `GET /api/teams` - Get user's teams
- `POST /api/teams` - Create new team
- `POST /api/teams/join` - Join team with code
- `POST /api/teams/join-with-email` - Join team with email
- `GET /api/teams/public` - Get public teams
- `GET /api/teams/<team_id>/members` - Get team members
- `POST /api/teams/<team_id>/activity` - Submit activity data

### Analytics
- `GET /api/analytics/burnout-risk` - Get burnout risk analysis
- `GET /api/analytics/distraction-profile` - Get distraction profile
- `GET /api/employee/daily-summary` - Get daily summary

### Subscriptions
- `GET /api/subscription/status` - Get subscription status
- `POST /api/subscription/update-payment` - Update payment method
- `GET /api/subscription/customer-portal` - Get customer portal URL
- `POST /api/subscription/webhook` - Stripe webhook handler

### System
- `GET /health` - Health check
- `GET /api/version` - Get API version
- `GET /api/config/stripe` - Get Stripe configuration
- `GET /api/updates/<platform>/<version>` - Check for updates

## Security Features

- **CORS Protection**: Comprehensive CORS configuration for all origins
- **Rate Limiting**: Configurable rate limiting with Redis or in-memory storage
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt password hashing
- **API Key Encryption**: Secure storage of sensitive API keys
- **Input Validation**: Comprehensive input validation and sanitization

## Deployment

The backend is designed to be deployed on Render.com with automatic database initialization and health checks.

### Render Deployment
1. Connect your GitHub repository to Render
2. Set all required environment variables in Render dashboard
3. Deploy as a Web Service
4. The application will automatically initialize the database on first startup

## Monitoring

- **Health Check**: `/health` endpoint for monitoring
- **Logging**: Comprehensive logging for debugging and monitoring
- **Error Handling**: Proper error responses with appropriate HTTP status codes
- **Performance**: Database indexing and query optimization

## Support

For issues or questions, please refer to the main project documentation or create an issue in the GitHub repository. 