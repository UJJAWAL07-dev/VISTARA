export default function LandingPage() {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#07111f",
        color: "#ffffff",
        fontFamily: "Inter, Arial, sans-serif",
      }}
    >
      <header
        style={{
          height: "72px",
          padding: "0 48px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1px solid rgba(255,255,255,0.08)",
        }}
      >
        <div style={{ fontSize: "24px", fontWeight: 700 }}>
          VISTARA
        </div>

        <nav style={{ display: "flex", gap: "28px" }}>
          <a href="/" style={{ color: "#fff", textDecoration: "none" }}>
            Home
          </a>

          <a
            href="/auth"
            style={{ color: "#fff", textDecoration: "none" }}
          >
            Sign In
          </a>
        </nav>
      </header>

      <main
        style={{
          minHeight: "calc(100vh - 72px)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px 24px",
        }}
      >
        <section
          style={{
            maxWidth: "900px",
            textAlign: "center",
          }}
        >
          <p
            style={{
              fontSize: "14px",
              letterSpacing: "3px",
              textTransform: "uppercase",
              opacity: 0.6,
              marginBottom: "20px",
            }}
          >
            Spatial Intelligence Platform
          </p>

          <h1
            style={{
              fontSize: "64px",
              lineHeight: 1.05,
              margin: "0 0 24px",
            }}
          >
            See your world
            <br />
            differently.
          </h1>

          <p
            style={{
              fontSize: "20px",
              lineHeight: 1.6,
              opacity: 0.7,
              maxWidth: "650px",
              margin: "0 auto 36px",
            }}
          >
            VISTARA brings geographic data, spatial analysis and
            visualization together in one intelligent workspace.
          </p>

          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: "16px",
              flexWrap: "wrap",
            }}
          >
            <a
              href="/auth"
              style={{
                padding: "14px 28px",
                borderRadius: "10px",
                background: "#ffffff",
                color: "#07111f",
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              Get Started
            </a>

            <a
              href="/dashboard"
              style={{
                padding: "14px 28px",
                borderRadius: "10px",
                border: "1px solid rgba(255,255,255,0.2)",
                color: "#ffffff",
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              Explore Dashboard
            </a>
          </div>
        </section>
      </main>
    </div>
  );
}