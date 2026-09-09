import { useState } from "react";
import {
  ArrowRight,
  CheckCircle2,
  Database,
  Download,
  Layers3,
  Map,
  ScanSearch,
  ShieldCheck,
} from "lucide-react";

const steps = [
  {
    number: "01",
    title: "Select Data",
    description:
      "Load the project dataset and orthorectified imagery that will be used for cadastral mapping.",
    icon: Database,
  },
  {
    number: "02",
    title: "Generate Features",
    description:
      "Run the feature extraction workflow to generate parcel boundaries, building footprints and roads.",
    icon: ScanSearch,
  },
  {
    number: "03",
    title: "Review GIS Layers",
    description:
      "Inspect the generated parcels, buildings, roads and land-use layers directly on the map.",
    icon: Layers3,
  },
  {
    number: "04",
    title: "Run Analysis",
    description:
      "Run GIS analysis and topology validation to identify geometry and spatial inconsistencies.",
    icon: Map,
  },
  {
    number: "05",
    title: "Inspect Issues",
    description:
      "Select problematic features and review their properties, confidence and validation status.",
    icon: ShieldCheck,
  },
  {
    number: "06",
    title: "Export Results",
    description:
      "Download the processed cadastral results for further GIS use and reporting.",
    icon: Download,
  },
];

export default function OnboardingPage() {
  const [activeStep, setActiveStep] = useState(0);

  const currentStep = steps[activeStep];
  const CurrentIcon = currentStep.icon;

  function goToDashboard() {
    window.location.href = "/dashboard";
  }

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-white/10 bg-slate-950/95">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
          <div>
            <p className="text-lg font-semibold tracking-[0.18em]">VISTARA</p>
            <p className="mt-1 text-xs text-slate-500">
              AI-Enabled Urban Cadastral Mapping
            </p>
          </div>

          <button
            type="button"
            onClick={goToDashboard}
            className="rounded-lg border border-white/15 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/5"
          >
            Skip tutorial
          </button>
        </div>
      </header>

      {/* Main */}
      <section className="mx-auto max-w-6xl px-6 py-12">
        <div className="max-w-2xl">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-400">
            Learn how to use VISTARA
          </p>

          <h1 className="mt-3 text-4xl font-semibold tracking-tight">
            From urban imagery to a validated cadastral map.
          </h1>

          <p className="mt-4 text-base leading-7 text-slate-400">
            VISTARA combines AI feature extraction with GIS processing and
            validation to help users create, inspect and export urban
            cadastral information.
          </p>
        </div>

        {/* Workflow */}
        <div className="mt-10 grid gap-8 lg:grid-cols-[280px_1fr]">
          {/* Step list */}
          <div className="space-y-2">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const active = index === activeStep;

              return (
                <button
                  key={step.number}
                  type="button"
                  onClick={() => setActiveStep(index)}
                  className={`flex w-full items-center gap-4 border px-4 py-4 text-left transition ${
                    active
                      ? "border-blue-500/50 bg-blue-500/10"
                      : "border-white/10 bg-white/[0.02] hover:bg-white/[0.05]"
                  }`}
                >
                  <div
                    className={`grid size-9 shrink-0 place-items-center rounded-md ${
                      active
                        ? "bg-blue-500 text-white"
                        : "bg-white/5 text-slate-400"
                    }`}
                  >
                    <Icon className="size-4" />
                  </div>

                  <div className="min-w-0">
                    <p
                      className={`text-xs font-semibold uppercase tracking-wider ${
                        active ? "text-blue-400" : "text-slate-500"
                      }`}
                    >
                      Step {step.number}
                    </p>

                    <p className="mt-1 text-sm font-medium text-slate-200">
                      {step.title}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Active step */}
          <div className="min-h-[430px] border border-white/10 bg-white/[0.03] p-8 lg:p-10">
            <div className="flex size-14 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
              <CurrentIcon className="size-7" />
            </div>

            <p className="mt-8 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Step {currentStep.number} of 06
            </p>

            <h2 className="mt-3 text-3xl font-semibold">
              {currentStep.title}
            </h2>

            <p className="mt-5 max-w-xl text-base leading-7 text-slate-400">
              {currentStep.description}
            </p>

            {/* Workflow indicator */}
            <div className="mt-10 flex items-center gap-2">
              {steps.map((step, index) => (
                <button
                  key={step.number}
                  type="button"
                  onClick={() => setActiveStep(index)}
                  aria-label={`Go to step ${index + 1}`}
                  className={`h-1.5 flex-1 transition ${
                    index <= activeStep
                      ? "bg-blue-500"
                      : "bg-white/10"
                  }`}
                />
              ))}
            </div>

            {/* Navigation */}
            <div className="mt-8 flex items-center justify-between">
              <button
                type="button"
                disabled={activeStep === 0}
                onClick={() =>
                  setActiveStep((current) => Math.max(0, current - 1))
                }
                className="rounded-lg border border-white/10 px-4 py-2 text-sm text-slate-300 transition hover:bg-white/5 disabled:cursor-not-allowed disabled:opacity-30"
              >
                Previous
              </button>

              {activeStep < steps.length - 1 ? (
                <button
                  type="button"
                  onClick={() =>
                    setActiveStep((current) =>
                      Math.min(steps.length - 1, current + 1),
                    )
                  }
                  className="flex items-center gap-2 rounded-lg bg-blue-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-400"
                >
                  Next
                  <ArrowRight className="size-4" />
                </button>
              ) : (
                <button
                  type="button"
                  onClick={goToDashboard}
                  className="flex items-center gap-2 rounded-lg bg-blue-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-400"
                >
                  <CheckCircle2 className="size-4" />
                  Open VISTARA Dashboard
                </button>
              )}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}