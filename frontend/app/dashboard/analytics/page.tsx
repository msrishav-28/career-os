'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';
import { TrendingUp, TrendingDown, Users, Mail, Target, Award } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import toast from 'react-hot-toast';

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);
  const [timeRange, setTimeRange] = useState(30);

  const userId = 'demo-user';

  useEffect(() => {
    loadAnalytics();
  }, [timeRange]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      
      const response = await apiClient.get(`/analytics/dashboard?user_id=${userId}&days=${timeRange}`);
      setAnalytics(response.data);
      
    } catch (error) {
      console.error('Error loading analytics:', error);
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="text-center">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(Number(e.target.value))}
              className="px-4 py-2 border rounded-lg"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Messages Sent"
            value={analytics?.outreach?.messages_sent || 0}
            icon={<Mail className="w-6 h-6" />}
            trend="+12%"
            trendUp={true}
          />
          <MetricCard
            title="Response Rate"
            value={`${analytics?.outreach?.response_rate || 0}%`}
            icon={<TrendingUp className="w-6 h-6" />}
            trend="+5%"
            trendUp={true}
          />
          <MetricCard
            title="Total Contacts"
            value={analytics?.pipeline?.total_contacts || 0}
            icon={<Users className="w-6 h-6" />}
            trend="+23"
            trendUp={true}
          />
          <MetricCard
            title="Network Health"
            value={`${analytics?.network?.health_score || 0}/10`}
            icon={<Award className="w-6 h-6" />}
            trend="Excellent"
            trendUp={true}
          />
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Response Rate Trend */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Response Rate Trend</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={sampleTimeSeriesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="response_rate" stroke="#3b82f6" name="Response Rate %" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Pipeline Distribution */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Pipeline Distribution</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getPipelineData(analytics?.pipeline?.by_status)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Insights Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Personalization Score */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold mb-4">Avg Personalization</h3>
            <div className="text-4xl font-bold text-blue-600 mb-2">
              {analytics?.outreach?.avg_personalization || 0}/100
            </div>
            <p className="text-gray-600">Quality threshold: 70+</p>
            <div className="mt-4 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 rounded-full h-2"
                style={{ width: `${analytics?.outreach?.avg_personalization || 0}%` }}
              />
            </div>
          </div>

          {/* Conversion Rate */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold mb-4">Conversion Rate</h3>
            <div className="text-4xl font-bold text-green-600 mb-2">
              {analytics?.pipeline?.conversion_rate || 0}%
            </div>
            <p className="text-gray-600">Contact → Response</p>
            <div className="mt-4">
              <div className="flex justify-between text-sm">
                <span>Target: 25%</span>
                <span className="text-green-600">
                  {analytics?.pipeline?.conversion_rate >= 25 ? '✓ On track' : '↗ Improving'}
                </span>
              </div>
            </div>
          </div>

          {/* Skill Gaps */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold mb-4">Top Skill Gap</h3>
            {analytics?.skill_gaps?.top_gap ? (
              <>
                <div className="text-2xl font-bold text-orange-600 mb-2">
                  {analytics.skill_gaps.top_gap.skill}
                </div>
                <p className="text-gray-600">
                  Appears in {analytics.skill_gaps.top_gap.frequency} opportunities
                </p>
                <button className="mt-4 px-4 py-2 bg-orange-100 text-orange-600 rounded-lg hover:bg-orange-200 transition">
                  Start Learning
                </button>
              </>
            ) : (
              <p className="text-gray-600">No skill gaps identified</p>
            )}
          </div>
        </div>

        {/* Recent Insights */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Recent Insights</h2>
          <div className="space-y-4">
            <InsightItem
              type="success"
              message="Your messages mentioning specific projects have 40% higher response rates"
              action="Continue this approach"
            />
            <InsightItem
              type="warning"
              message="Response rate dropped 5% this week. Consider improving personalization"
              action="Review templates"
            />
            <InsightItem
              type="info"
              message="Best time to send: Tuesday mornings (9-11 AM) show 35% higher open rates"
              action="Schedule accordingly"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon, trend, trendUp }: any) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-start mb-4">
        <div className="text-gray-600">{title}</div>
        <div className="text-blue-600">{icon}</div>
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-2">{value}</div>
      <div className={`text-sm flex items-center gap-1 ${trendUp ? 'text-green-600' : 'text-red-600'}`}>
        {trendUp ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
        {trend}
      </div>
    </div>
  );
}

function InsightItem({ type, message, action }: any) {
  const colors = {
    success: 'bg-green-50 border-green-200 text-green-800',
    warning: 'bg-orange-50 border-orange-200 text-orange-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800'
  };

  return (
    <div className={`border-l-4 p-4 ${colors[type as keyof typeof colors]}`}>
      <p className="font-medium mb-2">{message}</p>
      <button className="text-sm font-semibold hover:underline">
        → {action}
      </button>
    </div>
  );
}

function getPipelineData(byStatus: any) {
  if (!byStatus) return [];
  
  return Object.entries(byStatus).map(([name, count]) => ({
    name: name.replace('_', ' '),
    count
  }));
}

const sampleTimeSeriesData = [
  { date: 'Mon', response_rate: 22 },
  { date: 'Tue', response_rate: 28 },
  { date: 'Wed', response_rate: 25 },
  { date: 'Thu', response_rate: 30 },
  { date: 'Fri', response_rate: 27 },
  { date: 'Sat', response_rate: 24 },
  { date: 'Sun', response_rate: 26 },
];
