"use client";

import { useState, useRef, useEffect } from "react";
import { MessageSquare, Send, Sparkles, User, Bot, Loader2, AlertCircle } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface InlineProductChatProps {
  productName?: string;
  ingredients: string[];
  category?: string;
  claims?: any[];
}

export function InlineProductChat({
  productName = "Scanned Product",
  ingredients = [],
  category = "Packaged Food",
  claims = []
}: InlineProductChatProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: `Hello! I'm your **#LabelPadhegaIndia Product Safety Assistant**. Ask me anything about this **${productName}** — from diabetic sugar spikes and refined palm oil to pediatric azo dye risks and safe alternatives.`
    }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const suggestedPrompts = [
    "Is this safe for daily consumption?",
    "Why is maltodextrin bad for diabetics?",
    "Is this safe for young children?",
    "What whole-food alternative can I use?"
  ];

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async (textToSend?: string) => {
    const question = (textToSend || input).trim();
    if (!question || isLoading) return;

    const newMessages: Message[] = [...messages, { role: "user", content: question }];
    setMessages(newMessages);
    setInput("");
    setIsLoading(true);

    try {
      const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
      const res = await fetch(`${baseUrl}/chat/product-qa`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          product_name: productName,
          ingredients,
          category,
          claims
        })
      });

      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}`);
      }

      const data = await res.json();
      const answer = data.answer || data.content || data.response || "No response generated.";

      setMessages((prev) => [...prev, { role: "assistant", content: answer }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `⚠️ Sorry, couldn't fetch an answer right now (${err?.message || "Network error"}). Please ensure the LabelX backend is running.`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-line bg-paper p-6 shadow-sm space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-line pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent/10 text-accent font-bold">
            <MessageSquare className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-ink">In-Line Product Safety Q&A</h3>
              <span className="rounded-full bg-accent/10 px-2 py-0.5 text-[10px] font-semibold text-accent flex items-center gap-1">
                <Sparkles className="h-3 w-3" /> Context-Aware Agent
              </span>
            </div>
            <p className="text-xs text-inksoft">
              Grounded strictly in this product&apos;s verified ingredient monograph and clinical contraindications.
            </p>
          </div>
        </div>
      </div>

      {/* Suggested Prompts */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-[11px] font-bold text-inksoft">Quick Prompts:</span>
        {suggestedPrompts.map((prompt, idx) => (
          <button
            key={idx}
            type="button"
            disabled={isLoading}
            onClick={() => handleSend(prompt)}
            className="text-xs px-2.5 py-1 rounded-full border border-line bg-surface hover:bg-surface/80 hover:border-accent text-ink transition-colors disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Chat Messages Scroll Window */}
      <div
        ref={scrollRef}
        className="h-[300px] overflow-y-auto rounded-xl border border-line/60 bg-surface/30 p-4 space-y-3"
      >
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start gap-2.5 ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {m.role === "assistant" && (
              <div className="h-7 w-7 rounded-full bg-accent/10 text-accent flex items-center justify-center shrink-0 mt-0.5">
                <Bot className="h-4 w-4" />
              </div>
            )}
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-xs leading-relaxed ${
                m.role === "user"
                  ? "bg-accent text-white rounded-br-none"
                  : "bg-paper border border-line text-ink rounded-bl-none shadow-xs"
              }`}
            >
              <div className="whitespace-pre-wrap">{m.content}</div>
            </div>
            {m.role === "user" && (
              <div className="h-7 w-7 rounded-full bg-ink/10 text-ink flex items-center justify-center shrink-0 mt-0.5">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-inksoft pl-9">
            <Loader2 className="h-3.5 w-3.5 animate-spin text-accent" />
            Analyzing ingredient monograph & clinical citations...
          </div>
        )}
      </div>

      {/* Input Field */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this food product..."
          disabled={isLoading}
          className="flex-1 rounded-xl border border-line bg-paper px-4 py-2.5 text-xs text-ink placeholder:text-inksoft/60 focus:outline-none focus:ring-1 focus:ring-accent disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent text-white hover:bg-accent/90 disabled:opacity-40 transition-opacity"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
