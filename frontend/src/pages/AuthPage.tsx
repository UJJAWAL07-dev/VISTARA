export default function AuthPage() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#07111f",
        color: "#ffffff",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
        fontFamily: "Inter, Arial, sans-serif",
      }}
    >
      <div
        style={{
          width: "100%",
          maxWidth: "420px",
          padding: "40px",
          borderRadius: "20px",
          background: "#101c2d",
          border: "1px solid rgba(255,255,255,0.08)",
        }}
      >
        <a
          href="/"
          style={{
            color: "#ffffff",
            textDecoration: "none",
            opacity: 0.6,
            fontSize: "14px",
          }}
        >
          ← Back to VISTARA
        </a>

        <h1 style={{ marginTop: "32px", marginBottom: "10px" }}>
          Welcome back
        </h1>

        <p style={{ opacity: 0.6, marginBottom: "32px" }}>
          Sign in to continue to your workspace.
        </p>

        <label style={{ display: "block", marginBottom: "8px" }}>
          Email
        </label>

        <input
          type="email"
          placeholder="you@example.com"
          style={{
            width: "100%",
            padding: "14px",
            marginBottom: "20px",
            borderRadius: "10px",
            border: "1px solid rgba(255,255,255,0.12)",
            background: "#07111f",
            color: "#ffffff",
            outline: "none",
          }}
        />

        <label style={{ display: "block", marginBottom: "8px" }}>
          Password
        </label>

        <input
          type="password"
          placeholder="••••••••"
          style={{
            width: "100%",
            padding: "14px",
            marginBottom: "24px",
            borderRadius: "10px",
            border: "1px solid rgba(255,255,255,0.12)",
            background: "#07111f",
            color: "#ffffff",
            outline: "none",
          }}
        />

        <button
          onClick={() => {
            window.location.href = "/dashboard";
          }}
          style={{
            width: "100%",
            padding: "14px",
            borderRadius: "10px",
            border: "none",
            background: "#ffffff",
            color: "#07111f",
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          Sign In
        </button>

        <p
          style={{
            textAlign: "center",
            marginTop: "24px",
            opacity: 0.6,
            fontSize: "14px",
          }}
        >
          New to VISTARA?{" "}
          <a
            href="/onboarding"
            style={{ color: "#ffffff" }}
          >
            Get started
          </a>
        </p>
      </div>
    </div>
  );
}