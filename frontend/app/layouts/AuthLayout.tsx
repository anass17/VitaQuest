import React from "react";
import { Outlet } from "react-router";

export default function AuthLayout() {
  return (
    <div style={styles.viewPort}>
      {/* Decorative background elements */}
      <div style={styles.blob1}></div>
      <div style={styles.blob2}></div>

      <main style={styles.mainContent}>
        {/* This is where LoginForm.tsx will render */}
        <Outlet />
      </main>

      <footer style={styles.footer}>
        <p>&copy; {new Date().getFullYear()} VitaQuest AI • Secure RAG Intelligence</p>
      </footer>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  viewPort: {
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#f0f4f8", // Light slate
    position: "relative",
    overflow: "hidden",
    fontFamily: "Inter, system-ui, -apple-system, sans-serif",
  },
  mainContent: {
    position: "relative",
    zIndex: 2,
    width: "100%",
    display: "flex",
    justifyContent: "center",
    padding: "20px",
  },
  // Soft blue glow in the top-right
  blob1: {
    position: "absolute",
    top: "-10%",
    right: "-5%",
    width: "40vw",
    height: "40vw",
    background: "radial-gradient(circle, rgba(30, 144, 255, 0.08) 0%, transparent 70%)",
    borderRadius: "50%",
    zIndex: 1,
  },
  // Soft green glow in the bottom-left
  blob2: {
    position: "absolute",
    bottom: "-10%",
    left: "-5%",
    width: "40vw",
    height: "40vw",
    background: "radial-gradient(circle, rgba(16, 185, 129, 0.08) 0%, transparent 70%)",
    borderRadius: "50%",
    zIndex: 1,
  },
  footer: {
    position: "absolute",
    bottom: "20px",
    fontSize: "12px",
    color: "#94a3b8",
    zIndex: 2,
  },
};