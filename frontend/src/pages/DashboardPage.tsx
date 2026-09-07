import { useState } from "react";
import {
  BarChart3,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Download,
  Eye,
  EyeOff,
  FileCheck2,
  Layers3,
  Map,
  MapPin,
  PanelRight,
  Play,
  RotateCcw,
  Search,
  Settings2,
  Sparkles,
  Upload,
  X,
  ZoomIn,
  ZoomOut,
} from "lucide-react";

import { cn } from "@/lib/utils";

type Layer = {
  id: string;
  name: string;
  type: string;
  visible: boolean;
};

type Parcel = {
  id: string;
  area: string;
  landUse: string;
  confidence: number;
  status: "Validated" | "Review";
};

const initialLayers: Layer[] = [
  {
    id: "parcels",
    name: "Generated Parcels",
    type: "Polygon",
    visible: true,
  },
  {
    id: "buildings",
    name: "Building Footprints",
    type: "Polygon",
    visible: true,
  },
  {
    id: "roads",
    name: "Road Network",
    type: "Line",
    visible: true,
  },
  {
    id: "land-use",
    name: "Land Use",
    type: "Polygon",
    visible: false,
  },
];

const parcels: Parcel[] = [
  {
    id: "P-1042",
    area: "1,284 m²",
    landUse: "Residential",
    confidence: 96,
    status: "Validated",
  },
  {
    id: "P-1043",
    area: "842 m²",
    landUse: "Residential",
    confidence: 91,
    status: "Validated",
  },
  {
    id: "P-1044",
    area: "1,976 m²",
    landUse: "Mixed Use",
    confidence: 78,
    status: "Review",
  },
  {
    id: "P-1045",
    area: "623 m²",
    landUse: "Commercial",
    confidence: 94,
    status: "Validated",
  },
];

function MapGrid() {
  return (
    <div className="absolute inset-0 overflow-hidden bg-[#e9edf0]">
      <div
        className="absolute inset-0 opacity-70"
        style={{
          backgroundImage:
            "linear-gradient(#cbd5dc 1px, transparent 1px), linear-gradient(90deg, #cbd5dc 1px, transparent 1px)",
          backgroundSize: "42px 42px",
        }}
      />

      <div className="absolute -left-[8%] top-[42%] h-10 w-[125%] rotate-[-12deg] bg-white shadow-sm" />
      <div className="absolute left-[15%] top-[-10%] h-[130%] w-8 rotate-[23deg] bg-white shadow-sm" />
      <div className="absolute left-[57%] top-[-10%] h-[130%] w-7 rotate-[23deg] bg-white shadow-sm" />

      <div className="absolute left-[9%] top-[16%] h-28 w-36 border-2 border-slate-500 bg-white/40" />
      <div className="absolute left-[30%] top-[12%] h-24 w-48 border-2 border-slate-500 bg-white/40" />
      <div className="absolute left-[63%] top-[17%] h-32 w-32 border-2 border-slate-500 bg-white/40" />

      <div className="absolute left-[13%] top-[59%] h-32 w-44 border-2 border-slate-500 bg-white/40" />
      <div className="absolute left-[40%] top-[54%] h-28 w-36 border-2 border-slate-500 bg-white/40" />
      <div className="absolute left-[69%] top-[58%] h-36 w-28 border-2 border-slate-500 bg-white/40" />

      <div className="absolute left-[17%] top-[21%] size-3 rounded-full border-2 border-white bg-slate-700 shadow" />
      <div className="absolute left-[48%] top-[62%] size-3 rounded-full border-2 border-white bg-slate-700 shadow" />
      <div className="absolute left-[76%] top-[29%] size-3 rounded-full border-2 border-white bg-slate-700 shadow" />

      <div className="absolute bottom-5 left-5 border border-slate-300 bg-white px-3 py-2 text-xs text-slate-600 shadow-sm">
        Sample urban cadastral workspace
      </div>

      <div className="absolute bottom-5 right-5 flex items-center border border-slate-300 bg-white text-xs text-slate-600 shadow-sm">
        <span className="border-r border-slate-300 px-3 py-2">
          100 m
        </span>
        <span className="px-3 py-2">EPSG:4326</span>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [layers, setLayers] = useState(initialLayers);
  const [selectedParcel, setSelectedParcel] = useState<Parcel | null>(
    parcels[0],
  );
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [activeTool, setActiveTool] = useState("select");
  const [processing, setProcessing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);

  function toggleLayer(id: string) {
    setLayers((currentLayers) =>
      currentLayers.map((layer) =>
        layer.id === id
          ? { ...layer, visible: !layer.visible }
          : layer,
      ),
    );
  }

  function runGeneration() {
    setProcessing(true);

    window.setTimeout(() => {
      setProcessing(false);
    }, 1800);
  }

  function runAnalysis() {
    setProcessing(true);

    window.setTimeout(() => {
      setProcessing(false);
      setAnalysisComplete(true);
    }, 1600);
  }

  return (
    <div className="flex h-[calc(100vh-4rem)] min-h-[700px] flex-col overflow-hidden bg-slate-100 text-slate-900">
      {/* Dashboard header */}
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-300 bg-white px-4">
        <div className="flex items-center gap-4">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-400">
              Project
            </p>
            <button
              type="button"
              className="mt-0.5 flex items-center gap-2 text-sm font-semibold text-slate-900"
            >
              Pune Urban Survey
              <ChevronDown className="size-3.5 text-slate-400" />
            </button>
          </div>

          <div className="hidden h-7 w-px bg-slate-200 sm:block" />

          <div className="hidden items-center gap-2 text-xs text-slate-500 sm:flex">
            <span className="size-2 rounded-full bg-emerald-500" />
            Workspace ready
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className="hidden items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 sm:flex"
          >
            <CircleHelp className="size-4" />
            Help
          </button>

          <button
            type="button"
            className="grid size-9 place-items-center rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50"
            aria-label="Settings"
          >
            <Settings2 className="size-4" />
          </button>

          <div className="grid size-9 place-items-center rounded-md bg-slate-900 text-xs font-semibold text-white">
            DU
          </div>
        </div>
      </header>

      {/* Main workspace */}
      <div className="flex min-h-0 flex-1">
        {/* Left toolbar */}
        <aside className="z-20 flex w-14 shrink-0 flex-col items-center border-r border-slate-300 bg-white py-3">
          <ToolButton
            label="Select"
            active={activeTool === "select"}
            onClick={() => setActiveTool("select")}
          >
            <MapPin className="size-4" />
          </ToolButton>

          <ToolButton
            label="Layers"
            active={activeTool === "layers"}
            onClick={() => setActiveTool("layers")}
          >
            <Layers3 className="size-4" />
          </ToolButton>

          <ToolButton
            label="Inspect"
            active={activeTool === "inspect"}
            onClick={() => setActiveTool("inspect")}
          >
            <Search className="size-4" />
          </ToolButton>

          <div className="my-3 h-px w-7 bg-slate-200" />

          <ToolButton
            label="Generate"
            active={activeTool === "generate"}
            onClick={() => setActiveTool("generate")}
          >
            <Sparkles className="size-4" />
          </ToolButton>

          <ToolButton
            label="Analysis"
            active={activeTool === "analysis"}
            onClick={() => setActiveTool("analysis")}
          >
            <BarChart3 className="size-4" />
          </ToolButton>

          <ToolButton
            label="Validation"
            active={activeTool === "validation"}
            onClick={() => setActiveTool("validation")}
          >
            <FileCheck2 className="size-4" />
          </ToolButton>

          <div className="mt-auto">
            <ToolButton
              label="Export"
              active={false}
              onClick={() => undefined}
            >
              <Download className="size-4" />
            </ToolButton>
          </div>
        </aside>

        {/* Layer panel */}
        <aside className="hidden w-64 shrink-0 border-r border-slate-300 bg-white lg:block">
          <div className="flex h-12 items-center justify-between border-b border-slate-200 px-4">
            <div>
              <p className="text-sm font-semibold">Layers</p>
              <p className="text-[11px] text-slate-400">
                {layers.filter((layer) => layer.visible).length} visible
              </p>
            </div>

            <button
              type="button"
              className="grid size-8 place-items-center rounded-md text-slate-500 hover:bg-slate-100"
              aria-label="Add layer"
            >
              <Upload className="size-4" />
            </button>
          </div>

          <div className="border-b border-slate-200 p-3">
            <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Dataset
                  </p>
                  <p className="mt-1 text-sm font-medium">
                    Pune_Ward_07
                  </p>
                </div>
                <Map className="size-4 text-slate-400" />
              </div>
              <p className="mt-2 text-xs text-slate-500">
                Urban imagery · 2.4 GB
              </p>
            </div>
          </div>

          <div className="p-2">
            <p className="px-2 py-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
              Map layers
            </p>

            {layers.map((layer) => (
              <div
                key={layer.id}
                className="flex items-center gap-2 rounded-md px-2 py-2 hover:bg-slate-50"
              >
                <button
                  type="button"
                  onClick={() => toggleLayer(layer.id)}
                  className="grid size-7 place-items-center rounded text-slate-500 hover:bg-slate-100"
                  aria-label={
                    layer.visible
                      ? `Hide ${layer.name}`
                      : `Show ${layer.name}`
                  }
                >
                  {layer.visible ? (
                    <Eye className="size-4" />
                  ) : (
                    <EyeOff className="size-4 text-slate-300" />
                  )}
                </button>

                <div className="min-w-0 flex-1">
                  <p
                    className={cn(
                      "truncate text-sm font-medium",
                      !layer.visible && "text-slate-400",
                    )}
                  >
                    {layer.name}
                  </p>
                  <p className="text-[10px] text-slate-400">{layer.type}</p>
                </div>
              </div>
            ))}
          </div>
        </aside>

        {/* Central map */}
        <main className="relative min-w-0 flex-1">
          <MapGrid />

          {/* Map controls */}
          <div className="absolute left-4 top-4 z-10 flex flex-col border border-slate-300 bg-white shadow-sm">
            <button
              type="button"
              className="grid size-9 place-items-center border-b border-slate-200 text-slate-600 hover:bg-slate-50"
              aria-label="Zoom in"
            >
              <ZoomIn className="size-4" />
            </button>
            <button
              type="button"
              className="grid size-9 place-items-center text-slate-600 hover:bg-slate-50"
              aria-label="Zoom out"
            >
              <ZoomOut className="size-4" />
            </button>
          </div>

          <div className="absolute right-4 top-4 z-10 flex gap-2">
            <button
              type="button"
              className="flex items-center gap-2 border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            >
              <RotateCcw className="size-3.5" />
              Reset view
            </button>
          </div>

          {/* Map title */}
          <div className="absolute left-4 top-24 z-10 border border-slate-300 bg-white px-4 py-3 shadow-sm">
            <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
              MAP WORKSPACE
            </p>
            <p className="mt-1 text-sm font-semibold">
              Generated cadastral features
            </p>
          </div>

          {/* Processing overlay */}
          {processing && (
            <div className="absolute inset-0 z-30 grid place-items-center bg-slate-950/10">
              <div className="w-80 border border-slate-300 bg-white p-5 shadow-lg">
                <div className="flex items-center gap-3">
                  <div className="size-5 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900" />
                  <div>
                    <p className="text-sm font-semibold">
                      Processing workspace
                    </p>
                    <p className="mt-1 text-xs text-slate-500">
                      VISTARA is processing the selected operation...
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>

        {/* Right inspection panel */}
        {rightPanelOpen && (
          <aside className="hidden w-80 shrink-0 border-l border-slate-300 bg-white xl:block">
            <div className="flex h-12 items-center justify-between border-b border-slate-200 px-4">
              <div>
                <p className="text-sm font-semibold">Inspector</p>
                <p className="text-[11px] text-slate-400">
                  Feature properties
                </p>
              </div>

              <button
                type="button"
                onClick={() => setRightPanelOpen(false)}
                className="grid size-8 place-items-center rounded-md text-slate-500 hover:bg-slate-100"
                aria-label="Close inspector"
              >
                <X className="size-4" />
              </button>
            </div>

            <div className="border-b border-slate-200 p-4">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Selected parcel
              </p>

              {selectedParcel ? (
                <>
                  <div className="mt-2 flex items-center justify-between">
                    <h2 className="text-xl font-semibold">
                      {selectedParcel.id}
                    </h2>
                    <span
                      className={cn(
                        "rounded-full px-2 py-1 text-[10px] font-semibold",
                        selectedParcel.status === "Validated"
                          ? "bg-emerald-50 text-emerald-700"
                          : "bg-amber-50 text-amber-700",
                      )}
                    >
                      {selectedParcel.status}
                    </span>
                  </div>

                  <div className="mt-4 grid grid-cols-2 gap-2">
                    <Property label="Area" value={selectedParcel.area} />
                    <Property
                      label="Land use"
                      value={selectedParcel.landUse}
                    />
                    <Property
                      label="Confidence"
                      value={`${selectedParcel.confidence}%`}
                    />
                    <Property label="Source" value="AI + GIS" />
                  </div>
                </>
              ) : (
                <div className="mt-3 border border-dashed border-slate-300 p-4 text-sm text-slate-500">
                  Select a feature on the map to inspect its properties.
                </div>
              )}
            </div>

            <div className="border-b border-slate-200 p-4">
              <div className="flex items-center justify-between">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                  Generation
                </p>
                <Sparkles className="size-4 text-slate-400" />
              </div>

              <p className="mt-2 text-sm leading-5 text-slate-600">
                Generate cadastral features from the selected dataset.
              </p>

              <button
                type="button"
                onClick={runGeneration}
                disabled={processing}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-md bg-slate-950 px-3 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
              >
                <Play className="size-4" />
                Generate features
              </button>
            </div>

            <div className="border-b border-slate-200 p-4">
              <div className="flex items-center justify-between">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                  Analysis
                </p>
                <BarChart3 className="size-4 text-slate-400" />
              </div>

              <div className="mt-3 space-y-2">
                <Metric label="Parcels detected" value="1,248" />
                <Metric label="Buildings detected" value="3,417" />
                <Metric label="Validation issues" value="23" />
              </div>

              <button
                type="button"
                onClick={runAnalysis}
                disabled={processing}
                className="mt-4 flex w-full items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2.5 text-sm font-medium text-slate-800 hover:bg-slate-50 disabled:opacity-50"
              >
                <FileCheck2 className="size-4" />
                Run validation
              </button>

              {analysisComplete && (
                <div className="mt-3 flex items-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
                  <CheckCircle2 className="size-4" />
                  Validation completed successfully.
                </div>
              )}
            </div>

            <div className="p-4">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Recent parcels
              </p>

              <div className="mt-2 space-y-1">
                {parcels.map((parcel) => (
                  <button
                    type="button"
                    key={parcel.id}
                    onClick={() => setSelectedParcel(parcel)}
                    className={cn(
                      "flex w-full items-center justify-between rounded-md px-3 py-2 text-left hover:bg-slate-50",
                      selectedParcel?.id === parcel.id && "bg-slate-100",
                    )}
                  >
                    <div>
                      <p className="text-xs font-semibold text-slate-800">
                        {parcel.id}
                      </p>
                      <p className="text-[10px] text-slate-400">
                        {parcel.landUse}
                      </p>
                    </div>

                    <span className="text-[10px] font-medium text-slate-500">
                      {parcel.confidence}%
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </aside>
        )}

        {!rightPanelOpen && (
          <button
            type="button"
            onClick={() => setRightPanelOpen(true)}
            className="absolute right-4 top-4 z-20 grid size-9 place-items-center border border-slate-300 bg-white text-slate-600 shadow-sm hover:bg-slate-50"
            aria-label="Open inspector"
          >
            <PanelRight className="size-4" />
          </button>
        )}
      </div>

      {/* Status bar */}
      <footer className="flex h-8 shrink-0 items-center justify-between border-t border-slate-300 bg-white px-3 text-[10px] text-slate-500">
        <div className="flex items-center gap-4">
          <span>VISTARA WORKSPACE</span>
          <span>Dataset: Pune_Ward_07</span>
          <span className="hidden sm:inline">4 layers</span>
        </div>

        <div className="flex items-center gap-4">
          <span className="hidden sm:inline">Ready</span>
          <span>Zoom 14</span>
          <span>EPSG:4326</span>
        </div>
      </footer>
    </div>
  );
}

function ToolButton({
  children,
  label,
  active,
  onClick,
}: {
  children: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={label}
      aria-label={label}
      className={cn(
        "mb-1 grid size-9 place-items-center rounded-md transition-colors",
        active
          ? "bg-slate-950 text-white"
          : "text-slate-500 hover:bg-slate-100 hover:text-slate-900",
      )}
    >
      {children}
    </button>
  );
}

function Property({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-slate-200 bg-slate-50 p-3">
      <p className="text-[10px] text-slate-400">{label}</p>
      <p className="mt-1 text-xs font-semibold text-slate-800">{value}</p>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 py-2 last:border-0">
      <span className="text-xs text-slate-500">{label}</span>
      <span className="text-sm font-semibold text-slate-900">{value}</span>
    </div>
  );
}