"use client";

import { motion } from "framer-motion";
import { SUGGESTED_QUERIES } from "@/utils/constants";

interface SuggestedQueriesProps {
  onSelect: (query: string) => void;
  disabled?: boolean;
}

export function SuggestedQueries({ onSelect, disabled }: SuggestedQueriesProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {SUGGESTED_QUERIES.map((query, i) => (
        <motion.button
          key={query}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.05 }}
          onClick={() => !disabled && onSelect(query)}
          disabled={disabled}
          className="text-xs px-3 py-1.5 rounded-full border border-slate-600 bg-slate-700/30 text-slate-300 hover:bg-slate-700 hover:text-white hover:border-slate-500 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {query}
        </motion.button>
      ))}
    </div>
  );
}
