# ProductivityFlow Employee Dashboard

A modern web-based dashboard for employees to view their productivity data, activity history, and personal statistics.

## Features

- **Employee Login**: Secure authentication using employee codes
- **Dashboard Overview**: View daily productivity metrics and statistics
- **Activity Details**: Detailed timeline of daily activities
- **Profile Management**: Personal information and work statistics
- **Real-time Data**: Live updates from the ProductivityFlow backend

## Quick Start

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- ProductivityFlow backend running on `https://my-home-backend-7m6d.onrender.com`

### Installation

1. Navigate to the employee dashboard directory:
   ```bash
   cd employee-dashboard
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:3001`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Usage

### Employee Login

1. Enter your employee code (provided by your manager)
2. Click "Sign In" to access your dashboard

### Dashboard Features

- **Overview**: View your daily productivity metrics
- **Activity**: See detailed activity timeline
- **Profile**: Access your personal information and statistics

## API Endpoints

The dashboard connects to the following backend endpoints:

- `POST /api/auth/employee-login` - Employee authentication
- `GET /api/employee/daily-summary` - Daily productivity summary
- `GET /api/employee/activities` - Activity history
- `GET /api/employee/profile` - Employee profile data

## Technology Stack

- **Frontend**: React 18 with Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Routing**: React Router DOM

## Development

### Project Structure

```
src/
├── components/          # React components
│   ├── LoginView.jsx    # Employee login
│   ├── DashboardView.jsx # Main dashboard
│   ├── ActivityView.jsx # Activity details
│   └── ProfileView.jsx  # Profile management
├── contexts/            # React contexts
│   └── AuthContext.jsx  # Authentication context
├── App.jsx             # Main app component
├── main.jsx            # App entry point
└── index.css           # Global styles
```

### Customization

- Modify `src/contexts/AuthContext.jsx` to change API endpoints
- Update styling in `src/index.css` and component files
- Add new routes in `src/App.jsx`

## Support

For issues or questions, please refer to the main ProductivityFlow documentation or contact your system administrator. 