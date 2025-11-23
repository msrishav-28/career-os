'use client';

import { useState, useEffect } from 'react';
import { messagesAPI, contactsAPI, opportunitiesAPI } from '@/lib/api-client';
import { Users, Mail, Briefcase, TrendingUp, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalContacts: 0,
    pendingMessages: 0,
    topOpportunities: 0,
    responseRate: 0,
  });
  const [loading, setLoading] = useState(true);

  const userId = 'demo-user'; // In production, get from auth

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load contacts
      const contactsRes = await contactsAPI.list(userId);
      const contacts = contactsRes.data.contacts || [];
      
      // Load messages
      const messagesRes = await messagesAPI.list(userId, { status: 'draft' });
      const pendingMessages = messagesRes.data.messages || [];
      
      // Load opportunities
      const oppsRes = await opportunitiesAPI.getTop(userId, 10);
      const opportunities = oppsRes.data.opportunities || [];
      
      setStats({
        totalContacts: contacts.length,
        pendingMessages: pendingMessages.length,
        topOpportunities: opportunities.length,
        responseRate: 25, // Calculate from actual data
      });
      
    } catch (error) {
      console.error('Error loading dashboard:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">CareerOS Dashboard</h1>
            <div className="flex gap-4">
              <button className="px-4 py-2 text-gray-600 hover:text-gray-900">Settings</button>
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                New Campaign
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<Users className="w-6 h-6" />}
            label="Total Contacts"
            value={stats.totalContacts}
            color="blue"
            href="/dashboard/contacts"
          />
          <StatCard
            icon={<Mail className="w-6 h-6" />}
            label="Pending Approval"
            value={stats.pendingMessages}
            color="purple"
            href="/dashboard/messages"
          />
          <StatCard
            icon={<Briefcase className="w-6 h-6" />}
            label="Top Opportunities"
            value={stats.topOpportunities}
            color="green"
            href="/dashboard/opportunities"
          />
          <StatCard
            icon={<TrendingUp className="w-6 h-6" />}
            label="Response Rate"
            value={`${stats.responseRate}%`}
            color="orange"
          />
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Activity Feed */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
            <div className="space-y-4">
              <ActivityItem
                type="opportunity"
                message="New opportunity: AI/ML Internship at Google"
                time="2 hours ago"
              />
              <ActivityItem
                type="message"
                message="3 new draft messages ready for approval"
                time="5 hours ago"
              />
              <ActivityItem
                type="response"
                message="John Smith responded to your message"
                time="1 day ago"
              />
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <QuickActionButton
                label="Discover Opportunities"
                href="/dashboard/opportunities"
              />
              <QuickActionButton
                label="Approve Messages"
                href="/dashboard/messages"
              />
              <QuickActionButton
                label="Update Profile"
                href="/dashboard/profile"
              />
              <QuickActionButton
                label="View Analytics"
                href="/dashboard/analytics"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color, href }: any) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    purple: 'bg-purple-50 text-purple-600',
    green: 'bg-green-50 text-green-600',
    orange: 'bg-orange-50 text-orange-600',
  };

  const content = (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
      <div className={`inline-flex p-3 rounded-lg ${colorClasses[color]} mb-4`}>
        {icon}
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-gray-600">{label}</div>
    </div>
  );

  return href ? <Link href={href}>{content}</Link> : content;
}

function ActivityItem({ type, message, time }: any) {
  return (
    <div className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg">
      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2"></div>
      <div className="flex-1">
        <p className="text-gray-900">{message}</p>
        <p className="text-sm text-gray-500">{time}</p>
      </div>
    </div>
  );
}

function QuickActionButton({ label, href }: any) {
  return (
    <Link href={href}>
      <button className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition">
        <span className="font-medium text-gray-900">{label}</span>
        <ArrowRight className="w-4 h-4 text-gray-400" />
      </button>
    </Link>
  );
}
