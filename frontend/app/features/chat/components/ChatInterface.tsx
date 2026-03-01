import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router";


const API_URL = import.meta.env.REACT_APP_API_URL || "http://localhost:8000";


interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export default function ChatInterface() {

    const navigate = useNavigate();

  const [fullName, setFullName] = useState("")
  const [messages, setMessages] = useState<Message[]>([
    { id: "1", role: "assistant", content: "Hello! I'm VitaQuest. How can I assist you today?" }
  ]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(false)

    useEffect(() => {
        try {
            let first_name = localStorage.getItem("first_name")
            let last_name = localStorage.getItem("last_name")

            setFullName(first_name + ' ' + last_name)
        } catch {}
    })

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (scrollRef.current) {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);


    const getQueries = async () => {
        const request = await fetch(`${API_URL}/rag/queries`, {
            method: 'GET',
            headers: {
                "content-type": "application/json",
                "Authorization": "Bearer " + localStorage.getItem("access_token")
            },
        })

        let response = await request.json()

        response.queries.forEach((item: any) => {
            const userMessage: Message = {
                id: Date.now().toString(),
                role: "user",
                content: item.query,
            };

            const assistantMessage: Message = {
                id: Date.now().toString(),
                role: "assistant",
                content: item.reponse,
            };

            setMessages((prev) => [...prev, userMessage, assistantMessage]);
        });
    }


    useEffect(() => {
        getQueries()
    }, []);



    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage: Message = {
            id: Date.now().toString(),
            role: "user",
            content: input,
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");

        setLoading(true)

        // Simulate RAG response
        
        const request = await fetch(`${API_URL}/rag/generate`, {
            method: 'POST',
            headers: {
                "content-type": "application/json",
                "Authorization": "Bearer " + localStorage.getItem("access_token")
            },
            body: JSON.stringify({
                "query": input
            })
        })

        let response = await request.json()


        setLoading(false)

        let botMessage : Message
        
        if (request.status == 200) {
            botMessage = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: response.answer,
            };
        } else {
            botMessage = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: "Error! Could not generate an answer",
            };
        }

        setMessages((prev) => [...prev, botMessage]);

    };



  return (
    <div className="flex flex-col h-screen bg-slate-50 rounded-md">
        {/* Header */}
        <header className="flex items-center justify-between px-8 py-4 bg-white border-b border-slate-200 shrink-0">
            {/* Left Side: Logo & Brand */}
            <div className="flex items-center gap-3">
                <div className="p-2 bg-emerald-100 rounded-lg">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                    </svg>
                </div>
                <h2 className="text-xl font-bold text-slate-800">
                    VitaQuest
                </h2>
            </div>

            {/* Right Side: User Info & Logout */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-3">
                    <span className="text-sm font-semibold text-slate-700">{fullName}</span>
                </div>

                {/* Small Vertical Separator */}
                <div className="h-4 w-[1px] bg-slate-300"></div>

                {/* Logout Button: Text only, no bg, no border */}
                <button 
                onClick={() => {
                    navigate("/logout");
                }}
                className="text-sm font-medium text-slate-500 hover:text-red-500 transition-colors cursor-pointer"
                >
                Logout
                </button>
            </div>
        </header>

      {/* Messages Area */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth"
      >
        <div className="max-w-3xl mx-auto w-full space-y-6">
            {messages.map((msg) => (
                <div 
                key={msg.id} 
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                    <div className={`max-w-[80%] px-5 py-3 rounded-2xl shadow-sm leading-relaxed ${
                        msg.role === "user" 
                        ? "bg-emerald-500 text-white rounded-tr-none" 
                        : "bg-white text-slate-700 border border-slate-200 rounded-tl-none"
                    }`}>
                        <p className="text-[15px]" style={{ whiteSpace: "pre-line" }}>{msg.content}</p>
                    </div>
                </div>
            ))}
            {
                loading && (
                    <div 
                        className={`flex justify-start`}
                    >
                        <div className={`max-w-[80%] px-5 py-3 rounded-2xl shadow-sm leading-relaxed 
                            : "bg-white text-slate-700 border border-slate-200 rounded-tl-none`}>
                            <p className="text-[15px]">Generating response ...</p>
                        </div>
                    </div>
                )
            }
        </div>
      </div>

      {/* Input Area */}
      <footer className="p-6 bg-white border-t border-slate-200 shrink-0">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSend} className="relative flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask VitaQuest ..."
              className="w-full pl-6 pr-16 py-4 bg-slate-100 border-none rounded-2xl focus:ring-1 focus:ring-emerald-500 outline-none text-slate-700 transition-all shadow-inner"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="absolute right-2 p-2.5 bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 disabled:opacity-50 disabled:hover:bg-emerald-500 transition-all shadow-md active:scale-95"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </form>
        </div>
      </footer>
    </div>
  );
}