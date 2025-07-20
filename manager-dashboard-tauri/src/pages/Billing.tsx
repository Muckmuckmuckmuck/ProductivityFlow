import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { 
  CreditCard, 
  Users, 
  Calendar, 
  DollarSign, 
  AlertTriangle, 
  CheckCircle, 
  Loader2,
  ExternalLink,
  Download,
  Clock
} from 'lucide-react';

// Updated to use the correct backend URL
const API_URL = "https://productivityflow-backend-v3.onrender.com";

interface Subscription {
  status: 'active' | 'inactive' | 'cancelled' | 'past_due' | 'trialing';
  employeeCount: number;
  monthlyCost: number;
  currentPeriodStart: string;
  currentPeriodEnd: string;
  nextBillingDate: string;
  stripeCustomerId?: string;
  stripeSubscriptionId?: string;
  trialEnd?: string;
  isTrialActive: boolean;
}

interface BillingHistory {
  id: string;
  date: string;
  amount: number;
  status: 'paid' | 'pending' | 'failed';
  description: string;
}

export default function BillingPage() {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [billingHistory, setBillingHistory] = useState<BillingHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [managingSubscription, setManagingSubscription] = useState(false);
  const [downloadingReports, setDownloadingReports] = useState(false);

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch subscription status
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
        // Set mock data for demonstration
        setSubscription({
          status: 'trialing',
          employeeCount: 3,
          monthlyCost: 29.97, // $9.99 per employee
          currentPeriodStart: new Date().toISOString(),
          currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
          nextBillingDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
          isTrialActive: true,
          trialEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
        });
      }

      // Mock billing history
      setBillingHistory([
        {
          id: '1',
          date: new Date().toISOString(),
          amount: 0,
          status: 'paid',
          description: 'Free trial - 30 days'
        }
      ]);

    } catch (error: any) {
      console.error("Error fetching billing data:", error);
      setError("Failed to load billing information. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleManageSubscription = async () => {
    try {
      setManagingSubscription(true);
      
      const response = await fetch(`${API_URL}/api/subscription/customer-portal`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.url) {
          window.open(data.url, '_blank');
        }
      } else {
        throw new Error('Failed to get customer portal URL');
      }
    } catch (error: any) {
      console.error("Error managing subscription:", error);
      setError("Failed to open subscription management. Please try again.");
    } finally {
      setManagingSubscription(false);
    }
  };

  const handleDownloadReports = async () => {
    try {
      setDownloadingReports(true);
      
      // Simulate downloading reports
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Create a mock CSV file for demonstration
      const csvContent = `Employee Name,Date,Hour,Productive Hours,Unproductive Hours,Productivity Score,Summary
John Doe,${new Date().toISOString().split('T')[0]},09:00,0.8,0.2,80%,Focused on coding tasks
John Doe,${new Date().toISOString().split('T')[0]},10:00,0.9,0.1,90%,Completed feature implementation
Jane Smith,${new Date().toISOString().split('T')[0]},09:00,0.7,0.3,70%,Working on documentation
Jane Smith,${new Date().toISOString().split('T')[0]},10:00,0.6,0.4,60%,Team meeting and planning`;

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `productivity-reports-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
    } catch (error: any) {
      console.error("Error downloading reports:", error);
      setError("Failed to download reports. Please try again.");
    } finally {
      setDownloadingReports(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'trialing':
        return 'bg-blue-100 text-blue-800';
      case 'past_due':
        return 'bg-red-100 text-red-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4" />;
      case 'trialing':
        return <Clock className="h-4 w-4" />;
      case 'past_due':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
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

  const getDaysUntilBilling = () => {
    if (!subscription?.nextBillingDate) return 0;
    const nextBilling = new Date(subscription.nextBillingDate);
    const now = new Date();
    const diffTime = nextBilling.getTime() - now.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Billing & Subscription</h1>
          <p className="text-gray-500">Loading your billing information...</p>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Billing & Subscription</h1>
          <p className="text-gray-500">Manage your subscription and billing</p>
        </div>
        
        <Card className="border-red-200">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className="h-12 w-12 text-red-500 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Unable to Load Billing</h3>
            <p className="text-gray-600 text-center mb-4 max-w-md">{error}</p>
            <Button onClick={fetchBillingData}>
              Try Again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Billing & Subscription</h1>
        <p className="text-gray-500">Manage your subscription and billing</p>
      </div>

      {/* Current Plan Overview */}
      <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <CreditCard className="mr-2 h-5 w-5" />
              Current Plan
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Status</span>
              <Badge className={getStatusColor(subscription?.status || 'inactive')}>
                <div className="flex items-center space-x-1">
                  {getStatusIcon(subscription?.status || 'inactive')}
                  <span className="capitalize">{subscription?.status || 'inactive'}</span>
                </div>
              </Badge>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Employees</span>
              <span className="font-semibold">{subscription?.employeeCount || 0}</span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Monthly Cost</span>
              <span className="font-semibold">{formatCurrency(subscription?.monthlyCost || 0)}</span>
            </div>

            {subscription?.isTrialActive && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-blue-600" />
                  <div>
                    <p className="text-sm font-medium text-blue-800">Free Trial Active</p>
                    <p className="text-xs text-blue-600">
                      {getDaysUntilBilling()} days remaining
                    </p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Calendar className="mr-2 h-5 w-5" />
              Billing Cycle
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Current Period</span>
              <span className="text-sm font-medium">
                {subscription?.currentPeriodStart ? formatDate(subscription.currentPeriodStart) : 'N/A'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Next Billing</span>
              <span className="text-sm font-medium">
                {subscription?.nextBillingDate ? formatDate(subscription.nextBillingDate) : 'N/A'}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Days Until Billing</span>
              <span className="font-semibold text-blue-600">
                {getDaysUntilBilling()}
              </span>
            </div>

            {subscription?.isTrialActive && (
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  <strong>Note:</strong> Your trial ends on {subscription.trialEnd ? formatDate(subscription.trialEnd) : 'N/A'}. 
                  Add payment method to continue after trial.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <DollarSign className="mr-2 h-5 w-5" />
              Pricing
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-800">$9.99</div>
              <div className="text-sm text-gray-600">per employee/month</div>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Unlimited activity tracking</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>AI-powered productivity reports</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Team management tools</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Security & fraud detection</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Subscription Management</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Update payment methods, view invoices, and manage your subscription settings.
            </p>
            <Button 
              onClick={handleManageSubscription}
              disabled={managingSubscription}
              className="w-full"
            >
              {managingSubscription ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Opening...
                </>
              ) : (
                <>
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Manage Subscription
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Download Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-600 mb-4">
              Download daily employee productivity reports with hourly summaries.
            </p>
            <Button 
              onClick={handleDownloadReports}
              disabled={downloadingReports}
              variant="outline"
              className="w-full"
            >
              {downloadingReports ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Downloading...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4 mr-2" />
                  Download Reports
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Billing History */}
      <Card>
        <CardHeader>
          <CardTitle>Billing History</CardTitle>
        </CardHeader>
        <CardContent>
          {billingHistory.length === 0 ? (
            <div className="text-center py-8">
              <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No billing history yet</p>
              <p className="text-sm text-gray-400">Your first invoice will appear here after your trial ends</p>
            </div>
          ) : (
            <div className="space-y-4">
              {billingHistory.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium">{item.description}</p>
                    <p className="text-sm text-gray-500">{formatDate(item.date)}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">{formatCurrency(item.amount)}</p>
                    <Badge className={
                      item.status === 'paid' ? 'bg-green-100 text-green-800' :
                      item.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }>
                      {item.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Trial Warning */}
      {subscription?.isTrialActive && (
        <Card className="border-orange-200">
          <CardContent className="p-6">
            <div className="flex items-start space-x-4">
              <AlertTriangle className="h-6 w-6 text-orange-600 mt-1" />
              <div>
                <h3 className="text-lg font-semibold text-orange-800 mb-2">
                  Trial Ending Soon
                </h3>
                <p className="text-orange-700 mb-4">
                  Your free trial ends in {getDaysUntilBilling()} days. To continue using ProductivityFlow, 
                  please add a payment method and upgrade to a paid plan.
                </p>
                <div className="flex space-x-3">
                  <Button onClick={handleManageSubscription}>
                    Add Payment Method
                  </Button>
                  <Button variant="outline">
                    Learn More
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}