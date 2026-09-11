import { useState } from "react";

export default function AuthPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [imageFailed, setImageFailed] = useState(false);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    // Keep the existing prototype navigation.
    window.location.href = "/dashboard";
  };

  return (
    <main className="auth-page">
      {/* Background */}
      <div className="auth-bg" />

      {/* VISTARA BRAND */}
      <a href="/" className="auth-brand">
        <span className="auth-brand-name">VISTARA</span>

        <span className="auth-brand-subtitle">
          Urban Cadastral Intelligence
        </span>
      </a>

      {/* MAIN AUTH COMPOSITION */}
      <div className="auth-shell">

        {/* =================================================
            LEFT VISUAL
           ================================================= */}
        <section className="auth-image-panel">

          {!imageFailed ? (
            <img
              src="/images/auth-visual.jpg"
              alt="Urban aerial imagery for cadastral mapping"
              className="auth-image"
              onError={() => setImageFailed(true)}
            />
          ) : (
            <video
              src="/videos/globe-zoom.mp4"
              autoPlay
              muted
              loop
              playsInline
              className="auth-image"
              aria-label="VISTARA geospatial visualization"
            />
          )}

          <div className="auth-image-overlay" />

          <div className="auth-image-index">
            VISTARA / 01
          </div>

        <div className="auth-image-content">

  <div className="auth-image-tag">
    <span className="auth-live-dot" />
    GEOSPATIAL INTELLIGENCE
  </div>

  <div className="auth-image-footer">
    <span>AI</span>

    <span className="auth-mini-line" />

    <span>GIS</span>

    <span className="auth-mini-line" />

    <span>WEBGIS</span>
  </div>

</div>
        </section>

        {/* =================================================
            SIGN IN PANEL
           ================================================= */}
        <section className="auth-panel">

          <a href="/" className="auth-back">
            <span>←</span>
            Back to VISTARA
          </a>

          <div className="auth-intro">

            <p className="auth-kicker">
              WORKSPACE ACCESS
            </p>

            <h1>
              Welcome back
            </h1>

            <p className="auth-description">
              Sign in to continue to your workspace.
            </p>

          </div>

          <form
            className="auth-form"
            onSubmit={handleSubmit}
          >

            {/* EMAIL */}
            <div className="auth-field">

              <label htmlFor="email">
                Email
              </label>

              <input
                id="email"
                name="email"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                required
              />

            </div>

            {/* PASSWORD */}
            <div className="auth-field">

              <label htmlFor="password">
                Password
              </label>

              <div className="auth-password">

                <input
                  id="password"
                  name="password"
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  required
                />

                <button
                  type="button"
                  className="auth-show-password"
                  onClick={() =>
                    setShowPassword(
                      (current) => !current
                    )
                  }
                >
                  {showPassword ? "Hide" : "Show"}
                </button>

              </div>

            </div>

            {/* SIGN IN */}
            <button
              type="submit"
              className="auth-submit"
            >
              <span>
                Sign In
              </span>

              <span className="auth-submit-arrow">
                →
              </span>
            </button>

          </form>

          {/* DIVIDER */}
          <div className="auth-divider">

            <span />

            <small>
              VISTARA WORKSPACE
            </small>

            <span />

          </div>

          {/* SIGN UP */}
          <p className="auth-signup">
            New to VISTARA?
            <a href="/onboarding">
              {" "}Get started
            </a>
          </p>

          <p className="auth-security">
            Secure access to your geospatial workspace
          </p>

        </section>

      </div>

      {/* FOOTER */}
      <div className="auth-bottom">

        <span>
          VISTARA
        </span>

        <span>
          Urban Cadastral Intelligence
        </span>

      </div>

    </main>
  );
}