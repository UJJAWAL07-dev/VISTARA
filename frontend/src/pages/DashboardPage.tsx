
import { useState, type ReactNode } from "react";
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

import type {
  AnalysisResults,
  Layer,
  LayerId,
  Parcel,
  ToolId,
} from "@/types/dashboard";

import MapGrid from "@/map/MapGrid";

const FOCUS_RING =
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-2";

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

const initialParcels: Parcel[] = [
{
  id: "P-1042",
  area: "1,284 m²",
  landUse: "Residential",
  confidence: 96,
  status: "Validated",
  geometry: {
    type: "Polygon",
    coordinates: [
      [
        [73.8567, 18.5204],
        [73.8577, 18.5204],
        [73.8577, 18.5213],
        [73.8567, 18.5213],
        [73.8567, 18.5204],
      ],
    ],
  },
},
  {
  id: "P-1043",
  area: "1,284 m²",
  landUse: "Residential",
  confidence: 96,
  status: "Validated",
  geometry: {
  type: "Polygon",
  coordinates: [
    [
      [73.8580, 18.5204],
      [73.8590, 18.5204],
      [73.8590, 18.5213],
      [73.8580, 18.5213],
      [73.8580, 18.5204],
    ],
  ],
},
},
  {
  id: "P-1044",
  area: "1,284 m²",
  landUse: "Residential",
  confidence: 96,
  status: "Validated",
  geometry: {
  type: "Polygon",
  coordinates: [
    [
      [73.8567, 18.5192],
      [73.8577, 18.5192],
      [73.8577, 18.5201],
      [73.8567, 18.5201],
      [73.8567, 18.5192],
    ],
  ],
},
},
];

// Parcels the "Generate features" action reveals. In a real integration
// these — and their geometry — would come back from the AI/GIS backend
// instead of being appended locally.
const generatedParcels: Parcel[] = [
 {
  id: "P-1045",
  area: "1,284 m²",
  landUse: "Residential",
  confidence: 96,
  status: "Validated",
  geometry: {
  type: "Polygon",
  coordinates: [
    [
      [73.8580, 18.5192],
      [73.8590, 18.5192],
      [73.8590, 18.5201],
      [73.8580, 18.5201],
      [73.8580, 18.5192],
    ],
  ],
},
},
  {
  id: "P-1046",
  area: "1,284 m²",
  landUse: "Residential",
  confidence: 96,
  status: "Validated",
  geometry: {
  type: "Polygon",
  coordinates: [
    [
      [73.8593, 18.5204],
      [73.8603, 18.5204],
      [73.8603, 18.5213],
      [73.8593, 18.5213],
      [73.8593, 18.5204],
    ],
  ],
},
},
{
  id: "P-1047",
  area: "1,284 m²",
  landUse: "Residential",
  confidence: 96,
  status: "Validated",
  geometry: {
  type: "Polygon",
  coordinates: [
    [
      [73.8593, 18.5192],
      [73.8603, 18.5192],
      [73.8603, 18.5201],
      [73.8593, 18.5201],
      [73.8593, 18.5192],
    ],
  ],
},
},
];

// Demo-only screen positions for the mock parcel markers, keyed by parcel
// id. This is purely a frontend visualization concern for the sample
// workspace — a real map integration would position features from actual
// geometry (GeoJSON, etc.) instead of a lookup like this. Positions are
// percentages of the map's own coordinate space, so they stay correct
// under the zoom transform applied to that same space.


const MIN_ZOOM = 10;
const MAX_ZOOM = 20;
const DEFAULT_ZOOM = 14;



function LayerListPanel({
  layers,
  onToggleLayer,
}: {
  layers: Layer[];
  onToggleLayer: (id: LayerId) => void;
}) {
  return (
    <>
      <div className="flex h-12 shrink-0 items-center justify-between border-b border-slate-200 px-4">
        <div>
          <p className="text-sm font-semibold">Layers</p>
          <p className="text-[11px] text-slate-400">
            {layers.filter((layer) => layer.visible).length} visible
          </p>
        </div>

        <button
          type="button"
          className={cn(
            "grid size-8 place-items-center rounded-md text-slate-500 disabled:cursor-not-allowed disabled:opacity-40",
            FOCUS_RING,
          )}
          aria-label="Add layer"
          title="Add layer (coming soon)"
          disabled
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
              <p className="mt-1 text-sm font-medium">Pune_Ward_07</p>
            </div>
            <Map className="size-4 text-slate-400" />
          </div>
          <p className="mt-2 text-xs text-slate-500">Urban imagery · 2.4 GB</p>
        </div>
      </div>

      <div className="p-2">
        <p className="px-2 py-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Map layers
        </p>

        {/* Each layer row is a single control (not a row + nested button)
            so there is exactly one click target and no risk of a click on
            the eye icon also triggering a separate row handler. */}
        {layers.map((layer) => (
          <button
            key={layer.id}
            type="button"
            onClick={() => onToggleLayer(layer.id)}
            title={layer.visible ? `Hide ${layer.name}` : `Show ${layer.name}`}
            aria-label={layer.visible ? `Hide ${layer.name}` : `Show ${layer.name}`}
            aria-pressed={layer.visible}
            className={cn(
              "flex w-full items-center gap-2 rounded-md px-2 py-2 text-left transition-colors hover:bg-slate-50 active:bg-slate-100",
              FOCUS_RING,
            )}
          >
            <span className="grid size-7 shrink-0 place-items-center rounded text-slate-500">
              {layer.visible ? (
                <Eye className="size-4" />
              ) : (
                <EyeOff className="size-4 text-slate-300" />
              )}
            </span>

            <span className="min-w-0 flex-1">
              <span
                className={cn(
                  "block truncate text-sm font-medium",
                  !layer.visible && "text-slate-400",
                )}
              >
                {layer.name}
              </span>
              <span className="block text-[10px] text-slate-400">{layer.type}</span>
            </span>
          </button>
        ))}
      </div>
    </>
  );
}

function InspectorPanelBody({
  selectedParcel,
  featuresGenerated,
  processing,
  onRunGeneration,
  analysisResults,
  onRunAnalysis,
  parcels,
  selectedParcelId,
  onSelectParcel,
}: {
  selectedParcel: Parcel | null;
  featuresGenerated: boolean;
  processing: boolean;
  onRunGeneration: () => void;
  analysisResults: AnalysisResults | null;
  onRunAnalysis: () => void;
  parcels: Parcel[];
  selectedParcelId: string | null;
  onSelectParcel: (id: string) => void;
}) {
  return (
    <>
      <div className="border-b border-slate-200 p-4">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Selected parcel
        </p>

        {selectedParcel ? (
          <>
            <div className="mt-2 flex items-center justify-between">
              <h2 className="text-xl font-semibold">{selectedParcel.id}</h2>
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
              <Property label="Land use" value={selectedParcel.landUse} />
              <Property label="Confidence" value={`${selectedParcel.confidence}%`} />
              <Property label="Source" value="AI + GIS" />
            </div>
          </>
        ) : (
          <div className="mt-3 border border-dashed border-slate-300 p-4 text-sm text-slate-500">
            <p className="font-medium text-slate-700">No feature selected</p>
            <p className="mt-1">Select a parcel on the map to inspect its properties.</p>
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
          {featuresGenerated
            ? "Cadastral features generated from the selected dataset."
            : "Generate cadastral features from the selected dataset."}
        </p>

        <button
          type="button"
          onClick={onRunGeneration}
          disabled={processing}
          className={cn(
            "mt-4 flex w-full items-center justify-center gap-2 rounded-md bg-slate-950 px-3 py-2.5 text-sm font-medium text-white transition-colors hover:bg-slate-800 active:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-50",
            FOCUS_RING,
          )}
        >
          <Play className="size-4" />
          {featuresGenerated ? "Regenerate features" : "Generate features"}
        </button>

        {featuresGenerated && !processing && (
          <div className="mt-3 flex items-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
            <CheckCircle2 className="size-4" />
            Features generated successfully.
          </div>
        )}
      </div>

      <div className="border-b border-slate-200 p-4">
        <div className="flex items-center justify-between">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            Analysis
          </p>
          <BarChart3 className="size-4 text-slate-400" />
        </div>

        {analysisResults ? (
          <div className="mt-3 space-y-2">
            <Metric
              label="Parcels detected"
              value={analysisResults.parcelsDetected.toLocaleString()}
            />
            <Metric
              label="Buildings detected"
              value={analysisResults.buildingsDetected.toLocaleString()}
            />
            <Metric
              label="Validation issues"
              value={String(analysisResults.validationIssues)}
            />
          </div>
        ) : (
          <div className="mt-3 border border-dashed border-slate-300 p-4 text-sm text-slate-500">
            Run validation to see analysis metrics.
          </div>
        )}

        <button
          type="button"
          onClick={onRunAnalysis}
          disabled={processing}
          className={cn(
            "mt-4 flex w-full items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2.5 text-sm font-medium text-slate-800 transition-colors hover:bg-slate-50 active:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50",
            FOCUS_RING,
          )}
        >
          <FileCheck2 className="size-4" />
          {analysisResults ? "Re-run validation" : "Run validation"}
        </button>

        {analysisResults && !processing && (
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
              onClick={() => onSelectParcel(parcel.id)}
              aria-pressed={selectedParcelId === parcel.id}
              className={cn(
                "flex w-full items-center justify-between rounded-md px-3 py-2 text-left transition-colors hover:bg-slate-50 active:bg-slate-100",
                FOCUS_RING,
                selectedParcelId === parcel.id && "bg-slate-100",
              )}
            >
              <span>
                <span className="block text-xs font-semibold text-slate-800">{parcel.id}</span>
                <span className="block text-[10px] text-slate-400">{parcel.landUse}</span>
              </span>

              <span className="text-[10px] font-medium text-slate-500">
                {parcel.confidence}%
              </span>
            </button>
          ))}
        </div>
      </div>
    </>
  );
}

export default function DashboardPage() {
  const [layers, setLayers] = useState<Layer[]>(initialLayers);
  const [parcels, setParcels] = useState<Parcel[]>(initialParcels);
  const [selectedParcelId, setSelectedParcelId] = useState<string | null>(
    initialParcels[0]?.id ?? null,
  );
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [inspectorDrawerOpen, setInspectorDrawerOpen] = useState(false);
  const [layersDrawerOpen, setLayersDrawerOpen] = useState(false);
  const [activeTool, setActiveTool] = useState<ToolId>("select");
  const [processing, setProcessing] = useState(false);
  const [processingLabel, setProcessingLabel] = useState("");
  const [featuresGenerated, setFeaturesGenerated] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResults | null>(null);
  const [zoom, setZoom] = useState(DEFAULT_ZOOM);

  // Single source of truth for parcel selection: everything (map markers,
  // the inspector, the recent-parcels list) derives from this one id, so
  // nothing can independently disagree about which parcel is selected.
  const selectedParcel = parcels.find((parcel) => parcel.id === selectedParcelId) ?? null;

  function toggleLayer(id: LayerId) {
    setLayers((currentLayers) =>
      currentLayers.map((layer) =>
        layer.id === id ? { ...layer, visible: !layer.visible } : layer,
      ),
    );
  }

  function selectParcel(id: string) {
    setSelectedParcelId(id);
    setRightPanelOpen(true);
    setInspectorDrawerOpen(true);
  }

  function openToolPanel(tool: ToolId) {
    setActiveTool(tool);
    setRightPanelOpen(true);
    setInspectorDrawerOpen(true);
  }

  function runGeneration() {
    setProcessing(true);
    setProcessingLabel("Generating cadastral features...");

    window.setTimeout(() => {
      setProcessing(false);
      setProcessingLabel("");
      setFeaturesGenerated(true);
      // Newly generated features change the underlying dataset, so any
      // previous analysis is now stale until validation is re-run.
      setAnalysisResults(null);

      setLayers((currentLayers) =>
        currentLayers.map((layer) =>
          layer.id === "parcels" || layer.id === "buildings" || layer.id === "roads"
            ? { ...layer, visible: true }
            : layer,
        ),
      );

      setParcels((currentParcels) => {
        const alreadyGenerated = generatedParcels.every((parcel) =>
          currentParcels.some((existing) => existing.id === parcel.id),
        );

        return alreadyGenerated ? currentParcels : [...currentParcels, ...generatedParcels];
      });
    }, 1800);
  }

  function runAnalysis() {
    setProcessing(true);
    setProcessingLabel("Running topology validation...");

    window.setTimeout(() => {
      setProcessing(false);
      setProcessingLabel("");
      setAnalysisResults({
        parcelsDetected: parcels.length,
        buildingsDetected: parcels.length * 3,
        validationIssues: parcels.filter((parcel) => parcel.status === "Review").length,
      });
    }, 1600);
  }

  function zoomIn() {
    setZoom((current) => Math.min(MAX_ZOOM, current + 1));
  }

  function zoomOut() {
    setZoom((current) => Math.max(MIN_ZOOM, current - 1));
  }

  function resetView() {
    setZoom(DEFAULT_ZOOM);
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
              className={cn(
                "mt-0.5 flex items-center gap-2 rounded text-sm font-semibold text-slate-900",
                FOCUS_RING,
              )}
            >
              Pune Urban Survey
              <ChevronDown className="size-3.5 text-slate-400" />
            </button>
          </div>

          <div className="hidden h-7 w-px bg-slate-200 sm:block" />

          <div className="hidden items-center gap-2 text-xs text-slate-500 sm:flex">
            <span
              className={cn(
                "size-2 rounded-full",
                processing ? "bg-amber-500" : "bg-emerald-500",
              )}
            />
            {processing ? "Workspace processing" : "Workspace ready"}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className={cn(
              "hidden items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-xs font-medium text-slate-700 hover:bg-slate-50 sm:flex",
              FOCUS_RING,
            )}
          >
            <CircleHelp className="size-4" />
            Help
          </button>

          <button
            type="button"
            className={cn(
              "grid size-9 place-items-center rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50",
              FOCUS_RING,
            )}
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
      <div className="relative flex min-h-0 flex-1">
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
            onClick={() => {
              setActiveTool("layers");
              setLayersDrawerOpen(true);
            }}
          >
            <Layers3 className="size-4" />
          </ToolButton>

          <ToolButton
            label="Inspect"
            active={activeTool === "inspect"}
            onClick={() => openToolPanel("inspect")}
          >
            <Search className="size-4" />
          </ToolButton>

          <div className="my-3 h-px w-7 bg-slate-200" />

          <ToolButton
            label="Generate"
            active={activeTool === "generate"}
            onClick={() => openToolPanel("generate")}
          >
            <Sparkles className="size-4" />
          </ToolButton>

          <ToolButton
            label="Analysis"
            active={activeTool === "analysis"}
            onClick={() => openToolPanel("analysis")}
          >
            <BarChart3 className="size-4" />
          </ToolButton>

          <ToolButton
            label="Validation"
            active={activeTool === "validation"}
            onClick={() => openToolPanel("validation")}
          >
            <FileCheck2 className="size-4" />
          </ToolButton>

          <div className="mt-auto">
            <ToolButton
              label="Export (coming soon)"
              active={false}
              disabled
              onClick={() => undefined}
            >
              <Download className="size-4" />
            </ToolButton>
          </div>
        </aside>

        {/* Layer panel (desktop, persistent) */}
        <aside
          className={cn(
            "hidden w-64 shrink-0 border-r bg-white lg:block",
            activeTool === "layers" ? "border-slate-400 ring-1 ring-inset ring-slate-200" : "border-slate-300",
          )}
        >
          <LayerListPanel layers={layers} onToggleLayer={toggleLayer} />
        </aside>

        {/* Layer panel (mobile/tablet drawer) */}
        {layersDrawerOpen && (
          <div className="fixed inset-0 z-40 flex lg:hidden">
            <button
              type="button"
              aria-label="Close layers panel"
              onClick={() => setLayersDrawerOpen(false)}
              className="absolute inset-0 bg-slate-950/30"
            />
            <aside className="relative flex h-full w-72 max-w-[85vw] flex-col border-r border-slate-300 bg-white shadow-lg">
              <div className="flex h-10 shrink-0 items-center justify-end border-b border-slate-200 px-2">
                <button
                  type="button"
                  onClick={() => setLayersDrawerOpen(false)}
                  className={cn(
                    "grid size-8 place-items-center rounded-md text-slate-500 hover:bg-slate-100",
                    FOCUS_RING,
                  )}
                  aria-label="Close layers panel"
                >
                  <X className="size-4" />
                </button>
              </div>
              <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
                <LayerListPanel layers={layers} onToggleLayer={toggleLayer} />
              </div>
            </aside>
          </div>
        )}

        {/* Central map */}
        <main className="relative min-w-0 flex-1">
          <MapGrid
  layers={layers}
  parcels={parcels}
  selectedParcelId={selectedParcelId}
  zoom={zoom}
  onZoomChange={setZoom}
  onResetView={resetView}
  onSelectParcel={setSelectedParcelId}
/>

          {/* Map controls */}
          <div className="absolute left-4 top-4 z-10 flex flex-col border border-slate-300 bg-white shadow-sm">
            <button
              type="button"
              onClick={zoomIn}
              disabled={zoom >= MAX_ZOOM}
              className={cn(
                "grid size-9 place-items-center border-b border-slate-200 text-slate-600 transition-colors hover:bg-slate-50 active:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40",
                FOCUS_RING,
              )}
              aria-label="Zoom in"
            >
              <ZoomIn className="size-4" />
            </button>
            <button
              type="button"
              onClick={zoomOut}
              disabled={zoom <= MIN_ZOOM}
              className={cn(
                "grid size-9 place-items-center text-slate-600 transition-colors hover:bg-slate-50 active:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40",
                FOCUS_RING,
              )}
              aria-label="Zoom out"
            >
              <ZoomOut className="size-4" />
            </button>
          </div>

          <div className="absolute right-4 top-4 z-10 flex gap-2">
            <button
              type="button"
              onClick={resetView}
              className={cn(
                "flex items-center gap-2 border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50 active:bg-slate-100",
                FOCUS_RING,
              )}
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
            <p className="mt-1 text-sm font-semibold">Generated cadastral features</p>
          </div>

          {/* Processing overlay */}
          {processing && (
            <div className="absolute inset-0 z-30 grid place-items-center bg-slate-950/10">
              <div className="w-80 border border-slate-300 bg-white p-5 shadow-lg">
                <div className="flex items-center gap-3">
                  <div className="size-5 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900" />
                  <div>
                    <p className="text-sm font-semibold">Processing workspace</p>
                    <p className="mt-1 text-xs text-slate-500">{processingLabel}</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>

        {/* Right inspection panel (desktop, persistent) */}
        {rightPanelOpen && (
          <aside className="hidden w-80 shrink-0 flex-col border-l border-slate-300 bg-white xl:flex">
            <div className="flex h-12 shrink-0 items-center justify-between border-b border-slate-200 px-4">
              <div>
                <p className="text-sm font-semibold">Inspector</p>
                <p className="text-[11px] text-slate-400">Feature properties</p>
              </div>

              <button
                type="button"
                onClick={() => setRightPanelOpen(false)}
                className={cn(
                  "grid size-8 place-items-center rounded-md text-slate-500 hover:bg-slate-100 active:bg-slate-200",
                  FOCUS_RING,
                )}
                aria-label="Close inspector"
              >
                <X className="size-4" />
              </button>
            </div>

            {/* This wrapper is the actual scroll container: min-h-0 lets it
                shrink below its content's natural height inside the flex
                column above, flex-1 lets it fill the remaining space, and
                overflow-y-auto is what makes the content scrollable instead
                of silently clipping under the outer overflow-hidden. */}
            <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
              <InspectorPanelBody
                selectedParcel={selectedParcel}
                featuresGenerated={featuresGenerated}
                processing={processing}
                onRunGeneration={runGeneration}
                analysisResults={analysisResults}
                onRunAnalysis={runAnalysis}
                parcels={parcels}
                selectedParcelId={selectedParcelId}
                onSelectParcel={selectParcel}
              />
            </div>
          </aside>
        )}

        {/* Right inspection panel (mobile/tablet drawer) */}
        {inspectorDrawerOpen && (
          <div className="fixed inset-0 z-40 flex justify-end xl:hidden">
            <button
              type="button"
              aria-label="Close inspector"
              onClick={() => setInspectorDrawerOpen(false)}
              className="absolute inset-0 bg-slate-950/30"
            />
            <aside className="relative flex h-full w-80 max-w-[90vw] flex-col border-l border-slate-300 bg-white shadow-lg">
              <div className="flex h-12 shrink-0 items-center justify-between border-b border-slate-200 px-4">
                <div>
                  <p className="text-sm font-semibold">Inspector</p>
                  <p className="text-[11px] text-slate-400">Feature properties</p>
                </div>

                <button
                  type="button"
                  onClick={() => setInspectorDrawerOpen(false)}
                  className={cn(
                    "grid size-8 place-items-center rounded-md text-slate-500 hover:bg-slate-100",
                    FOCUS_RING,
                  )}
                  aria-label="Close inspector"
                >
                  <X className="size-4" />
                </button>
              </div>

              <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
                <InspectorPanelBody
                  selectedParcel={selectedParcel}
                  featuresGenerated={featuresGenerated}
                  processing={processing}
                  onRunGeneration={runGeneration}
                  analysisResults={analysisResults}
                  onRunAnalysis={runAnalysis}
                  parcels={parcels}
                  selectedParcelId={selectedParcelId}
                  onSelectParcel={selectParcel}
                />
              </div>
            </aside>
          </div>
        )}

        {!rightPanelOpen && (
          <button
            type="button"
            onClick={() => setRightPanelOpen(true)}
            className={cn(
              "absolute right-4 top-4 z-20 hidden size-9 place-items-center border border-slate-300 bg-white text-slate-600 shadow-sm transition-colors hover:bg-slate-50 active:bg-slate-100 xl:grid",
              FOCUS_RING,
            )}
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
          <span className="hidden sm:inline">{layers.length} layers</span>
        </div>

        <div className="flex items-center gap-4">
          <span className="hidden sm:inline">{processing ? "Processing" : "Ready"}</span>
          <span>Zoom {zoom}</span>
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
  disabled = false,
}: {
  children: ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={label}
      aria-label={label}
      aria-pressed={active}
      disabled={disabled}
      className={cn(
        "mb-1 grid size-9 place-items-center rounded-md transition-colors",
        FOCUS_RING,
        disabled
          ? "cursor-not-allowed text-slate-300"
          : active
            ? "bg-slate-950 text-white active:bg-slate-800"
            : "text-slate-500 hover:bg-slate-100 hover:text-slate-900 active:bg-slate-200",
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
