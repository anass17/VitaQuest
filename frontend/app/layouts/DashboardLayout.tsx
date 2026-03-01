import React, { useState } from "react";
import { Outlet, Link, useLocation } from "react-router";

export default function DashboardLayout() {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();

  const menuItems = [
    { name: "New Chat", path: "/chat", icon: "＋" },
    { name: "My Documents", path: "/documents", icon: "📂" },
    { name: "Search History", path: "/history", icon: "🕒" },
    { name: "Settings", path: "/settings", icon: "⚙️" },
  ];

  return (
    <div className="flex h-screen bg-white text-slate-900 overflow-hidden font-sans">

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col relative overflow-hidden bg-white">
        {/* This is where ChatInterface.tsx will render */}
        <Outlet />
      </main>
    </div>
  );
}