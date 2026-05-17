import React, { useEffect, useState, useCallback } from 'react';
import { toast } from 'react-toastify';
import { api } from '../utils/api';
import { useAuth } from '../middleware/auth'; // Hypothethical auth hook, adjust based on existing Auth context

// Types based on backend subscription and billing models
interface SubscriptionPlan {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  interval: 'month' | 'year';
  features: string[];
  is_active: boolean;
}

interface CurrentSubscription {
  plan: SubscriptionPlan;
  status: 'active' | 'canceled' | 'past_due' | 'trialing';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  trial_end?: string;
}

interface Invoice {
  id: string;
  amount: number;
  currency: string;
  status: 'paid' | 'unpaid' | 'overdue' | 'canceled';
  date: string;
  pdf_url?: string;
}

const Billing: React.FC = () => {
  const { user } = useAuth();
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [currentSubscription, setCurrentSubscription] = useState<CurrentSubscription | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [changingPlan, setChangingPlan] = useState<string | null>(null);

  const fetchBillingData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [plansRes, subRes, invoicesRes] = await Promise.all([
        api.get('/api/billing/plans'),
        api.get('/api/billing/current'),
        api.get('/api/billing/history'),
      ]);

      setPlans(plansRes.data.plans || []);
      setCurrentSubscription(subRes.data.subscription || null);
      setInvoices(invoicesRes.data.invoices || []);
    } catch (err: any) {
      const message = err?.response?.data?.detail || err?.message || 'Failed to load billing data';
      setError(message);
      toast.error(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBillingData();
  }, [fetchBillingData]);

  if (loading) {
    return <div>Loading billing information...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <h2>Subscription Plans</h2>
      {plans.length === 0 && <p>No plans available.</p>}
      <ul>
        {plans.map((plan) => (
          <li key={plan.id}>
            {plan.name} - ${plan.price}/{plan.interval}
          </li>
        ))}
      </ul>

      <h2>Current Subscription</h2>
      {currentSubscription ? (
        <div>
          <p>Plan: {currentSubscription.plan.name}</p>
          <p>Status: {currentSubscription.status}</p>
          <p>
            Period: {new Date(currentSubscription.current_period_start).toLocaleDateString()} –{' '}
            {new Date(currentSubscription.current_period_end).toLocaleDateString()}
          </p>
        </div>
      ) : (
        <p>No active subscription.</p>
      )}

      <h2>Invoice History</h2>
      {invoices.length === 0 && <p>No invoices found.</p>}
      <ul>
        {invoices.map((invoice) => (
          <li key={invoice.id}>
            {new Date(invoice.date).toLocaleDateString()} - ${invoice.amount} - {invoice.status}
            {invoice.pdf_url && (
              <a href={invoice.pdf_url} target="_blank" rel="noopener noreferrer">
                View PDF
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Billing;