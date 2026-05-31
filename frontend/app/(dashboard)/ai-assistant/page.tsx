"use client";

import { motion } from "framer-motion";
import { ChatInterface } from "@/components/ai/ChatInterface";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bot, Zap, Shield, BarChart3 } from "lucide-react";

const CAPABILITIES = [
  {
    icon: BarChart3,
    title: "Real-time Analytics",
    description: "Access live revenue, sales, and inventory data through natural language queries",
    color: "text-blue-400 bg-blue-400/10",
  },
  {
    icon: Zap,
    title: "Instant Insights",
    description: "Get AI-generated insights about trends, anomalies, and opportunities",
    color: "text-amber-400 bg-amber-400/10",
  },
  {
    icon: Shield,
    title: "Enterprise Security",
    description: "All queries run within your secure environment. No data leaves your infrastructure",
    color: "text-emerald-400 bg-emerald-400/10",
  },
];

export default function AIAssistantPage() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full" style={{ minHeight: "calc(100vh - 130px)" }}>
      {/* Chat Interface */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
        className="lg:col-span-2"
        style={{ height: "calc(100vh - 130px)" }}
      >
        <ChatInterface />
      </motion.div>

      {/* Sidebar info */}
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
        className="space-y-4"
      >
        {/* About */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <CardTitle>About ExecutiveAI</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="text-sm text-slate-400 leading-relaxed">
            Your AI-powered executive assistant has direct access to your business data. Ask questions in plain English to get instant analysis, charts, and recommendations.
          </CardContent>
        </Card>

        {/* Capabilities */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle>Capabilities</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {CAPABILITIES.map((cap) => {
              const Icon = cap.icon;
              return (
                <div key={cap.title} className="flex gap-3">
                  <div className={`w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center ${cap.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white mb-0.5">{cap.title}</p>
                    <p className="text-xs text-slate-400 leading-relaxed">{cap.description}</p>
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>

        {/* Tips */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle>Pro Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-xs text-slate-400">
              <li className="flex gap-2">
                <span className="text-blue-400 font-bold">→</span>
                Ask about specific time periods: "last 30 days", "Q3 2025"
              </li>
              <li className="flex gap-2">
                <span className="text-blue-400 font-bold">→</span>
                Compare metrics: "How does NYC vs Chicago compare?"
              </li>
              <li className="flex gap-2">
                <span className="text-blue-400 font-bold">→</span>
                Request forecasts: "What will revenue be next quarter?"
              </li>
              <li className="flex gap-2">
                <span className="text-blue-400 font-bold">→</span>
                Diagnose issues: "Why is Singapore underperforming?"
              </li>
              <li className="flex gap-2">
                <span className="text-blue-400 font-bold">→</span>
                Get action items: "What should I prioritize today?"
              </li>
            </ul>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
