import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { CreditCard, Calendar, DollarSign, Users, Loader2, AlertCircle } from 'lucide-react';

// Updated to use the correct backend URL
const API_URL = "https://my-home-backend-7m6d.onrender.com";

interface SubscriptionData {
  status: string;
  current_period_end: string;
  employee_count: number;
  monthly_cost: number;
  stripe_customer_id: string;
  stripe_subscription_id: string;
}

interface BillingHistory {
  id: string;
  date: string;
  amount: number;
  status: string;
  description: string;
}

export default function Billing() {
  const [subscription, setSubscription] = useState<SubscriptionData | null>(null);
  const [billingHistory, setBillingHistory] = useState<BillingHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadBillingData();
  }, []);

  const loadBillingData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get selected team from localStorage
      const selectedTeamId = localStorage.getItem('selectedTeamId');
      
      if (!selectedTeamId) {
        setError('No team selected. Please select a team first.');
        setLoading(false);
        return;
      }

      // Load subscription status
      const subscriptionResponse = await fetch(`${API_URL}/api/subscription/status`, {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (subscriptionResponse.ok) {
        const subscriptionData = await subscriptionResponse.json();
        setSubscription(subscriptionData);
      } else {
        setSubscription(null);
      }

      // For now, set empty billing history since we don't have that endpoint yet
      setBillingHistory([]);

    } catch (err) {
      setError('Failed to load billing data. Please try again.');
      console.error('Billing loading error:', err);
      setSubscription(null);
      setBillingHistory([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      case 'past_due': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading billing information...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Billing</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={loadBillingData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Billing & Subscription</h1>
        <div className="flex items-center space-x-2">
          <CreditCard className="h-5 w-5 text-gray-500" />
          <span className="text-sm text-gray-600">Payment Management</span>
        </div>
      </div>

      {/* Current Subscription */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CreditCard className="h-5 w-5" />
            <span>Current Subscription</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!subscription ? (
            <div className="text-center py-8">
              <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Subscription</h3>
              <p className="text-gray-600">Subscription information will appear here once you set up billing.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-3">
                  <Badge className={getStatusColor(subscription.status)}>
                    {subscription.status.toUpperCase()}
                  </Badge>
                </div>
                <h3 className="font-medium text-gray-900">Status</h3>
                <p className="text-sm text-gray-600">{subscription.status}</p>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mx-auto mb-3">
                  <Users className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-medium text-gray-900">Employees</h3>
                <p className="text-2xl font-bold text-green-600">{subscription.employee_count}</p>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mx-auto mb-3">
                  <DollarSign className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-medium text-gray-900">Monthly Cost</h3>
                <p className="text-2xl font-bold text-purple-600">{formatCurrency(subscription.monthly_cost)}</p>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center w-12 h-12 bg-orange-100 rounded-lg mx-auto mb-3">
                  <Calendar className="h-6 w-6 text-orange-600" />
                </div>
                <h3 className="font-medium text-gray-900">Next Billing</h3>
                <p className="text-sm text-gray-600">{formatDate(subscription.current_period_end)}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Billing History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calendar className="h-5 w-5" />
            <span>Billing History</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {billingHistory.length === 0 ? (
            <div className="text-center py-8">
              <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Billing History</h3>
              <p className="text-gray-600">Billing history will appear here once you have payment activity.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {billingHistory.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                      <CreditCard className="h-5 w-5 text-gray-600" />
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{item.description}</h3>
                      <p className="text-sm text-gray-600">{formatDate(item.date)}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-gray-900">{formatCurrency(item.amount)}</p>
                    <Badge className={getStatusColor(item.status)}>
                      {item.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Payment Methods */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CreditCard className="h-5 w-5" />
            <span>Payment Methods</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Payment Methods</h3>
            <p className="text-gray-600">Payment method management will be available soon.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}