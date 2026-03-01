import React, { useState } from "react";
import { Form, Link, useNavigate } from "react-router";

const API_URL = import.meta.env.REACT_APP_API_URL || "http://localhost:8000";

export default function LoginForm() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [status, setStatus] = useState<{type: string | null, message: string}>({
    type: null,
    message: ""
  })



  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  

  const submitForm = async (e: React.FormEvent) => {
    e.preventDefault();

    if (loading == true) {
        return
    }

    setLoading(true)

    const request = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
         "content-type": "application/json"
      },
      body: JSON.stringify(formData)
    })

    const response = await request.json()

    if (request.status == 200) {

      setStatus({
        type: "success",
        message: "Logged in successfully!"
      })

      localStorage.setItem("access_token", response.access_token);
      localStorage.setItem("first_name", response.first_name);
      localStorage.setItem("last_name", response.last_name);
      localStorage.setItem("role", response.role);

      setTimeout(() => {
        navigate("/dashboard");
      }, 2000)

    } else if (request.status == 401) {

      setStatus({
        type: "error",
        message: response.detail
      })

    } else {

      setStatus({
        type: "error",
        message: "You have errors in your form"
      })

    }
      
    setLoading(false)
  };




  // Custom SVGs
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
    <div className="w-full max-w-lg p-10 bg-white rounded-[20px] shadow-xl border border-slate-100">
      <div className="flex flex-col items-center gap-2 mb-8 text-center">
        <QuestLogo />
        <h1 className="text-2xl font-bold text-slate-800 tracking-tight">VitaQuest</h1>
        <p className="text-sm text-slate-500">Enter your credentials to continue</p>
      </div>

      <form method="post" className="flex flex-col gap-5" onSubmit={submitForm}>
        <div className="flex flex-col gap-1.5">
          <label htmlFor="email" className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
            Email Address
          </label>
          <input
            type="email"
            id="email"
            name="email"
            placeholder="name@example.com"
            required
            autoComplete="email"
            className="w-full px-4 py-3 rounded-xl border border-slate-200 text-slate-900 placeholder-slate-400 focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all"
            onChange={handleChange}
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="password" className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
            Password
          </label>
          <div className="relative flex items-center">
            <input
              type={showPassword ? "text" : "password"}
              id="password"
              name="password"
              placeholder="••••••••"
              required
              autoComplete="current-password"
              className="w-full pl-4 pr-12 py-3 rounded-xl border border-slate-200 text-slate-900 placeholder-slate-400 focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all"
              onChange={handleChange}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 p-2 text-slate-400 hover:text-slate-600 transition-colors"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOffIcon /> : <EyeIcon />}
            </button>
          </div>
        </div>

        {
          loading ? (
            <button
              className="mt-2 w-full py-3.5 bg-slate-100 text-slate-500 font-bold rounded-xl"
            >
              Loading ...
            </button>

          ) : (
            <button
              type="submit"
              className="mt-2 w-full py-3.5 bg-emerald-500 hover:bg-emerald-600 cursor-pointer text-white font-bold rounded-xl shadow-lg shadow-emerald-200 transition-all active:scale-[0.98]"
            >
              Sign In
            </button>

          )
        }

      </form>

      <div className="mt-8 text-center text-sm text-slate-500">
        <span>Don't have an account? </span>
        <Link to="/signup" className="text-emerald-500 font-bold hover:underline transition-all">
          Sign up
        </Link>
      </div>
    </div>
  );
}