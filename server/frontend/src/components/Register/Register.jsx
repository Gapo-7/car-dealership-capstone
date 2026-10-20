import React, { useState } from "react";
import Header from "../Header/Header";
import "./Register.css";

const initialForm = { userName: "", firstName: "", lastName: "", email: "", password: "" };

export default function Register() {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const update = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const register = async (event) => {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      const response = await fetch("/djangoapp/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const result = await response.json();
      if (!response.ok || result.status !== "Authenticated") {
        throw new Error(result.error || "Registration failed. Please check your details.");
      }
      sessionStorage.setItem("username", result.userName);
      sessionStorage.setItem("firstname", result.firstName);
      sessionStorage.setItem("lastname", result.lastName);
      window.location.assign("/dealers");
    } catch (cause) {
      setError(cause.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <Header />
      <main className="register_panel">
        <h1>Sign up</h1>
        <p>Create an account to review a dealership.</p>
        <form onSubmit={register}>
          <label htmlFor="userName">Username</label>
          <input id="userName" name="userName" value={form.userName} onChange={update} required autoComplete="username" />
          <label htmlFor="firstName">First Name</label>
          <input id="firstName" name="firstName" value={form.firstName} onChange={update} required autoComplete="given-name" />
          <label htmlFor="lastName">Last Name</label>
          <input id="lastName" name="lastName" value={form.lastName} onChange={update} required autoComplete="family-name" />
          <label htmlFor="email">Email</label>
          <input id="email" name="email" type="email" value={form.email} onChange={update} required autoComplete="email" />
          <label htmlFor="password">Password</label>
          <input id="password" name="password" type="password" value={form.password} onChange={update} required minLength="8" autoComplete="new-password" />
          {error && <p role="alert">{error}</p>}
          <button type="submit" disabled={busy}>{busy ? "Registering…" : "Register"}</button>
        </form>
      </main>
    </div>
  );
}
