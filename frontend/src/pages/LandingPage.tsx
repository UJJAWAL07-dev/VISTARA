import {
  ArrowRight,
  CheckCircle2,
  Database,
  FileOutput,
  Layers3,
  Map,
  ScanSearch,
  ShieldCheck,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Navigation */}
      <header className="border-b border-white/10">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <div>
            <p className="text-lg font-bold tracking-tight">VISTARA</p>

            <p className="text-[9px] uppercase tracking-[0.25em] text-white/40">
              Urban Cadastral Intelligence
            </p>
          </div>

          <nav className="hidden items-center gap-6 text-sm text-white/60 md:flex">
            <a href="#workflow" className="hover:text-white">
              Workflow
            </a>

            <a href="#capabilities" className="hover:text-white">
              Capabilities
            </a>

            <a href="/auth" className="hover:text-white">
              Sign in
            </a>
          </nav>

          <a
            href="/auth"
            className="flex items-center gap-2 rounded-lg bg-white px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-white/90"
          >
            Get Started
            <ArrowRight className="size-4" />
          </a>
        </div>
      </header>

      {/* Hero */}
      <main>
        <section className="relative min-h-[calc(100vh-4rem)] overflow-hidden border-b border-white/10">
          {/* Background Globe Video */}
          <video
            className="absolute inset-0 z-0 h-full w-full object-cover"
            src="/videos/globe-zoom.mp4"
            autoPlay
            muted
            loop
            playsInline
            preload="auto"
          />

          {/* Dark Overlay */}
          <div className="absolute inset-0 z-[1] bg-slate-950/55" />

          {/* Hero Content */}
          <div className="relative z-10 mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl items-center px-6 py-24">
            <div className="max-w-4xl">
              {/* Hero Heading */}
              <h1 className="max-w-3xl text-5xl font-semibold leading-[1.05] tracking-tight md:text-6xl">
                <span className="block animate-fade-in">
                  From urban imagery to
                </span>

                <span className="block text-white/50 animate-fade-in-delay">
                  intelligent cadastral maps.
                </span>
              </h1>

              {/* Hero Description */}
              <p className="mt-6 max-w-2xl text-base leading-7 text-white/70 md:text-lg">
                VISTARA transforms inherited drone and urban imagery into
                structured building, road, parcel and land-use information
                that can be inspected, validated, analyzed and exported.
              </p>

              {/* Buttons */}
              <div className="mt-8 flex flex-wrap gap-3">
                <a
                  href="/auth"
                  className="flex items-center gap-2 rounded-lg bg-white px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-white/90"
                >
                  Explore VISTARA
                  <ArrowRight className="size-4" />
                </a>

                <a
                  href="/dashboard"
                  className="rounded-lg border border-white/20 bg-slate-950/30 px-5 py-3 text-sm font-medium text-white/80 backdrop-blur-sm transition hover:bg-white/10"
                >
                  View Demo
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Problem */}
        <section className="border-b border-white/10">
          <div className="mx-auto max-w-7xl px-6 py-20">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/35">
              The problem
            </p>

            <div className="mt-4 grid gap-10 lg:grid-cols-2">
              <h2 className="text-3xl font-semibold tracking-tight md:text-4xl">
                Urban mapping should not stop at imagery.
              </h2>

              <p className="text-sm leading-7 text-white/50 md:text-base">
                Large volumes of drone and survey imagery contain valuable
                spatial information, but converting that information into
                usable cadastral features requires extraction, GIS processing,
                validation and human inspection.
              </p>
            </div>
          </div>
        </section>

        {/* Workflow */}
        <section id="workflow" className="border-b border-white/10">
          <div className="mx-auto max-w-7xl px-6 py-20">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/35">
              Workflow
            </p>

            <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-tight">
              One workspace for the complete mapping pipeline.
            </h2>

            <div className="mt-10 grid gap-4 md:grid-cols-3 lg:grid-cols-6">
              <WorkflowStep
                number="01"
                icon={<Database className="size-5" />}
                title="Input"
                text="Upload or select urban imagery."
              />

              <WorkflowStep
                number="02"
                icon={<ScanSearch className="size-5" />}
                title="AI Extraction"
                text="Extract buildings, roads and boundaries."
              />

              <WorkflowStep
                number="03"
                icon={<Layers3 className="size-5" />}
                title="GIS Layers"
                text="Organize generated spatial features."
              />

              <WorkflowStep
                number="04"
                icon={<ShieldCheck className="size-5" />}
                title="Validation"
                text="Identify geometry and spatial issues."
              />

              <WorkflowStep
                number="05"
                icon={<Map className="size-5" />}
                title="Inspection"
                text="Inspect individual mapped features."
              />

              <WorkflowStep
                number="06"
                icon={<FileOutput className="size-5" />}
                title="Export"
                text="Export validated spatial results."
              />
            </div>
          </div>
        </section>

        {/* Capabilities */}
        <section id="capabilities">
          <div className="mx-auto max-w-7xl px-6 py-20">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-white/35">
              Capabilities
            </p>

            <h2 className="mt-3 text-3xl font-semibold tracking-tight">
              Built for urban and cadastral workflows.
            </h2>

            <div className="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Capability
                icon={<Map className="size-5" />}
                title="WebGIS workspace"
                text="Explore spatial layers, select features and inspect their properties."
              />

              <Capability
                icon={<ScanSearch className="size-5" />}
                title="AI feature extraction"
                text="Turn imagery into structured building, road and parcel features."
              />

              <Capability
                icon={<ShieldCheck className="size-5" />}
                title="GIS validation"
                text="Surface invalid geometries, conflicts and other spatial issues."
              />

              <Capability
                icon={<FileOutput className="size-5" />}
                title="Structured output"
                text="Prepare validated results for downstream GIS workflows."
              />
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10">
        <div className="mx-auto flex max-w-7xl flex-col gap-2 px-6 py-8 text-xs text-white/35 sm:flex-row sm:items-center sm:justify-between">
          <span>VISTARA · Urban Cadastral Intelligence</span>
          <span>AI + GIS + WebGIS</span>
        </div>
      </footer>
    </div>
  );
}

function WorkflowStep({
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
    <div className="rounded-xl border border-white/10 bg-white/[0.025] p-4">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-semibold text-white/25">
          {number}
        </span>

        <span className="text-white/60">{icon}</span>
      </div>

      <h3 className="mt-6 text-sm font-semibold">{title}</h3>

      <p className="mt-2 text-xs leading-5 text-white/40">{text}</p>
    </div>
  );
}

function Capability({
  icon,
  title,
  text,
}: {
  icon: React.ReactNode;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.025] p-5">
      <div className="flex size-9 items-center justify-center rounded-lg bg-white/10 text-white/70">
        {icon}
      </div>

      <h3 className="mt-5 text-sm font-semibold">{title}</h3>

      <p className="mt-2 text-xs leading-5 text-white/40">{text}</p>

      <div className="mt-4 flex items-center gap-1.5 text-[10px] text-emerald-400">
        <CheckCircle2 className="size-3.5" />
        Available in workspace
      </div>
    </div>
  );
}