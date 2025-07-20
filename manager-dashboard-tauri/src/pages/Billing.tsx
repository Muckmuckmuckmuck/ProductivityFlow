import { useState, useEffect } from 'react';
import { 
  CreditCard, 
  DollarSign, 
 
  Calendar,
  CheckCircle,
  AlertCircle,
  Download,
  Settings
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

interface SubscriptionData {
  status: 'active' | 'inactive' | 'cancelled' | 'past_due';
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
  status: 'paid' | 'pending' | 'failed';
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

      // Mock data for demonstration
      const mockSubscription: SubscriptionData = {
        status: 'active',
        current_period_end: '2024-02-20T00:00:00Z',
        employee_count: 5,
        monthly_cost: 49.95,
        stripe_customer_id: 'cus_123456789',
        stripe_subscription_id: 'sub_123456789'
      };

      const mockBillingHistory: BillingHistory[] = [
        {
          id: '1',
          date: '2024-01-20',
          amount: 49.95,
          status: 'paid',
          description: 'Monthly subscription - 5 employees'
        },
        {
          id: '2',
          date: '2023-12-20',
          amount: 39.96,
          status: 'paid',
          description: 'Monthly subscription - 4 employees'
        },
        {
          id: '3',
          date: '2023-11-20',
          amount: 29.97,
          status: 'paid',
          description: 'Monthly subscription - 3 employees'
        }
      ];

      setSubscription(mockSubscription);
      setBillingHistory(mockBillingHistory);

    } catch (err) {
      setError('Failed to load billing data. Please try again.');
      console.error('Billing loading error:', err);
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

  const getPaymentStatusColor = (status: string) => {
    switch (status) {
      case 'paid': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'failed': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <Card>
          <CardContent className="flex items-center justify-center h-64">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Loading Billing</h3>
              <p className="text-gray-600 mb-4">{error}</p>
              <Button onClick={loadBillingData}>Try Again</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Billing & Subscription</h1>
        <p className="text-gray-600">Manage your subscription and view billing history</p>
      </div>

      {subscription && (
        <div className="space-y-6">
          {/* Current Subscription */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <CreditCard className="w-5 h-5 mr-2 text-blue-500" />
                Current Subscription
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 mb-1">
                    ${subscription.monthly_cost}
                  </div>
                  <div className="text-sm text-gray-600">Monthly Cost</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 mb-1">
                    {subscription.employee_count}
                  </div>
                  <div className="text-sm text-gray-600">Employees</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 mb-1">
                    {subscription.status.charAt(0).toUpperCase() + subscription.status.slice(1)}
                  </div>
                  <div className="text-sm text-gray-600">Status</div>
                </div>
                
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900 mb-1">
                    {new Date(subscription.current_period_end).toLocaleDateString()}
                  </div>
                  <div className="text-sm text-gray-600">Next Billing</div>
                </div>
              </div>

              <div className="mt-6 flex items-center justify-between">
                <Badge className={getStatusColor(subscription.status)}>
                  {subscription.status.toUpperCase()}
                </Badge>
                
                <div className="flex space-x-3">
                  <Button variant="outline" size="sm">
                    <Settings className="w-4 h-4 mr-2" />
                    Manage Subscription
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Download Invoice
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Pricing Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <DollarSign className="w-5 h-5 mr-2 text-green-500" />
                Pricing
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-blue-900 mb-4">ProductivityFlow Pro</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-2">$9.99</div>
                    <div className="text-sm text-blue-700">per employee/month</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-blue-900 mb-2">Unlimited</div>
                    <div className="text-sm text-blue-700">team members</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-blue-900 mb-2">All Features</div>
                    <div className="text-sm text-blue-700">included</div>
                  </div>
                </div>
                
                <div className="mt-6 space-y-2">
                  <div className="flex items-center text-sm text-blue-800">
                    <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                    Advanced analytics and insights
                  </div>
                  <div className="flex items-center text-sm text-blue-800">
                    <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                    Burnout risk detection
                  </div>
                  <div className="flex items-center text-sm text-blue-800">
                    <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                    Distraction profile analysis
                  </div>
                  <div className="flex items-center text-sm text-blue-800">
                    <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                    Team management tools
                  </div>
                  <div className="flex items-center text-sm text-blue-800">
                    <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                    Priority support
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Billing History */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="w-5 h-5 mr-2 text-purple-500" />
                Billing History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {billingHistory.map((item) => (
                  <div key={item.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center">
                      <div className="mr-4">
                        <div className="font-medium text-gray-900">{item.description}</div>
                        <div className="text-sm text-gray-600">{item.date}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="font-semibold text-gray-900">${item.amount}</div>
                      </div>
                      <Badge className={getPaymentStatusColor(item.status)}>
                        {item.status.toUpperCase()}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}