"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { User, Bell, Shield, Building2, Save } from "lucide-react";
import { toast } from "sonner";
import { useAuthStore } from "@/store/auth.store";

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user);
  const [notifications, setNotifications] = useState({
    email_alerts: true,
    inventory_warnings: true,
    weekly_reports: true,
    ai_insights: false,
  });

  const handleSave = () => {
    toast.success("Settings saved successfully");
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-slate-400 text-sm">Manage your account and platform preferences</p>
      </div>

      {[
        {
          icon: User, title: "Profile", color: "blue",
          content: (
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Full Name</label>
                <input defaultValue={user?.name || "CEO User"}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Email</label>
                <input defaultValue={user?.email || "ceo@acme.com"} type="email"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Role</label>
                <input defaultValue={user?.role || "CEO"} readOnly
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-400 text-sm cursor-not-allowed" />
              </div>
            </div>
          ),
        },
        {
          icon: Building2, title: "Company", color: "purple",
          content: (
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Company Name</label>
                <input defaultValue={user?.company || "Acme Corporation"}
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Plan</label>
                <div className="px-3 py-2 bg-blue-600/10 border border-blue-500/20 rounded-lg text-blue-400 text-sm font-medium">Enterprise</div>
              </div>
            </div>
          ),
        },
        {
          icon: Bell, title: "Notifications", color: "amber",
          content: (
            <div className="space-y-3">
              {Object.entries(notifications).map(([key, val]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-sm text-slate-300 capitalize">{key.replace(/_/g, " ")}</span>
                  <button
                    onClick={() => setNotifications((prev) => ({ ...prev, [key]: !val }))}
                    className={`relative w-10 h-5 rounded-full transition-colors ${val ? "bg-blue-600" : "bg-slate-700"}`}>
                    <span className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${val ? "translate-x-5" : "translate-x-0.5"}`} />
                  </button>
                </div>
              ))}
            </div>
          ),
        },
        {
          icon: Shield, title: "Security", color: "emerald",
          content: (
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Current Password</label>
                <input type="password" placeholder="••••••••"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">New Password</label>
                <input type="password" placeholder="••••••••"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
            </div>
          ),
        },
      ].map((section) => (
        <motion.div key={section.title} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
          className="bg-slate-900 border border-slate-700/50 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-4">
            <section.icon className="w-4 h-4 text-slate-400" />
            <h2 className="text-base font-semibold text-white">{section.title}</h2>
          </div>
          {section.content}
        </motion.div>
      ))}

      <button onClick={handleSave}
        className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg transition">
        <Save className="w-4 h-4" /> Save Changes
      </button>
    </div>
  );
}
