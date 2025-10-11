"use client";

import React, { useState } from "react";
import { Send, Loader2, BookOpen, Github, ExternalLink } from "lucide-react";

export default function SimpleChatPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Array<{
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
  }>>([]);
  const [isLoading, setIsLoading] = useState(false);

  const exampleQuestions = [
    "What should you do if the 'Braking Power Low' message appears?",
    "What does the PCS warning light indicate?",
    "What does the tire pressure warning light mean?",
    "How do you activate the parking brake?",
  ];

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    
    // Add user message
    setMessages(prev => [...prev, {
      role: "user",
      content: userMessage,
      timestamp: new Date()
    }]);

    setIsLoading(true);

    try {
      // Call our API route (which calls HuggingFace)
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      // Add assistant message
      setMessages(prev => [...prev, {
        role: "assistant",
        content: data.answer || "I couldn't find an answer to that question.",
        timestamp: new Date()
      }]);

    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (question: string) => {
    setInput(question);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-blue-500 p-2 rounded-lg">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">ManualAi</h1>
                <p className="text-sm text-slate-400">64% accuracy | 800% improvement</p>
              </div>
            </div>
            <div className="flex gap-3">
              <a
                href="https://github.com/agapemiteu/ManualAi"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
              >
                <Github className="w-4 h-4" />
                <span className="hidden sm:inline">GitHub</span>
              </a>
              <a
                href="https://agapemiteu.github.io/ManualAi/"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                <span className="hidden sm:inline">Portfolio</span>
              </a>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Welcome Message */}
        {messages.length === 0 && (
          <div className="text-center mb-8 space-y-6">
            <div className="inline-block p-4 bg-blue-500/10 rounded-full">
              <BookOpen className="w-16 h-16 text-blue-400" />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">
                Ask me anything about your Toyota 4Runner
              </h2>
              <p className="text-slate-400 text-lg">
                Intelligent Q&A system powered by hybrid retrieval + cross-encoder reranking
              </p>
            </div>

            {/* Example Questions */}
            <div className="grid sm:grid-cols-2 gap-3 mt-8">
              {exampleQuestions.map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => handleExampleClick(question)}
                  className="p-4 bg-slate-800/50 hover:bg-slate-800 border border-slate-700 rounded-lg text-left text-sm text-slate-300 hover:text-white transition-all hover:border-blue-500"
                >
                  <span className="text-blue-400 mr-2">💬</span>
                  {question}
                </button>
              ))}
            </div>

            {/* Stats */}
            <div className="flex justify-center gap-8 mt-8 text-sm">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">64%</div>
                <div className="text-slate-400">Accuracy (±2 pages)</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">+56pp</div>
                <div className="text-slate-400">Improvement</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">11</div>
                <div className="text-slate-400">Experiments</div>
              </div>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="space-y-4 mb-4">
          {messages.map((message, idx) => (
            <div
              key={idx}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  message.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-800 text-slate-100 border border-slate-700"
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                <p className="text-xs mt-2 opacity-70">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="sticky bottom-0 bg-slate-900/95 backdrop-blur-sm border-t border-slate-700 pt-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder="Ask a question about your car manual..."
              disabled={isLoading}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg transition-colors flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="text-xs text-slate-500 mt-2 text-center">
            Powered by HuggingFace Spaces • Deployed on Vercel
          </p>
        </div>
      </div>
    </div>
  );
}
