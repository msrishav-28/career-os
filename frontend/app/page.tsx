'use client';

import Link from 'next/link';
import { ArrowRight, Sparkles, Target, Users, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center max-w-4xl mx-auto"
        >
          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6">
            Your AI Co-Pilot for
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {' '}Career Growth
            </span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Automate networking, outreach, and opportunity discovery while staying authentic.
            Let AI handle the repetitive tasks while you focus on meaningful conversations.
          </p>

          <div className="flex gap-4 justify-center">
            <Link href="/dashboard">
              <button className="px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition flex items-center gap-2">
                Get Started
                <ArrowRight className="w-5 h-5" />
              </button>
            </Link>
            <button className="px-8 py-4 border-2 border-gray-300 rounded-lg font-semibold hover:border-gray-400 transition">
              Watch Demo
            </button>
          </div>
        </motion.div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-24">
          <FeatureCard
            icon={<Sparkles className="w-8 h-8 text-blue-600" />}
            title="AI-Powered Outreach"
            description="Generate personalized messages that score 70+ on quality. Reference specific work and demonstrate genuine interest."
          />
          <FeatureCard
            icon={<Target className="w-8 h-8 text-purple-600" />}
            title="Smart Opportunity Discovery"
            description="Find relevant jobs, internships, and connections daily. Match scores help you focus on what matters."
          />
          <FeatureCard
            icon={<Users className="w-8 h-8 text-green-600" />}
            title="CRM & Relationship Management"
            description="Track every contact through the pipeline. Never miss a follow-up or lose momentum."
          />
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mt-24 bg-white rounded-2xl p-8 shadow-xl">
          <StatCard number="20-30%" label="Response Rate" />
          <StatCard number="15-20" label="Outreach/Day" />
          <StatCard number="0" label="Platform Violations" />
          <StatCard number="10+" label="Hours Saved/Week" />
        </div>

        {/* CTA */}
        <div className="mt-24 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-center text-white">
          <h2 className="text-4xl font-bold mb-4">Ready to accelerate your career?</h2>
          <p className="text-xl mb-8 opacity-90">Join ambitious professionals using AI to achieve their goals faster.</p>
          <Link href="/dashboard">
            <button className="px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100 transition">
              Start Your Journey
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition"
    >
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </motion.div>
  );
}

function StatCard({ number, label }: { number: string; label: string }) {
  return (
    <div className="text-center">
      <div className="text-4xl font-bold text-blue-600 mb-2">{number}</div>
      <div className="text-gray-600">{label}</div>
    </div>
  );
}
