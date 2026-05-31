"use client";

import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { Bot, User } from "lucide-react";
import { cn } from "@/utils/cn";
import { formatDateTime } from "@/utils/formatters";
import type { ChatMessage } from "@/types/dashboard.types";

interface MessageBubbleProps {
  message: ChatMessage;
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-1 py-1">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-2 h-2 rounded-full bg-slate-400"
          animate={{ y: [0, -4, 0] }}
          transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
        />
      ))}
    </div>
  );
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn("flex gap-3", isUser && "flex-row-reverse")}
    >
      {/* Avatar */}
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
        isUser
          ? "bg-blue-600"
          : "bg-gradient-to-br from-blue-500 to-purple-600"
      )}>
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>

      {/* Content */}
      <div className={cn("flex-1 max-w-[85%]", isUser && "flex flex-col items-end")}>
        <div className={cn(
          "rounded-xl px-4 py-3",
          isUser
            ? "bg-blue-600 text-white"
            : "bg-slate-700/60 border border-slate-600/50"
        )}>
          {message.isStreaming && !message.content ? (
            <TypingIndicator />
          ) : isUser ? (
            <p className="text-sm">{message.content}</p>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="text-sm text-slate-100 mb-2 last:mb-0 leading-relaxed">{children}</p>,
                  strong: ({ children }) => <strong className="text-white font-semibold">{children}</strong>,
                  ul: ({ children }) => <ul className="text-sm text-slate-200 space-y-1 my-2 list-disc list-inside">{children}</ul>,
                  ol: ({ children }) => <ol className="text-sm text-slate-200 space-y-1 my-2 list-decimal list-inside">{children}</ol>,
                  li: ({ children }) => <li className="text-slate-200">{children}</li>,
                  h1: ({ children }) => <h1 className="text-base font-bold text-white mb-2">{children}</h1>,
                  h2: ({ children }) => <h2 className="text-sm font-bold text-white mb-2">{children}</h2>,
                  h3: ({ children }) => <h3 className="text-sm font-semibold text-white mb-1">{children}</h3>,
                  code: ({ children }) => <code className="bg-slate-800 text-blue-300 px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>,
                  table: ({ children }) => (
                    <div className="overflow-x-auto my-3">
                      <table className="min-w-full text-xs border border-slate-600 rounded-lg overflow-hidden">
                        {children}
                      </table>
                    </div>
                  ),
                  th: ({ children }) => <th className="bg-slate-700 text-slate-300 px-3 py-1.5 text-left font-medium">{children}</th>,
                  td: ({ children }) => <td className="border-t border-slate-600/50 px-3 py-1.5 text-slate-200">{children}</td>,
                  blockquote: ({ children }) => <blockquote className="border-l-2 border-blue-500 pl-3 text-slate-300 italic my-2">{children}</blockquote>,
                }}
              >
                {message.content}
              </ReactMarkdown>
              {message.isStreaming && <TypingIndicator />}
            </div>
          )}
        </div>
        <p className="text-[10px] text-slate-500 mt-1 px-1">
          {formatDateTime(message.timestamp)}
        </p>
      </div>
    </motion.div>
  );
}
