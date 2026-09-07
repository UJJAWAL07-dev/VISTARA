export default function OnboardingPage() {
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
          maxWidth: "700px",
          textAlign: "center",
        }}
      >
        <p
          style={{
            textTransform: "uppercase",
            letterSpacing: "3px",
            fontSize: "13px",
            opacity: 0.5,
          }}
        >
          Welcome to VISTARA
        </p>

        <h1 style={{ fontSize: "42px", marginBottom: "16px" }}>
          Let's set up your workspace.
        </h1>

        <p
          style={{
            opacity: 0.65,
            fontSize: "18px",
            marginBottom: "40px",
          }}
        >
          Tell us what you want to explore and analyze.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "16px",
            marginBottom: "32px",
          }}
        >
          {[
            "Urban Planning",
            "Environment",
            "Infrastructure",
            "Research",
          ].map((item) => (
            <button
              key={item}
              style={{
                padding: "24px",
                borderRadius: "14px",
                border: "1px solid rgba(255,255,255,0.12)",
                background: "#101c2d",
                color: "#ffffff",
                cursor: "pointer",
                fontSize: "16px",
              }}
            >
              {item}
            </button>
          ))}
        </div>

        <button
          onClick={() => {
            window.location.href = "/dashboard";
          }}
          style={{
            padding: "14px 32px",
            border: "none",
            borderRadius: "10px",
            background: "#ffffff",
            color: "#07111f",
            fontWeight: 700,
            cursor: "pointer",
          }}
        >
          Continue to VISTARA
        </button>
      </div>
    </div>
  );
}