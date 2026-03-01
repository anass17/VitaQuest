import React, { useState } from "react";
import { Link, useNavigate } from "react-router";


const API_URL = import.meta.env.REACT_APP_API_URL || "http://localhost:8000";


export default function RegisterForm() {
  const [showPassword, setShowPassword] = useState(false);
  
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
  });
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState<{type: string | null, message: string}>({
    type: null,
    message: ""
  })


  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setFormData({ ...formData, [e.target.name]: e.target.value });
    };



  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setLoading(true)

    const request = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
         "content-type": "application/json"
      },
      body: JSON.stringify(formData)
    })

    const response = await request.json()

    if (request.status == 201) {

      setStatus({
        type: "success",
        message: "Registered successfully!"
      })

      localStorage.setItem("access_token", response.access_token);
      localStorage.setItem("first_name", response.first_name);
      localStorage.setItem("last_name", response.last_name);
      localStorage.setItem("role", response.role);

      setTimeout(() => {
        navigate("/dashboard");
      }, 2000)

    } else {

      setStatus({
        type: "error",
        message: response.detail
      })

    }
      
    setLoading(false)

  };


  const EyeIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
  );

  const EyeOffIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
  );

  const QuestLogo = () => (
    <svg width="42" height="42" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
  );

  return (
    <div className="w-full max-w-lg p-10 py-8 mb-10 bg-white rounded-[24px] shadow-xl border border-slate-100">
      <div className="flex flex-col items-center gap-2 mb-8 text-center">
        <QuestLogo />
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">Create Account</h1>
        <p className="text-sm text-slate-500">Join VitaQuest to start your data exploration</p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        
        {/* Row for First and Last Name */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-600 uppercase tracking-wider">First Name</label>
            <input
              name="first_name"
              type="text"
              placeholder="New"
              required
              className="w-full px-4 py-3 rounded-xl border border-slate-200 placeholder-slate-400 outline-none focus:ring-1 focus:ring-dodgerblue-500 transition-all text-slate-900"
              onChange={handleChange}
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Last Name</label>
            <input
              name="last_name"
              type="text"
              placeholder="User"
              required
              className="w-full px-4 py-3 rounded-xl border border-slate-200 placeholder-slate-400 outline-none focus:ring-1 focus:ring-dodgerblue-500 transition-all text-slate-900"
              onChange={handleChange}
            />
          </div>
        </div>

        {/* Email Input */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Email Address</label>
          <input
            name="email"
            type="email"
            placeholder="jane@example.com"
            required
            className="w-full px-4 py-3 rounded-xl border border-slate-200 placeholder-slate-400 outline-none focus:ring-1 focus:ring-dodgerblue-500 transition-all text-slate-900"
            onChange={handleChange}
          />
        </div>

        {/* Password Input */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Password</label>
          <div className="relative flex items-center">
            <input
              name="password"
              type={showPassword ? "text" : "password"}
              placeholder="••••••••"
              required
              minLength={8}
              className="w-full pl-4 pr-12 py-3 rounded-xl border border-slate-200 placeholder-slate-400 outline-none focus:ring-1 focus:ring-dodgerblue-500 transition-all text-slate-900"
              onChange={handleChange}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 p-2 text-xs font-bold text-slate-400 hover:text-emerald-500 transition-colors"
            >
              {showPassword ? <EyeOffIcon /> : <EyeIcon />}
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="mt-2 w-full py-3.5 bg-emerald-500 cursor-pointer hover:bg-emerald-600 text-white font-bold rounded-xl shadow-lg shadow-emerald-100 disabled:opacity-50 transition-all active:scale-[0.98]"
        >
          {loading ? "Registering..." : "Create Account"}
        </button>
      </form>

      <div className="mt-8 text-center text-sm text-slate-500">
        <span>Already have an account? </span>
        <Link to="/login" className="text-emerald-500 font-bold">
          Sign In
        </Link>
      </div>
    </div>
  );
}