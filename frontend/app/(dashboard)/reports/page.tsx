"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Download, RefreshCw, Clock, CheckCircle, AlertCircle, Plus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { formatRelativeTime } from "@/utils/formatters";
import { cn } from "@/utils/cn";

interface Report {
  id: string;
  name: string;
  type: string;
  status: "completed" | "generating" | "scheduled" | "failed";
  size?: string;
  generatedAt?: string;
  scheduledAt?: string;
  period: string;
}

const INITIAL_REPORTS: Report[] = [
  { id: "r1", name: "Executive Monthly Summary", type: "Executive", status: "completed", size: "2.4 MB", generatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), period: "May 2025" },
  { id: "r2", name: "Sales Performance Report", type: "Sales", status: "completed", size: "1.8 MB", generatedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), period: "May 2025" },
  { id: "r3", name: "Inventory Status Report", type: "Inventory", status: "completed", size: "3.1 MB", generatedAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), period: "Week 21, 2025" },
  { id: "r4", name: "Revenue Forecast Q3", type: "Forecast", status: "completed", size: "985 KB", generatedAt: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(), period: "Q3 2025" },
  { id: "r5", name: "Branch Comparison Analysis", type: "Analytics", status: "generating", period: "May 2025" },
  { id: "r6", name: "Weekly KPI Digest", type: "Executive", status: "scheduled", scheduledAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), period: "Week 22, 2025" },
  { id: "r7", name: "Supplier Performance", type: "Inventory", status: "failed", period: "April 2025" },
];

const REPORT_TEMPLATES = [
  { name: "Executive Dashboard Summary", description: "High-level KPIs, revenue, and strategic alerts", type: "Executive", icon: "📊" },
  { name: "Sales Analytics Report", description: "Detailed revenue, product, and branch performance", type: "Sales", icon: "💰" },
  { name: "Inventory Management Report", description: "Stock levels, alerts, and turnover analysis", type: "Inventory", icon: "📦" },
  { name: "Revenue Forecast Report", description: "AI-powered predictions with confidence intervals", type: "Forecast", icon: "🔮" },
  { name: "Custom Analysis", description: "Build a custom report with selected metrics", type: "Custom", icon: "⚙️" },
];

const STATUS_CONFIG = {
  completed: { color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20", label: "Completed", icon: CheckCircle },
  generating: { color: "text-blue-400 bg-blue-400/10 border-blue-400/20", label: "Generating", icon: RefreshCw },
  scheduled: { color: "text-amber-400 bg-amber-400/10 border-amber-400/20", label: "Scheduled", icon: Clock },
  failed: { color: "text-red-400 bg-red-400/10 border-red-400/20", label: "Failed", icon: AlertCircle },
};

const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.07 } } };
const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } };

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>(INITIAL_REPORTS);

  const handleGenerate = (templateName: string, type: string) => {
    const newReport: Report = {
      id: `r${Date.now()}`,
      name: templateName,
      type,
      status: "generating",
      period: new Date().toLocaleDateString("en-US", { month: "long", year: "numeric" }),
    };
    setReports((prev) => [newReport, ...prev]);
    toast.success("Report generation started");

    setTimeout(() => {
      setReports((prev) =>
        prev.map((r) =>
          r.id === newReport.id
            ? { ...r, status: "completed" as const, size: `${(Math.random() * 3 + 0.5).toFixed(1)} MB`, generatedAt: new Date().toISOString() }
            : r
        )
      );
      toast.success(`${templateName} is ready for download`);
    }, 3000);
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Stats */}
      <motion.div variants={item} className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Total Reports", value: reports.length, color: "text-blue-400" },
          { label: "Completed", value: reports.filter((r) => r.status === "completed").length, color: "text-emerald-400" },
          { label: "In Progress", value: reports.filter((r) => r.status === "generating").length, color: "text-amber-400" },
          { label: "Scheduled", value: reports.filter((r) => r.status === "scheduled").length, color: "text-purple-400" },
        ].map((stat) => (
          <Card key={stat.label}>
            <CardContent className="p-4">
              <p className="text-xs text-slate-400 mb-1">{stat.label}</p>
              <p className={cn("text-2xl font-bold", stat.color)}>{stat.value}</p>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {/* Generate New Report */}
      <motion.div variants={item}>
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Plus className="w-5 h-5 text-blue-400" />
              <div>
                <CardTitle>Generate New Report</CardTitle>
                <CardDescription>Choose a template to create a new report</CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {REPORT_TEMPLATES.map((template) => (
                <button
                  key={template.name}
                  onClick={() => handleGenerate(template.name, template.type)}
                  className="flex flex-col items-start gap-2 p-4 rounded-lg border border-slate-700/50 bg-slate-700/20 hover:bg-slate-700/40 hover:border-slate-600 transition-all text-left group"
                >
                  <span className="text-2xl">{template.icon}</span>
                  <div>
                    <p className="text-sm font-medium text-white group-hover:text-blue-300 transition-colors">{template.name}</p>
                    <p className="text-xs text-slate-400 mt-0.5 leading-relaxed">{template.description}</p>
                  </div>
                  <Badge variant="secondary" className="text-[10px]">{template.type}</Badge>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Reports List */}
      <motion.div variants={item}>
        <Card>
          <CardHeader>
            <CardTitle>Report History</CardTitle>
            <CardDescription>Previously generated and scheduled reports</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-slate-700/30">
              {reports.map((report) => {
                const statusConfig = STATUS_CONFIG[report.status];
                const StatusIcon = statusConfig.icon;
                return (
                  <div key={report.id} className="flex items-center gap-4 px-6 py-4 hover:bg-slate-700/10 transition-colors">
                    <div className="w-10 h-10 rounded-lg bg-slate-700/50 flex items-center justify-center flex-shrink-0">
                      <FileText className="w-5 h-5 text-slate-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">{report.name}</p>
                      <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                        <Badge variant="secondary" className="text-[10px] py-0">{report.type}</Badge>
                        <span className="text-xs text-slate-500">{report.period}</span>
                        {report.generatedAt && (
                          <span className="text-xs text-slate-500">· {formatRelativeTime(report.generatedAt)}</span>
                        )}
                        {report.scheduledAt && (
                          <span className="text-xs text-slate-500">· Runs {formatRelativeTime(report.scheduledAt)}</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 flex-shrink-0">
                      {report.size && <span className="text-xs text-slate-500 hidden sm:block">{report.size}</span>}
                      <div className={cn("flex items-center gap-1.5 px-2 py-1 rounded-md border text-xs font-medium", statusConfig.color)}>
                        <StatusIcon className={cn("w-3.5 h-3.5", report.status === "generating" && "animate-spin")} />
                        {statusConfig.label}
                      </div>
                      {report.status === "completed" && (
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400" onClick={() => toast.success(`Downloading ${report.name}...`)}>
                          <Download className="w-4 h-4" />
                        </Button>
                      )}
                      {report.status === "failed" && (
                        <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400" onClick={() => toast.info("Retrying...")}>
                          <RefreshCw className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
