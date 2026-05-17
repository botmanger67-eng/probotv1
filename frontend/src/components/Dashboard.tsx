import React, { useState, useEffect, useCallback } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { fetchAnalytics } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

// ------------------------------------------------------------------
// Types
// ------------------------------------------------------------------

interface AnalyticsData {
  users: {
    total: number;
    active: number;
    newToday: number;
    growth: Array<{ date: string; count: number }>;
  };
  projects: {
    total: number;
    completed: number;
    inProgress: number;
    byType: Array<{ name: string; value: number }>;
    creationTrend: Array<{ date: string; created: number; completed: number }>;
  };
  subscriptions: {
    totalRevenue: number;
    activeCount: number;
    churnRate: number;
    revenueHistory: Array<{ date: string; amount: number }>;
  };
  performance: {
    avgResponseTime: number;
    errorRate: number;
    requestsToday: number;
    uptime: number;
  };
}

interface DashboardProps {
  className?: string;
}

// ------------------------------------------------------------------
// Constants
// ------------------------------------------------------------------

const CHART_COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#a4de6c'];
const REFRESH_INTERVAL = 60000; // 1 minute

const initialData: AnalyticsData = {
  users: { total: 0, active: 0, newToday: 0, growth: [] },
  projects: { total: 0, completed: 0, inProgress: 0, byType: [], creationTrend: [] },
  subscriptions: { totalRevenue: 0, activeCount: 0, churnRate: 0, revenueHistory: [] },
  performance: { avgResponseTime: 0, errorRate: 0, requestsToday: 0, uptime: 0 },
};

// ------------------------------------------------------------------
// Helper components
// ------------------------------------------------------------------

const StatCard = ({
  title,
  value,
  subtitle,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
}) => (
  <div className="stat-card">
    <h3>{title}</h3>
    <p className="stat-value">{value}</p>
    {subtitle && <p className="stat-subtitle">{subtitle}</p>}
  </div>
);

const Dashboard: React.FC<DashboardProps> = ({ className }) => {
  const [data, setData] = useState<AnalyticsData>(initialData);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const analytics = await fetchAnalytics(user?.token ?? '');
      setData(analytics);
    } catch (err) {
      setError('Failed to fetch analytics data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [user?.token]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchData]);

  if (loading) return <div className="dashboard-loading">Loading…</div>;
  if (error) return <div className="dashboard-error">{error}</div>;

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

  return (
    <div className={`dashboard ${className ?? ''}`}>
      <h1>Dashboard</h1>

      {/* Summary Stats */}
      <section className="stats-grid">
        <StatCard title="Total Users" value={data.users.total} subtitle={`${data.users.active} active`} />
        <StatCard title="New Today" value={data.users.newToday} />
        <StatCard title="Projects" value={data.projects.total} />
        <StatCard
          title="Revenue"
          value={formatCurrency(data.subscriptions.totalRevenue)}
          subtitle={`${data.subscriptions.activeCount} active subscriptions`}
        />
        <StatCard title="Avg Response" value={`${data.performance.avgResponseTime}ms`} />
        <StatCard title="Uptime" value={`${data.performance.uptime}%`} />
      </section>

      {/* Charts */}
      <section className="charts-grid">
        {/* User Growth (Area Chart) */}
        <div className="chart-container">
          <h2>User Growth</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data.users.growth}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="count" stroke="#8884d8" fill="#8884d8" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Projects by Type (Pie Chart) */}
        <div className="chart-container">
          <h2>Projects by Type</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data.projects.byType}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label
              >
                {data.projects.byType.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Project Creation Trend (Bar Chart) */}
        <div className="chart-container">
          <h2>Project Creation / Completion</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.projects.creationTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="created" fill="#82ca9d" name="Created" />
              <Bar dataKey="completed" fill="#8884d8" name="Completed" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Revenue History (Line Chart) */}
        <div className="chart-container">
          <h2>Revenue History</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.subscriptions.revenueHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="amount" stroke="#ffc658" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;