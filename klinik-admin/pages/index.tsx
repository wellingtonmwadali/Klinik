import { useState } from "react";
import { useRouter } from "next/router";
import Head from "next/head";

const MODULES = [
  {
    tag: "AVAILABILITY",
    title: "Live 30-minute slots",
    desc: "Pick a doctor and a day to see every open slot, updated in real time.",
  },
  {
    tag: "BOOKING",
    title: "One booking, one slot",
    desc: "The moment it's booked, it's off the board — no double-booking, ever.",
  },
  {
    tag: "CANCELLATIONS",
    title: "Self-service cancellations",
    desc: "Patients cancel their own appointment and free the slot for someone else.",
  },
];

function PulseMark({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect x="0.5" y="0.5" width="31" height="31" rx="7.5" />
      <path
        d="M6 17h4l2.2-6 3.4 12 2.6-9.5L20 17h6"
        strokeWidth="1.75"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
}

function ChevronRight() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path
        d="M6 3.5L11 8l-5 4.5"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function VitalsLine({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 400 48"
      preserveAspectRatio="none"
      className={className}
      fill="none"
    >
      <path
        d="M0,26 L120,26 L136,10 L150,42 L166,4 L180,40 L196,26 L400,26"
        stroke="#2DD4BF"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        pathLength={1}
        className="vitals-path"
      />
    </svg>
  );
}

function Field({
  id,
  name,
  label,
  type = "text",
  placeholder,
  autoComplete,
  required = true,
}: {
  id: string;
  name: string;
  label: string;
  type?: string;
  placeholder?: string;
  autoComplete?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label
        htmlFor={id}
        className="mb-1.5 block text-[13px] font-medium text-[#344054]"
      >
        {label}
      </label>
      <input
        id={id}
        name={name}
        type={type}
        placeholder={placeholder}
        autoComplete={autoComplete}
        required={required}
        className="w-full rounded-lg border border-[#E4E7EB] bg-white px-3.5 py-3 text-[14.5px] text-[#101828] placeholder:text-[#B0B8C4] transition-colors focus:border-[#0D9488] focus:outline-none focus:ring-2 focus:ring-[#0D9488]/20"
      />
    </div>
  );
}

export default function Home() {
  const router = useRouter();
  const [tab, setTab] = useState<"login" | "register">("login");

  // --- Login state (wired to /api/auth/login) ---
  const [loginError, setLoginError] = useState<string>();
  const [loginPending, setLoginPending] = useState(false);

  async function handleLogin(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoginPending(true);
    setLoginError(undefined);

    const formData = new FormData(e.currentTarget);
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: formData.get("username"),
        password: formData.get("password"),
      }),
    });
    const body = await response.json().catch(() => null);

    if (!response.ok) {
      setLoginError(body?.error ?? "Login failed. Please try again.");
      setLoginPending(false);
      return;
    }

    router.push("/dashboard");
  }

  // --- Registration state (assumes /api/auth/register — see note below) ---
  const [registerError, setRegisterError] = useState<string>();
  const [registerPending, setRegisterPending] = useState(false);
  const [registerSuccess, setRegisterSuccess] = useState(false);

  async function handleRegister(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setRegisterError(undefined);

    const formData = new FormData(e.currentTarget);
    const password = formData.get("password");
    const confirmPassword = formData.get("confirmPassword");

    if (password !== confirmPassword) {
      setRegisterError("Passwords don't match.");
      return;
    }

    setRegisterPending(true);

    const response = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        first_name: formData.get("first_name"),
        last_name: formData.get("last_name"),
        email: formData.get("email"),
        phone: formData.get("phone"),
        password,
        confirm_password: confirmPassword,
      }),
    });
    const body = await response.json().catch(() => null);

    if (!response.ok) {
      setRegisterError(body?.error ?? "Registration failed. Please try again.");
      setRegisterPending(false);
      return;
    }

    setRegisterPending(false);
    setRegisterSuccess(true);
    setTab("login");
  }

  return (
    <>
      <Head>
        <title>Klinik — Book with your doctor</title>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap"
          rel="stylesheet"
        />
      </Head>

      <style jsx global>{`
        :root {
          --font-display: "Poppins", sans-serif;
          --font-body: "Inter", sans-serif;
          --font-mono: "IBM Plex Mono", monospace;
        }
        body {
          font-family: var(--font-body);
        }
        .vitals-path {
          stroke-dasharray: 1;
          stroke-dashoffset: 1;
          animation: draw-vitals 1.4s 0.2s cubic-bezier(0.4, 0, 0.2, 1)
            forwards;
        }
        @keyframes draw-vitals {
          to {
            stroke-dashoffset: 0;
          }
        }
        @media (prefers-reduced-motion: reduce) {
          .vitals-path {
            animation: none;
            stroke-dashoffset: 0;
          }
        }
      `}</style>

      <main
        className="min-h-screen bg-[#F6F7F5]"
        style={{ fontFamily: "var(--font-body)" }}
      >
        {/* Top bar */}
        <header className="flex items-center justify-between border-b border-[#E4E7EB] bg-white px-6 py-4 lg:px-12">
          <div className="flex items-center gap-2.5">
            <PulseMark className="h-8 w-8 text-[#0A1F33] [&>rect]:stroke-[#0A1F33] [&>path]:stroke-[#2DD4BF]" />
            <span
              className="text-[19px] font-semibold text-[#0A1F33]"
              style={{ fontFamily: "var(--font-display)" }}
            >
              Klinik
            </span>
          </div>
          <span
            className="hidden rounded-full border border-[#E4E7EB] px-3 py-1 text-[11px] font-medium uppercase tracking-[0.08em] text-[#64748B] sm:inline-block"
            style={{ fontFamily: "var(--font-mono)" }}
          >
            Online Appointment Booking
          </span>
        </header>

        <div className="grid min-h-[calc(100vh-65px)] lg:grid-cols-[1.1fr_1fr]">
          {/* LEFT — brand / product panel */}
          <div className="flex flex-col justify-center bg-[#0A1F33] px-8 py-16 sm:px-14 lg:px-16 lg:py-0">
            <div className="mx-auto w-full max-w-lg">
              <span
                className="text-[11px] font-medium uppercase tracking-[0.14em] text-[#2DD4BF]"
                style={{ fontFamily: "var(--font-mono)" }}
              >
                Appointment booking
              </span>

              <h1
                className="mt-4 text-[38px] font-semibold leading-[1.15] text-white sm:text-[44px]"
                style={{ fontFamily: "var(--font-display)" }}
              >
                See what's open. Book it in one tap.
              </h1>

              <p className="mt-5 max-w-md text-[15.5px] leading-relaxed text-[#A9B4C4]">
                Real-time availability across all 5 doctors, in 30-minute
                slots. Once a slot's booked it's gone from the board —
                and patients can cancel anytime to free it back up.
              </p>

              <VitalsLine className="mt-10 h-8 w-full" />

              <div className="mt-2 divide-y divide-[#1B3350]">
                {MODULES.map((m) => (
                  <div
                    key={m.tag}
                    className="group flex items-start justify-between gap-4 py-5"
                  >
                    <div>
                      <span
                        className="text-[11px] font-medium tracking-[0.1em] text-[#2DD4BF]"
                        style={{ fontFamily: "var(--font-mono)" }}
                      >
                        {m.tag}
                      </span>
                      <h3
                        className="mt-1.5 text-[16px] font-semibold text-white"
                        style={{ fontFamily: "var(--font-display)" }}
                      >
                        {m.title}
                      </h3>
                      <p className="mt-1 text-[13.5px] text-[#8592A6]">
                        {m.desc}
                      </p>
                    </div>
                    <ChevronRight />
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT — login / register panel */}
          <div className="flex items-center justify-center px-6 py-14 sm:px-10">
            <div className="w-full max-w-[400px]">
              {/* Tabs */}
              <div
                className="mb-8 flex gap-6 border-b border-[#E4E7EB]"
                role="tablist"
              >
                <button
                  role="tab"
                  aria-selected={tab === "login"}
                  onClick={() => setTab("login")}
                  className={`-mb-px border-b-2 pb-3 text-[14.5px] font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0D9488] focus-visible:ring-offset-2 ${
                    tab === "login"
                      ? "border-[#0D9488] text-[#0A1F33]"
                      : "border-transparent text-[#94A0B2] hover:text-[#0A1F33]"
                  }`}
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  Log in
                </button>
                <button
                  role="tab"
                  aria-selected={tab === "register"}
                  onClick={() => setTab("register")}
                  className={`-mb-px border-b-2 pb-3 text-[14.5px] font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0D9488] focus-visible:ring-offset-2 ${
                    tab === "register"
                      ? "border-[#0D9488] text-[#0A1F33]"
                      : "border-transparent text-[#94A0B2] hover:text-[#0A1F33]"
                  }`}
                  style={{ fontFamily: "var(--font-display)" }}
                >
                  Register as patient
                </button>
              </div>

              {tab === "login" ? (
                <>
                  <h2
                    className="text-[22px] font-semibold text-[#0A1F33]"
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    Sign in
                  </h2>
                  <p className="mt-1.5 text-[14px] text-[#64748B]">
                    Manage doctors, patients, and appointments.
                  </p>

                  {registerSuccess && (
                    <p className="mt-4 rounded-lg bg-[#0D9488]/10 px-3.5 py-2.5 text-[13.5px] text-[#0D9488]">
                      Account created. Sign in to continue.
                    </p>
                  )}

                  <form onSubmit={handleLogin} className="mt-7 space-y-5">
                    <Field
                      id="username"
                      name="username"
                      label="Username"
                      autoComplete="username"
                    />
                    <Field
                      id="password"
                      name="password"
                      label="Password"
                      type="password"
                      autoComplete="current-password"
                    />

                    {loginError && (
                      <p className="text-[13.5px] text-red-600" role="alert">
                        {loginError}
                      </p>
                    )}

                    <button
                      type="submit"
                      disabled={loginPending}
                      className="w-full rounded-lg bg-[#0D9488] py-3.5 text-[14.5px] font-semibold text-white transition-colors hover:bg-[#0A1F33] disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0D9488] focus-visible:ring-offset-2"
                      style={{ fontFamily: "var(--font-display)" }}
                    >
                      {loginPending ? "Signing in…" : "Sign in"}
                    </button>
                  </form>
                </>
              ) : (
                <>
                  <h2
                    className="text-[22px] font-semibold text-[#0A1F33]"
                    style={{ fontFamily: "var(--font-display)" }}
                  >
                    Create your account
                  </h2>
                  <p className="mt-1.5 text-[14px] text-[#64748B]">
                    Register as a patient to book appointments.
                  </p>

                  <form onSubmit={handleRegister} className="mt-7 space-y-5">
                    <div className="grid grid-cols-2 gap-4">

                    <Field
                      id="name"
                      name="first_name"
                      label="First name"
                      placeholder="Jane"
                      autoComplete="name"
                    />
                      <Field
                      id="name"
                      name="last_name"
                      label="last name"
                      placeholder="Wanjiru"
                      autoComplete="name"
                    />
                    </div>
                    <Field
                      id="email"
                      name="email"
                      label="Email address"
                      type="email"
                      placeholder="you@example.com"
                      autoComplete="email"
                    />
                    <Field
                      id="phone"
                      name="phone"
                      label="Phone number"
                      type="tel"
                      placeholder="+254 7XX XXX XXX"
                      autoComplete="tel"
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <Field
                        id="reg-password"
                        name="password"
                        label="Password"
                        type="password"
                        autoComplete="new-password"
                      />
                      <Field
                        id="confirm-password"
                        name="confirmPassword"
                        label="Confirm"
                        type="password"
                        autoComplete="new-password"
                      />
                    </div>

                    {registerError && (
                      <p className="text-[13.5px] text-red-600" role="alert">
                        {registerError}
                      </p>
                    )}

                    <button
                      type="submit"
                      disabled={registerPending}
                      className="w-full rounded-lg bg-[#0D9488] py-3.5 text-[14.5px] font-semibold text-white transition-colors hover:bg-[#0A1F33] disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0D9488] focus-visible:ring-offset-2"
                      style={{ fontFamily: "var(--font-display)" }}
                    >
                      {registerPending ? "Creating account…" : "Create account"}
                    </button>
                  </form>
                </>
              )}

              <p
                className="mt-8 text-center text-[11.5px] uppercase tracking-[0.08em] text-[#94A0B2]"
                style={{ fontFamily: "var(--font-mono)" }}
              >
                Protected by 256-bit encryption
              </p>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}