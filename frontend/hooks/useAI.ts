"use client";

import { useState, useCallback, useRef } from "react";
import { aiService } from "@/services/ai.service";
import type { ChatMessage } from "@/types/dashboard.types";

export function useAI() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hello! I'm your ExecutiveAI assistant. I have access to your real-time business data including revenue, inventory, sales performance, and forecasts. What would you like to know?",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [isStreaming, setIsStreaming] = useState(false);
  const streamingMessageRef = useRef<string>("");

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isStreaming) return;

    const userMessage: ChatMessage = {
      id: `msg_${Date.now()}_user`,
      role: "user",
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };

    const assistantMessageId = `msg_${Date.now()}_assistant`;
    const assistantMessage: ChatMessage = {
      id: assistantMessageId,
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setIsStreaming(true);
    streamingMessageRef.current = "";

    try {
      await aiService.sendMessage(
        content,
        messages,
        (chunk: string) => {
          streamingMessageRef.current += chunk;
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMessageId
                ? { ...m, content: streamingMessageRef.current }
                : m
            )
          );
        }
      );

      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMessageId
            ? { ...m, isStreaming: false }
            : m
        )
      );
    } catch (error) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMessageId
            ? { ...m, content: "I encountered an error processing your request. Please try again.", isStreaming: false }
            : m
        )
      );
    } finally {
      setIsStreaming(false);
      streamingMessageRef.current = "";
    }
  }, [messages, isStreaming]);

  const clearMessages = useCallback(() => {
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content: "Hello! I'm your ExecutiveAI assistant. How can I help you today?",
        timestamp: new Date().toISOString(),
      },
    ]);
  }, []);

  return {
    messages,
    isStreaming,
    sendMessage,
    clearMessages,
  };
}
