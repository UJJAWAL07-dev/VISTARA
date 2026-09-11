import { useState } from "react";

import {
  ArrowRight,
  Database,
  FileOutput,
  Map,
  ScanSearch,
  ShieldCheck,
} from "lucide-react";
export default function LandingPage() {
  return (
    <div className="vistara-page min-h-screen text-white">

      {/* =====================================================
          FIXED BACKGROUND VIDEO
          This stays behind the entire landing page.
          ===================================================== */}
      <div className="vistara-background" aria-hidden="true">
        <video
          className="vistara-background-video"
          src="/videos/globe-zoom.mp4"
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
        />

        <div className="vistara-background-overlay" />

        <div className="vistara-background-vignette" />
      </div>

      {/* =====================================================
          NAVBAR
          Kept transparent and over the background.
          ===================================================== */}
      <header className="absolute inset-x-0 top-0 z-50">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6 lg:px-8">

          {/* VISTARA Logo */}
          <a
            href="/"
            className="group flex flex-col leading-none"
            aria-label="VISTARA home"
          >
            <span className="text-[15px] font-bold tracking-[0.08em] text-white transition-opacity duration-200 group-hover:opacity-80">
              VISTARA
            </span>

            <span className="mt-1 text-[7px] font-medium uppercase tracking-[0.28em] text-white/45">
              Urban Cadastral Intelligence
            </span>
          </a>

          {/* Navigation */}
          <nav className="hidden items-center gap-8 md:flex">

            <a
              href="#workflow"
              className="text-[13px] font-medium text-white/65 transition-colors duration-200 hover:text-white"
            >
              Workflow
            </a>

            <a
              href="#capabilities"
              className="text-[13px] font-medium text-white/65 transition-colors duration-200 hover:text-white"
            >
              Capabilities
            </a>

            <a
              href="/auth"
              className="text-[13px] font-medium text-white/65 transition-colors duration-200 hover:text-white"
            >
              Sign in
            </a>

            <a
              href="/auth"
              className="ml-1 flex items-center gap-2 rounded-md bg-white px-4 py-2 text-[12px] font-semibold text-slate-950 shadow-lg shadow-black/10 transition-all duration-200 hover:bg-white/90 hover:shadow-xl"
            >
              Get Started
              <ArrowRight className="size-3.5" />
            </a>

          </nav>
        </div>
      </header>

      {/* =====================================================
          PAGE CONTENT
          Everything here scrolls over the fixed video.
          ===================================================== */}
      <main className="relative z-10">

        {/* =================================================
            HERO
            ================================================= */}
        <section className="vistara-hero relative min-h-screen overflow-hidden">

          {/* Top readability gradient */}
          <div className="absolute inset-x-0 top-0 z-[3] h-52 bg-gradient-to-b from-slate-950/65 via-slate-950/20 to-transparent" />

          {/* Hero Content */}
          <div className="hero-content relative z-10 mx-auto flex min-h-screen max-w-7xl items-center px-6 pb-20 pt-28 lg:px-8">

            <div className="max-w-5xl">

              {/* Hero Heading */}
              <h1 className="hero-heading">

                <span className="hero-line hero-line-one">
                  From urban imagery to
                </span>

                <span className="hero-line hero-line-two hero-heading-muted">
                  intelligent cadastral maps.
                </span>

              </h1>

              {/* Hero Description */}
              <p className="hero-description mt-7 max-w-2xl text-[15px] font-medium leading-7 tracking-[-0.01em] text-white/65 md:text-base">
                VISTARA transforms inherited drone and urban imagery into
                structured building, road, parcel and land-use information
                that can be inspected, validated, analyzed and exported.
              </p>

              {/* Hero Actions */}
              <div className="hero-actions mt-8 flex flex-wrap gap-3">

                <a
                  href="/auth"
                  className="hero-primary-button flex items-center gap-2 rounded-lg bg-white px-5 py-3 text-[13px] font-semibold tracking-[-0.01em] text-slate-950"
                >
                  Explore VISTARA
                  <ArrowRight className="size-4" />
                </a>

                <a
                  href="/dashboard"
                  className="hero-secondary-button flex items-center rounded-lg border border-white/20 bg-black/10 px-5 py-3 text-[13px] font-medium tracking-[-0.01em] text-white/80 backdrop-blur-sm"
                >
                  View Demo
                </a>

              </div>
            </div>
          </div>
        </section>

       {/* VISTARA Introduction */}
<section
  id="about"
  className="vistara-intro-section"
>
  <div className="mx-auto max-w-7xl px-6 py-28 lg:px-8 lg:py-36">

    <div className="grid items-center gap-14 lg:grid-cols-[0.9fr_1.1fr] lg:gap-20">

      {/* =================================================
          LEFT — VISTARA INTRODUCTION
          ================================================= */}
      <div className="max-w-xl">

        <p className="section-eyebrow">
          VISTARA
        </p>

        <h2 className="intro-heading mt-5">
          Turning urban imagery
          <span> into intelligence.</span>
        </h2>

        <p className="intro-description mt-7">
          VISTARA transforms inherited drone and urban imagery into
          structured geospatial information that can be understood,
          inspected and acted upon.
        </p>

        <p className="intro-description mt-4">
          From building and road extraction to cadastral mapping,
          validation and export, VISTARA brings the complete workflow
          into one intelligent workspace.
        </p>

        <div className="mt-9 flex items-center gap-6">

          <a
            href="#workflow"
            className="intro-link group"
          >
            Explore the workflow

            <ArrowRight className="size-4 transition-transform duration-300 group-hover:translate-x-1" />
          </a>

          <span className="h-px w-12 bg-white/15" />

          <span className="text-[10px] font-medium uppercase tracking-[0.18em] text-white/30">
            AI · GIS · WebGIS
          </span>

        </div>
      </div>


      {/* =================================================
          RIGHT — SAMPLE VIDEO
          This is an independent visual block.
          It does NOT overlap the fixed globe background.
          ================================================= */}
      <div className="vistara-sample-video-wrapper">

        <div className="vistara-sample-video">

          <video
            src="/videos/vistara-sample.mp4"
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
            aria-label="VISTARA sample workflow demonstration"
          />

          {/* Video shade */}
          <div className="vistara-sample-video-shade" />

          {/* Small label */}
          <div className="vistara-video-label">
            <span className="vistara-video-dot" />
            VISTARA WORKSPACE
          </div>

          {/* Video controls-style indicator */}
          <div className="vistara-video-status">
            <span>LIVE PREVIEW</span>
          </div>

        </div>

        <p className="vistara-video-caption">
          From imagery to structured spatial intelligence.
        </p>

      </div>

    </div>
  </div>
</section>

        {/* =================================================
    WORKFLOW
    ================================================= */}
<section
  id="workflow"
  className="vistara-workflow-section"
>
  <div className="mx-auto max-w-7xl px-6 py-28 lg:px-8 lg:py-36">

    {/* Section Heading */}
    <div className="mx-auto max-w-3xl text-center">

      <p className="section-eyebrow">
        Workflow
      </p>

      <h2 className="workflow-heading mt-4">
        From imagery to spatial intelligence.
      </h2>

      <p className="workflow-intro mt-5">
        A connected workflow for extracting, validating and delivering
        structured geospatial information from urban imagery.
      </p>

    </div>


    {/* Workflow Features */}
    <div className="relative mt-16">

      {/* Left navigation */}



      {/* Four workflow columns */}
      <div className="workflow-features">

        {/* 01 */}
        <WorkflowFeature
          number="01"
          icon={<Database className="size-7" strokeWidth={1.4} />}
          title="Input"
          text="Bring inherited drone and urban imagery into the workspace."
        />

        {/* 02 */}
        <WorkflowFeature
          number="02"
          icon={<ScanSearch className="size-7" strokeWidth={1.4} />}
          title="AI Extraction"
          text="Extract building, road and other spatial features from imagery."
        />

        {/* 03 */}
        <WorkflowFeature
          number="03"
          icon={<ShieldCheck className="size-7" strokeWidth={1.4} />}
          title="Validate"
          text="Inspect extracted geometry and identify spatial inconsistencies."
        />

        {/* 04 */}
        <WorkflowFeature
          number="04"
          icon={<FileOutput className="size-7" strokeWidth={1.4} />}
          title="Deliver"
          text="Export structured and validated information for downstream GIS use."
        />

      </div>


      {/* Right navigation */}
      

    </div>

  </div>
</section>

{/* =================================================
    CAPABILITIES
    ================================================= */}
<section
  id="capabilities"
  className="vistara-capabilities-section"
>
  <div className="mx-auto max-w-7xl px-6 py-28 lg:px-8 lg:py-36">

    {/* =================================================
        SECTION HEADER
        ================================================= */}
    <div className="capabilities-header">

      <p className="section-eyebrow">
        Capabilities
      </p>

      <h2 className="capabilities-heading mt-4">
        Built for urban and cadastral workflows.
      </h2>

      <p className="capabilities-intro mt-5">
        Explore the core capabilities that connect imagery,
        extraction, GIS validation and structured spatial output
        inside VISTARA.
      </p>

    </div>


    {/* =================================================
        CAPABILITY SELECTOR
        ================================================= */}
    <CapabilityShowcase />

  </div>
</section>
      </main>
{/* =================================================
    WHY VISTARA
    ================================================= */}
<section
  id="why-vistara"
  className="vistara-why-section"
>
  <div className="mx-auto max-w-7xl px-6 py-28 lg:px-8 lg:py-36">

    <div className="why-vistara-grid">

      {/* =================================================
          LEFT — INFORMATION
          ================================================= */}
      <div className="why-vistara-content">

        <p className="section-eyebrow">
          Why VISTARA
        </p>

        <h2 className="why-vistara-heading mt-4">
          Urban mapping should
          <span> go beyond imagery.</span>
        </h2>

        <div className="why-vistara-copy">

          <p>
            Drone and survey imagery contains valuable spatial
            information, but imagery alone is not the final product.
            Turning that information into useful cadastral data
            requires extraction, organization, validation and
            inspection.
          </p>

          <p>
            VISTARA connects these steps into one focused workflow,
            helping users move from inherited imagery to structured
            spatial information that can be reviewed, understood
            and exported.
          </p>

          <p>
            Instead of treating mapping as a collection of disconnected
            tools, VISTARA brings the imagery, AI extraction and GIS
            workflow together in one workspace.
          </p>

        </div>

        <div className="why-vistara-link-row">

          <a
            href="#workflow"
            className="why-vistara-link group"
          >
            Explore the workflow

            <ArrowRight
              className="size-4 transition-transform duration-300 group-hover:translate-x-1"
            />
          </a>

          <span className="why-vistara-divider" />

          <span className="why-vistara-meta">
            AI · GIS · WEBGIS
          </span>

        </div>

      </div>


      {/* =================================================
          RIGHT — VIDEO
          ================================================= */}
      <div className="why-vistara-visual-column">

        <div className="why-vistara-video">

          <video
            src="/videos/why-vistara.mp4"
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
            aria-label="VISTARA urban mapping demonstration"
          />

          <div className="why-vistara-video-overlay" />

          <div className="why-vistara-video-top">
            <span className="why-vistara-video-label">
              VISTARA
            </span>

            <span className="why-vistara-video-state">
              WORKSPACE PREVIEW
            </span>
          </div>

          <div className="why-vistara-video-bottom">
            <span className="why-vistara-video-line" />

            <span>
              URBAN · CADASTRAL · SPATIAL
            </span>
          </div>

        </div>

      </div>

    </div>

  </div>
</section>
      {/* =====================================================
          FOOTER
          ===================================================== */}
      <footer className="relative z-10 border-t border-white/10 bg-slate-950/30 backdrop-blur-md">

        <div className="mx-auto flex max-w-7xl flex-col gap-2 px-6 py-10 text-xs text-white/40 sm:flex-row sm:items-center sm:justify-between lg:px-8">

          <span>
            VISTARA · Urban Cadastral Intelligence
          </span>

          <span>
            AI + GIS + WebGIS
          </span>

        </div>
      </footer>
    </div>
  );
}


/* =========================================================
   WORKFLOW CARD
   ========================================================= */

function WorkflowFeature({
  number,
  icon,
  title,
  text,
}: {
  number: string;
  icon: React.ReactNode;
  title: string;
  text: string;
}) {
  return (
    <div className="workflow-feature">

      {/* Icon */}
      <div className="workflow-feature-icon">
        {icon}
      </div>

      {/* Number */}
      <span className="workflow-feature-number">
        {number}
      </span>

      {/* Title */}
      <h3 className="workflow-feature-title">
        {title}
      </h3>

      {/* Description */}
      <p className="workflow-feature-text">
        {text}
      </p>

    </div>
  );
}


/* =========================================================
   CAPABILITY CARD
   ========================================================= */


function CapabilityShowcase() {
  const capabilities = [
    {
      id: "webgis",
      label: "WebGIS Workspace",
      eyebrow: "01 · WEBGIS",
      title: "Explore spatial information in one connected workspace.",
      description:
        "View generated spatial layers, select mapped features and inspect their properties through a focused WebGIS environment designed for urban and cadastral work.",
      image: "/images/capabilities/webgis.jpg",
      icon: <Map className="size-4" strokeWidth={1.6} />,
    },

    {
      id: "extraction",
      label: "AI Feature Extraction",
      eyebrow: "02 · AI EXTRACTION",
      title: "Turn urban imagery into structured spatial features.",
      description:
        "VISTARA processes inherited drone and urban imagery to identify buildings, roads, parcels and other meaningful spatial features.",
      image: "/images/capabilities/ai-extraction.jpg",
      icon: <ScanSearch className="size-4" strokeWidth={1.6} />,
    },

    {
      id: "validation",
      label: "GIS Validation",
      eyebrow: "03 · GIS VALIDATION",
      title: "Find geometry and spatial issues before delivery.",
      description:
        "Review generated geometry, surface spatial inconsistencies and validate the resulting features before they move downstream.",
      image: "/images/capabilities/validation.jpg",
      icon: <ShieldCheck className="size-4" strokeWidth={1.6} />,
    },

    {
      id: "output",
      label: "Structured Output",
      eyebrow: "04 · STRUCTURED OUTPUT",
      title: "Prepare validated spatial information for GIS workflows.",
      description:
        "Move validated cadastral information into structured outputs that can continue into downstream GIS analysis and operational workflows.",
      image: "/images/capabilities/output.jpg",
      icon: <FileOutput className="size-4" strokeWidth={1.6} />,
    },
  ];

  const [activeId, setActiveId] = useState("webgis");

  const activeCapability =
    capabilities.find((capability) => capability.id === activeId) ??
    capabilities[0];

  return (
    <div className="capability-showcase">

      {/* =================================================
          CAPABILITY SELECTOR
          ================================================= */}
      <div className="capability-selector">

        {capabilities.map((capability) => {
          const isActive = capability.id === activeId;

          return (
            <button
              key={capability.id}
              type="button"
              onClick={() => setActiveId(capability.id)}
              className={`capability-tab ${
                isActive ? "capability-tab-active" : ""
              }`}
              aria-pressed={isActive}
            >
              <span className="capability-tab-icon">
                {capability.icon}
              </span>

              <span className="capability-tab-label">
                {capability.label}
              </span>
            </button>
          );
        })}

      </div>


      {/* =================================================
          SELECTED CAPABILITY
          ================================================= */}
      <div className="capability-content">

        {/* =================================================
            LEFT — VISUAL
            ================================================= */}
        <div className="capability-visual-column">

          <div className="capability-visual">

            <img
              key={activeCapability.image}
              src={activeCapability.image}
              alt={`${activeCapability.label} visual`}
              className="capability-image"
            />

            <div className="capability-visual-overlay" />

            <div className="capability-visual-meta">
              <span>
                VISTARA
              </span>

              <span>
                {activeCapability.eyebrow}
              </span>
            </div>

          </div>

        </div>


        {/* =================================================
            RIGHT — INFORMATION
            ================================================= */}
        <div className="capability-details">

          <p className="capability-detail-eyebrow">
            {activeCapability.eyebrow}
          </p>

          <h3
            key={`${activeCapability.id}-title`}
            className="capability-detail-title"
          >
            {activeCapability.title}
          </h3>

          <p
            key={`${activeCapability.id}-description`}
            className="capability-detail-description"
          >
            {activeCapability.description}
          </p>

          <div className="capability-detail-rule" />

          <div className="capability-detail-footer">

            <span className="capability-detail-status">
              <span className="capability-status-dot" />
              Available in workspace
            </span>

            <span className="capability-detail-index">
              {capabilities.findIndex(
                (capability) =>
                  capability.id === activeCapability.id,
              ) + 1}
              <span>/</span>
              {capabilities.length}
            </span>

          </div>

        </div>

      </div>

    </div>
  );
}