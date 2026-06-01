import api from "./api";
import type { ChatMessage } from "@/types/dashboard.types";

const DEMO_RESPONSES: Record<string, string> = {
  default: `Based on the current data analysis, here are the key insights:

**Revenue Performance**
- Total revenue is tracking at **$4.82M** this month, up **12.4%** vs prior month
- New York HQ and Chicago branches are outperforming targets significantly
- Enterprise Suite Pro remains the top revenue driver at $924K

**Areas of Concern**
- Singapore branch is 6.8% below target for the 3rd consecutive month
- 7 critical/warning inventory alerts require immediate attention
- SSD-512E and RAM-32G face stockout within 3-5 days

**Recommended Actions**
1. Expedite inventory reorders for critical SKUs to prevent ~$234K in lost revenue
2. Schedule review with Singapore regional manager regarding Q2 strategy
3. Consider increasing ML Pipeline product marketing — 34.5% growth indicates strong demand

Would you like me to drill deeper into any of these areas?`,

  revenue: `**Revenue Analysis — Current Period**

Your revenue is showing strong momentum:

| Metric | Value | vs. Prior Period |
|--------|-------|------------------|
| Total Revenue | $4.82M | +12.4% |
| Best Branch | New York | +15.2% |
| Top Product | Enterprise Suite | +18.2% |

**Revenue Drivers:**
- Enterprise software sales accelerated in the last 2 weeks
- New York and Chicago are pulling the overall average up
- Product mix has shifted toward higher-margin software (44% of revenue)

The Q4 forecast based on current trajectory is **$5.8M**, which is 8.2% above target.`,

  inventory: `**Inventory Health Report**

Current inventory status requires immediate executive attention:

\u{1F534} **Critical (Action Required Today)**
- SSD-512E: 12 units remaining (3 days to stockout) — Potential revenue impact: $89K
- RAM-32G: 28 units (5 days) — Potential revenue impact: $67K
- 2 SKUs already out of stock

\u{1F7E1} **Warning (Action Required This Week)**
- Network Switch 48-Port: 9 days remaining
- UPS 2000VA: 14 days remaining
- Server GPU A100: 21 days remaining

**Recommendation:** Issue emergency POs for critical items today. Estimated total reorder value: $487,000.`,

  forecast: `**Revenue Forecast — Next 90 Days**

Based on ML model analysis (R² = 0.94, MAPE = 3.2%):

- **30-day forecast:** $5.1M (confidence: 94%)
- **60-day forecast:** $5.4M (confidence: 88%)
- **90-day forecast:** $5.8M (confidence: 82%)

**Key Assumptions:**
- Current growth trajectory continues
- No major supply chain disruptions
- Seasonal Q4 uplift factor of +8.5%

**Risk Factors:**
- Singapore underperformance could reduce forecast by $180K
- Inventory stockouts may cause $234K+ in lost revenue if not addressed`,
};

function getMockResponse(query: string): string {
  const lower = query.toLowerCase();
  if (lower.includes("revenue") || lower.includes("sales") || lower.includes("growth")) {
    return DEMO_RESPONSES.revenue;
  }
  if (lower.includes("inventory") || lower.includes("stock") || lower.includes("alert")) {
    return DEMO_RESPONSES.inventory;
  }
  if (lower.includes("forecast") || lower.includes("predict") || lower.includes("q4") || lower.includes("quarter")) {
    return DEMO_RESPONSES.forecast;
  }
  return DEMO_RESPONSES.default;
}

export const aiService = {
  async sendMessage(
    message: string,
    history: ChatMessage[],
    onChunk?: (chunk: string) => void
  ): Promise<string> {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/ai/chat/stream`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${typeof window !== "undefined" ? localStorage.getItem("access_token") : ""}`,
          },
          body: JSON.stringify({
            message,
            history: history.map((m) => ({ role: m.role, content: m.content })),
          }),
        }
      );

      if (!response.ok) throw new Error("Stream request failed");
      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let fullText = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") break;
            try {
              const parsed = JSON.parse(data);
              const text = parsed.content || parsed.text || parsed.delta || "";
              fullText += text;
              onChunk?.(text);
            } catch {
              fullText += data;
              onChunk?.(data);
            }
          }
        }
      }

      return fullText;
    } catch {
      // Demo: simulate streaming with mock response
      const mockResponse = getMockResponse(message);
      if (onChunk) {
        const words = mockResponse.split(" ");
        for (let i = 0; i < words.length; i++) {
          await new Promise((resolve) => setTimeout(resolve, 30 + Math.random() * 40));
          onChunk(words[i] + (i < words.length - 1 ? " " : ""));
        }
      }
      return mockResponse;
    }
  },

  async getInsights() {
    try {
      const response = await api.get("/ai/insights");
      return response.data;
    } catch {
      return [];
    }
  },
};
