import {
  BarChart3,
  CheckCircle2,
  ChevronDown,
  CircleHelp,
  Download,
  FileCheck2,
  Layers3,
  MapPin,
  PanelRight,
  Search,
  Settings2,
  Sparkles,
  Upload,
  X,
} from "lucide-react";

import {
  useEffect,
  useRef,
  useState,
  type ChangeEvent,
  type DragEvent,
  type ReactNode,
} from "react";

import { cn } from "@/lib/utils";

import type {
  AnalysisResults,
  Building,
  LandUseZone,
  Layer,
  LayerId,
  Parcel,
  Road,
  ToolId,
} from "@/types/dashboard";

import LayerListPanel from "@/components/dashboard/LayerListPanel";
import { runCadastralAnalysis } from "@/services/dashboardService";

const FOCUS_RING =
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900 focus-visible:ring-offset-2";

type InspectedFeature =
  | { type: "parcel"; id: string }
  | { type: "building"; id: string }
  | { type: "road"; id: string }
  | { type: "land-use"; id: string };

type UploadedDataset = {
  file: File;
  previewUrl: string | null;
};

const ACCEPTED_IMAGE_EXTENSIONS =
  /\.(jpe?g|png|webp|tiff?)$/i;

const ACCEPTED_IMAGE_TYPES = new Set([
  "image/jpeg",
  "image/png",
  "image/webp",
  "image/tiff",
]);

/*
 * VISTARA starts with an empty workspace.
 *
 * These arrays intentionally contain no mock GIS features.
 * Real parcels, buildings, roads and land-use zones should
 * arrive from the AI/GIS processing pipeline later.
 */
const initialLayers: Layer[] = [];

const initialParcels: Parcel[] = [];

const initialBuildings: Building[] = [];

const initialRoads: Road[] = [];

const initialLandUseZones: LandUseZone[] = [];

/* -------------------------------------------------------
   Helpers
------------------------------------------------------- */

function formatFileSize(bytes: number): string {
  if (bytes === 0) {
    return "0 B";
  }

  const units = ["B", "KB", "MB", "GB"];

  const index = Math.min(
    Math.floor(Math.log(bytes) / Math.log(1024)),
    units.length - 1,
  );

  const value = bytes / Math.pow(1024, index);

  return `${value.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function isAcceptedImagery(file: File): boolean {
  const extensionMatches =
    ACCEPTED_IMAGE_EXTENSIONS.test(file.name);

  const typeMatches =
    !file.type || ACCEPTED_IMAGE_TYPES.has(file.type);

  return extensionMatches && typeMatches;
}

/* -------------------------------------------------------
   Inspector
------------------------------------------------------- */

function InspectorPanelBody({
  selectedFeature,
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
  selectedFeature: InspectedFeature | null;
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
      {/* Selected feature */}
      <div className="border-b border-slate-200 px-5 py-5">
        <div className="flex items-center justify-between">
          <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-slate-400">
            Selected feature
          </p>

          {selectedFeature && (
            <span className="rounded-full bg-slate-100 px-2 py-1 text-[9px] font-semibold uppercase tracking-wide text-slate-500">
              Live selection
            </span>
          )}
        </div>

        {selectedFeature?.type === "parcel" &&
        selectedParcel ? (
          <>
            <div className="mt-3 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-slate-950">
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

            <p className="mt-1 text-[11px] font-medium text-slate-400">
              Parcel
            </p>

            <div className="mt-4 grid grid-cols-2 gap-2.5">
              <Property
                label="Area"
                value={selectedParcel.area}
              />

              <Property
                label="Land use"
                value={selectedParcel.landUse}
              />

              <Property
                label="Confidence"
                value={`${selectedParcel.confidence}%`}
              />

              <Property
                label="Geometry"
                value={selectedParcel.geometry.type}
              />

              <Property
                label="Source"
                value="AI + GIS"
              />
            </div>
          </>
        ) : selectedFeature?.type === "building" ? (
          <>
            <h2 className="mt-2 text-xl font-semibold text-slate-950">
              {selectedFeature.id}
            </h2>

            <p className="mt-1 text-[11px] font-medium text-slate-400">
              Building
            </p>

            <div className="mt-4 grid grid-cols-2 gap-2.5">
              <Property
                label="Type"
                value="Building footprint"
              />

              <Property
                label="Geometry"
                value={
                  initialBuildings.find(
                    (building) =>
                      building.id === selectedFeature.id,
                  )?.geometry.type ?? "Polygon"
                }
              />
            </div>
          </>
        ) : selectedFeature?.type === "road" ? (
          <>
            <h2 className="mt-2 text-xl font-semibold text-slate-950">
              {selectedFeature.id}
            </h2>

            <p className="mt-1 text-[11px] font-medium text-slate-400">
              Road
            </p>

            <div className="mt-4 grid grid-cols-2 gap-2.5">
              <Property
                label="Type"
                value="Road network"
              />

              <Property
                label="Geometry"
                value={
                  initialRoads.find(
                    (road) =>
                      road.id === selectedFeature.id,
                  )?.geometry.type ?? "LineString"
                }
              />
            </div>
          </>
        ) : selectedFeature?.type === "land-use" ? (
          <>
            <h2 className="mt-2 text-xl font-semibold text-slate-950">
              {selectedFeature.id}
            </h2>

            <p className="mt-1 text-[11px] font-medium text-slate-400">
              Land-use zone
            </p>

            <div className="mt-4 grid grid-cols-2 gap-2.5">
              <Property
                label="Category"
                value={
                  initialLandUseZones.find(
                    (zone) =>
                      zone.id === selectedFeature.id,
                  )?.category ?? "Unknown"
                }
              />

              <Property
                label="Geometry"
                value="Polygon"
              />
            </div>
          </>
        ) : (
          <div className="mt-4 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">
            <p className="font-medium text-slate-700">
              No feature selected
            </p>

            <p className="mt-1">
              Generate cadastral features first, then select a
              feature to inspect its properties.
            </p>
          </div>
        )}
      </div>

      {/* Generation */}
      <div className="border-b border-slate-200 px-5 py-5">
        <div className="flex items-center justify-between">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            Generation
          </p>

          <Sparkles className="size-4 text-slate-400" />
        </div>

        <p className="mt-2 text-sm leading-5 text-slate-600">
          {featuresGenerated
            ? "Cadastral features have been generated for this workspace."
            : "Generate cadastral features from the imported drone imagery."}
        </p>

        <button
          type="button"
          onClick={onRunGeneration}
          disabled={processing}
          className={cn(
            "mt-4 flex w-full items-center justify-center gap-2 rounded-md bg-slate-950 px-3 py-2.5 text-sm font-medium text-white transition-colors",
            "hover:bg-slate-800 active:bg-slate-900",
            "disabled:cursor-not-allowed disabled:opacity-50",
            FOCUS_RING,
          )}
        >
          <PlayIcon />

          {featuresGenerated
            ? "Regenerate features"
            : "Generate features"}
        </button>

        {featuresGenerated && !processing && (
          <div className="mt-3 flex items-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
            <CheckCircle2 className="size-4" />

            Features generated successfully.
          </div>
        )}
      </div>

      {/* Analysis */}
      <div className="border-b border-slate-200 px-5 py-5">
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
              value={String(
                analysisResults.validationIssues,
              )}
            />
          </div>
        ) : (
          <div className="mt-4 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">
            Run validation after cadastral features have been
            generated.
          </div>
        )}

        <button
          type="button"
          onClick={onRunAnalysis}
          disabled={
            processing ||
            parcels.length === 0
          }
          className={cn(
            "mt-4 flex w-full items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2.5 text-sm font-medium text-slate-800 transition-colors",
            "hover:bg-slate-50 active:bg-slate-100",
            "disabled:cursor-not-allowed disabled:opacity-50",
            FOCUS_RING,
          )}
        >
          <FileCheck2 className="size-4" />

          {analysisResults
            ? "Re-run validation"
            : "Run validation"}
        </button>

        {analysisResults && !processing && (
          <div className="mt-3 flex items-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
            <CheckCircle2 className="size-4" />

            Validation completed successfully.
          </div>
        )}
      </div>

      {/* Recent parcels */}
      <div className="px-5 py-5">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Recent parcels
        </p>

        {parcels.length === 0 ? (
          <div className="mt-3 rounded-lg border border-dashed border-slate-200 bg-slate-50 px-3 py-4 text-center">
            <p className="text-xs font-medium text-slate-500">
              No parcels yet
            </p>

            <p className="mt-1 text-[11px] leading-5 text-slate-400">
              Generated parcel boundaries will appear here.
            </p>
          </div>
        ) : (
          <div className="mt-2 space-y-1">
            {parcels.map((parcel) => (
              <button
                type="button"
                key={parcel.id}
                onClick={() => onSelectParcel(parcel.id)}
                aria-pressed={
                  selectedParcelId === parcel.id
                }
                className={cn(
                  "flex w-full items-center justify-between rounded-md px-3 py-2 text-left transition-colors",
                  "hover:bg-slate-50 active:bg-slate-100",
                  FOCUS_RING,
                  selectedParcelId === parcel.id &&
                    "bg-slate-100",
                )}
              >
                <span>
                  <span className="block text-xs font-semibold text-slate-800">
                    {parcel.id}
                  </span>

                  <span className="block text-[10px] text-slate-400">
                    {parcel.landUse}
                  </span>
                </span>

                <span className="text-[10px] font-medium text-slate-500">
                  {parcel.confidence}%
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    </>
  );
}

/* -------------------------------------------------------
   Dashboard
------------------------------------------------------- */

export default function DashboardPage() {
  const [layers, setLayers] =
    useState<Layer[]>(initialLayers);

  const [parcels, setParcels] =
    useState<Parcel[]>(initialParcels);

  const [selectedParcelId, setSelectedParcelId] =
    useState<string | null>(null);

  const [selectedFeature, setSelectedFeature] =
    useState<InspectedFeature | null>(null);

  const [rightPanelOpen, setRightPanelOpen] =
    useState(false);

  const [inspectorDrawerOpen, setInspectorDrawerOpen] =
    useState(false);

  const [layersDrawerOpen, setLayersDrawerOpen] =
    useState(false);

  const [activeTool, setActiveTool] =
    useState<ToolId>("select");

  const [processing, setProcessing] =
    useState(false);

  const [processingLabel, setProcessingLabel] =
    useState("");

  const [featuresGenerated, setFeaturesGenerated] =
    useState(false);

  const [analysisResults, setAnalysisResults] =
    useState<AnalysisResults | null>(null);

  const [uploadedDataset, setUploadedDataset] =
    useState<UploadedDataset | null>(null);

  const [uploadError, setUploadError] =
    useState<string | null>(null);

  const [isDragging, setIsDragging] =
    useState(false);

  const fileInputRef =
    useRef<HTMLInputElement>(null);

  const selectedParcel =
    parcels.find(
      (parcel) => parcel.id === selectedParcelId,
    ) ?? null;

  /* -----------------------------------------------------
     Object URL cleanup
  ----------------------------------------------------- */

  useEffect(() => {
    return () => {
      if (uploadedDataset?.previewUrl) {
        URL.revokeObjectURL(
          uploadedDataset.previewUrl,
        );
      }
    };
  }, [uploadedDataset?.previewUrl]);

  /* -----------------------------------------------------
     Layer controls
  ----------------------------------------------------- */

  function toggleLayer(id: LayerId) {
    setLayers((currentLayers) =>
      currentLayers.map((layer) =>
        layer.id === id
          ? {
              ...layer,
              visible: !layer.visible,
            }
          : layer,
      ),
    );
  }

  /* -----------------------------------------------------
     Dataset upload
  ----------------------------------------------------- */

  function handleImportClick() {
    fileInputRef.current?.click();
  }

  function handleFile(file: File) {
    setUploadError(null);

    if (!isAcceptedImagery(file)) {
      setUploadError(
        "Unsupported file type. Please upload JPG, JPEG, PNG, WEBP, TIF or TIFF imagery.",
      );

      return;
    }

    /*
     * Browser image previews work for common web formats.
     * TIFF files are accepted but aren't assumed to be
     * previewable without a TIFF decoder.
     */
    const canPreview =
      file.type === "image/jpeg" ||
      file.type === "image/png" ||
      file.type === "image/webp";

    const previewUrl = canPreview
      ? URL.createObjectURL(file)
      : null;

    setUploadedDataset({
      file,
      previewUrl,
    });

    /*
     * Importing a new dataset invalidates all previous
     * generated/selected state.
     */
    setLayers([]);
    setParcels([]);
    setSelectedParcelId(null);
    setSelectedFeature(null);
    setFeaturesGenerated(false);
    setAnalysisResults(null);

    setRightPanelOpen(false);
    setInspectorDrawerOpen(false);

    setActiveTool("select");
  }

  function handleFileInputChange(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (file) {
      handleFile(file);
    }

    /*
     * Reset the input so the same file can be selected again.
     */
    event.target.value = "";
  }

  function handleDragOver(
    event: DragEvent<HTMLDivElement>,
  ) {
    event.preventDefault();
    event.stopPropagation();

    setIsDragging(true);
  }

  function handleDragLeave(
    event: DragEvent<HTMLDivElement>,
  ) {
    event.preventDefault();
    event.stopPropagation();

    setIsDragging(false);
  }

  function handleDrop(
    event: DragEvent<HTMLDivElement>,
  ) {
    event.preventDefault();
    event.stopPropagation();

    setIsDragging(false);

    const file = event.dataTransfer.files?.[0];

    if (file) {
      handleFile(file);
    }
  }

  /* -----------------------------------------------------
     Selection
  ----------------------------------------------------- */

  function selectParcel(id: string) {
    setSelectedParcelId(id);

    setSelectedFeature({
      type: "parcel",
      id,
    });

    setRightPanelOpen(true);
    setInspectorDrawerOpen(true);
  }

  

  function openToolPanel(tool: ToolId) {
    setActiveTool(tool);

    setRightPanelOpen(true);
    setInspectorDrawerOpen(true);
  }

  /* -----------------------------------------------------
     Generation
  ----------------------------------------------------- */

  function runGeneration() {
    if (!uploadedDataset) {
      setUploadError(
        "Import drone imagery before generating cadastral features.",
      );

      return;
    }

    /*
     * IMPORTANT:
     * The current dashboardService does not yet accept the
     * uploaded image and return real GIS features.
     *
     * Therefore this UI does NOT fabricate parcels.
     *
     * Once the backend/AI contract exists, this function is
     * where the real service call should be connected.
     */
    setUploadError(
      "Cadastral generation is not connected to the imported imagery yet.",
    );
  }

  /* -----------------------------------------------------
     Analysis
  ----------------------------------------------------- */

  async function runAnalysis() {
    if (!uploadedDataset) {
      setUploadError(
        "Import drone imagery before running analysis.",
      );

      return;
    }

    if (parcels.length === 0) {
      setUploadError(
        "Generate cadastral features before running validation.",
      );

      return;
    }

    setProcessing(true);
    setProcessingLabel(
      "Running topology validation...",
    );

    setUploadError(null);

    try {
      const results =
        await runCadastralAnalysis(
          parcels,
          initialBuildings,
        );

      setAnalysisResults(results);
    } catch {
      setUploadError(
        "Processing failed. Please try again.",
      );
    } finally {
      setProcessing(false);
      setProcessingLabel("");
    }
  }

  /* -----------------------------------------------------
     Export
  ----------------------------------------------------- */

  function exportGeoJSON() {
    if (!uploadedDataset) {
      setUploadError(
        "Import imagery before exporting results.",
      );

      return;
    }

    if (parcels.length === 0) {
      setUploadError(
        "There are no generated features to export.",
      );

      return;
    }

    const geojson = {
      type: "FeatureCollection",
      features: parcels.map((parcel) => ({
        type: "Feature",
        properties: {
          id: parcel.id,
          area: parcel.area,
          landUse: parcel.landUse,
          confidence: parcel.confidence,
          status: parcel.status,
        },
        geometry: parcel.geometry,
      })),
    };

    const blob = new Blob(
      [JSON.stringify(geojson, null, 2)],
      {
        type: "application/geo+json",
      },
    );

    const url = URL.createObjectURL(blob);

    const anchor = document.createElement("a");

    anchor.href = url;
    anchor.download = "vistara-cadastral-results.geojson";

    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();

    URL.revokeObjectURL(url);
  }

  /* -----------------------------------------------------
     Dataset object for LayerListPanel
  ----------------------------------------------------- */

  const layerPanelDataset =
    uploadedDataset
      ? {
          name: uploadedDataset.file.name,
          size: formatFileSize(
            uploadedDataset.file.size,
          ),
        }
      : null;

  return (
    <div
      className="flex h-[calc(100vh-4rem)] min-h-[700px] flex-col overflow-hidden bg-[#e9eef2] text-slate-900"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* =================================================
          HEADER
      ================================================= */}

      <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 shadow-[0_1px_8px_rgba(15,23,42,0.05)]">
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
              VISTARA Workspace

              <ChevronDown className="size-3.5 text-slate-400" />
            </button>
          </div>

          <div className="hidden h-7 w-px bg-slate-200 sm:block" />

          <div className="hidden items-center gap-2 text-xs text-slate-500 sm:flex">
            <span
              className={cn(
                "size-2 rounded-full",
                processing
                  ? "bg-amber-500"
                  : uploadedDataset
                    ? "bg-emerald-500"
                    : "bg-slate-300",
              )}
            />

            {processing
              ? "Workspace processing"
              : uploadedDataset
                ? "Imagery loaded"
                : "Workspace ready"}
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

          <div
             className="size-9 overflow-hidden rounded-full border border-slate-300 bg-slate-100"
             title="Profile"
          >
             <img
               src="/public/images/Profile/profile.png"
               alt="Profile"
               className="h-full w-full object-cover"
             />
          </div>
        </div>
      </header>

      {/* =================================================
          MAIN WORKSPACE
      ================================================= */}

      <div className="relative flex min-h-0 flex-1">
        {/* =================================================
            LEFT TOOLBAR
        ================================================= */}

        <aside className="z-20 flex w-[60px] shrink-0 flex-col items-center border-r border-slate-800 bg-slate-950 py-3">
          <ToolButton
            label="Select"
            active={activeTool === "select"}
            onClick={() =>
              setActiveTool("select")
            }
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
            disabled={!uploadedDataset}
            onClick={() =>
              openToolPanel("inspect")
            }
          >
            <Search className="size-4" />
          </ToolButton>

          <div className="my-3 h-px w-7 bg-slate-800" />

          <ToolButton
            label="Generate"
            active={activeTool === "generate"}
            disabled={!uploadedDataset}
            onClick={() =>
              openToolPanel("generate")
            }
          >
            <Sparkles className="size-4" />
          </ToolButton>

          <ToolButton
            label="Analysis"
            active={activeTool === "analysis"}
            disabled={
              !uploadedDataset ||
              parcels.length === 0
            }
            onClick={() =>
              openToolPanel("analysis")
            }
          >
            <BarChart3 className="size-4" />
          </ToolButton>

          <ToolButton
            label="Validation"
            active={activeTool === "validation"}
            disabled={
              !uploadedDataset ||
              parcels.length === 0
            }
            onClick={() =>
              openToolPanel("validation")
            }
          >
            <FileCheck2 className="size-4" />
          </ToolButton>

          <div className="mt-auto">
            <ToolButton
              label={
                parcels.length > 0
                  ? "Export GeoJSON"
                  : "Export unavailable"
              }
              active={false}
              disabled={
                !uploadedDataset ||
                parcels.length === 0
              }
              onClick={exportGeoJSON}
            >
              <Download className="size-4" />
            </ToolButton>
          </div>
        </aside>

        {/* =================================================
            LAYER PANEL — DESKTOP
        ================================================= */}

        <aside
          className={cn(
            "hidden w-[280px] shrink-0 border-r border-slate-200 bg-white lg:block",
            activeTool === "layers"
              ? "border-slate-400 ring-1 ring-inset ring-slate-200"
              : "border-slate-300",
          )}
        >
          <LayerListPanel
            layers={layers}
            onToggleLayer={toggleLayer}
            dataset={layerPanelDataset}
          />
        </aside>

        {/* =================================================
            LAYER PANEL — MOBILE/TABLET
        ================================================= */}

        {layersDrawerOpen && (
          <div className="fixed inset-0 z-40 flex lg:hidden">
            <button
              type="button"
              aria-label="Close layers panel"
              onClick={() =>
                setLayersDrawerOpen(false)
              }
              className="absolute inset-0 bg-slate-950/30"
            />

            <aside className="relative flex h-full w-72 max-w-[85vw] flex-col border-r border-slate-300 bg-white shadow-lg">
              <div className="flex h-10 shrink-0 items-center justify-end border-b border-slate-200 px-2">
                <button
                  type="button"
                  onClick={() =>
                    setLayersDrawerOpen(false)
                  }
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
                <LayerListPanel
                  layers={layers}
                  onToggleLayer={toggleLayer}
                  dataset={layerPanelDataset}
                />
              </div>
            </aside>
          </div>
        )}

        {/* =================================================
            CENTRAL WORKSPACE
        ================================================= */}

        <main
          className={cn(
            "relative min-w-0 flex-1 overflow-hidden",
            isDragging &&
              "bg-slate-100",
          )}
        >
          {!uploadedDataset ? (
            /* ---------------------------------------------
               EMPTY WORKSPACE
            --------------------------------------------- */

            <div
              className={cn(
                "flex h-full items-center justify-center p-6 transition-colors",
                isDragging && "bg-slate-100",
              )}
            >
              <div
                className={cn(
                  "w-full max-w-2xl border border-dashed border-slate-300 bg-white px-8 py-14 text-center shadow-sm transition-all",
                  isDragging &&
                    "border-slate-500 bg-slate-50 shadow-md",
                )}
              >
                <div className="mx-auto grid size-16 place-items-center rounded-xl bg-slate-100 text-slate-600">
                  <Upload className="size-7" />
                </div>

                

                <button
                  type="button"
                  onClick={handleImportClick}
                  className={cn(
                    "mx-auto mt-7 flex items-center gap-2 rounded-lg bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-sm transition-colors",
                    "hover:bg-slate-800 active:bg-slate-900",
                    FOCUS_RING,
                  )}
                >
                  <Upload className="size-4" />
                  Import Imagery
                </button>

                <p className="mt-5 text-xs text-slate-400">
                  JPG · JPEG · PNG · WEBP · TIF · TIFF
                </p>

                <p className="mt-3 text-xs text-slate-400">
                  or drag and drop your imagery anywhere
                  in this workspace
                </p>

                {uploadError && (
                  <div className="mx-auto mt-6 max-w-lg rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-left text-xs text-red-700">
                    {uploadError}
                  </div>
                )}
              </div>
            </div>
          ) : (
            /* ---------------------------------------------
               IMPORTED DATASET WORKSPACE
            --------------------------------------------- */

            <div className="flex h-full flex-col bg-slate-100">
              {/* Dataset header */}
              <div className="flex shrink-0 items-center justify-between border-b border-slate-200 bg-white px-5 py-3">
                <div className="min-w-0">
                  <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                    Imported imagery
                  </p>

                  <p
                    className="mt-1 truncate text-sm font-semibold text-slate-900"
                    title={uploadedDataset.file.name}
                  >
                    {uploadedDataset.file.name}
                  </p>

                  <p className="mt-1 text-[11px] text-slate-400">
                    {formatFileSize(
                      uploadedDataset.file.size,
                    )}
                  </p>
                </div>

                <button
                  type="button"
                  onClick={handleImportClick}
                  className={cn(
                    "flex shrink-0 items-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700",
                    "hover:bg-slate-50",
                    FOCUS_RING,
                  )}
                >
                  <Upload className="size-3.5" />
                  Replace imagery
                </button>
              </div>

              {/* Imagery viewer */}
              <div className="relative min-h-0 flex-1 overflow-auto p-6">
                <div className="flex min-h-full items-center justify-center">
                  {uploadedDataset.previewUrl ? (
                    <div className="relative max-h-full max-w-full overflow-hidden border border-slate-300 bg-white shadow-sm">
                      <img
                        src={
                          uploadedDataset.previewUrl
                        }
                        alt={`Imported drone imagery: ${uploadedDataset.file.name}`}
                        className="block max-h-[calc(100vh-13rem)] max-w-full object-contain"
                      />

                      <div className="absolute left-4 top-4 rounded-md border border-slate-200 bg-white/95 px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500 shadow-sm">
                        Source imagery
                      </div>
                    </div>
                  ) : (
                    <div className="w-full max-w-xl border border-slate-300 bg-white p-8 text-center shadow-sm">
                      <div className="mx-auto grid size-12 place-items-center rounded-lg bg-slate-100 text-slate-500">
                        <Upload className="size-5" />
                      </div>

                      <p className="mt-4 text-sm font-semibold text-slate-800">
                        TIFF imagery imported
                      </p>

                      <p className="mt-2 text-xs leading-5 text-slate-500">
                        The file has been accepted by
                        VISTARA. A browser-native preview
                        is not available for this TIFF
                        file yet.
                      </p>

                      <div className="mx-auto mt-5 max-w-sm rounded-lg bg-slate-50 px-4 py-3 text-left">
                        <div className="flex justify-between gap-4">
                          <span className="text-xs text-slate-400">
                            File
                          </span>

                          <span
                            className="max-w-[65%] truncate text-xs font-medium text-slate-700"
                            title={
                              uploadedDataset.file.name
                            }
                          >
                            {uploadedDataset.file.name}
                          </span>
                        </div>

                        <div className="mt-2 flex justify-between gap-4">
                          <span className="text-xs text-slate-400">
                            Size
                          </span>

                          <span className="text-xs font-medium text-slate-700">
                            {formatFileSize(
                              uploadedDataset.file.size,
                            )}
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Generate CTA */}
                <div className="pointer-events-none absolute bottom-6 left-0 right-0 flex justify-center">
                  <button
                    type="button"
                    onClick={() =>
                      openToolPanel("generate")
                    }
                    disabled={processing}
                    className={cn(
                      "pointer-events-auto flex items-center gap-2 rounded-lg bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-lg transition-colors",
                      "hover:bg-slate-800 active:bg-slate-900",
                      "disabled:cursor-not-allowed disabled:opacity-50",
                      FOCUS_RING,
                    )}
                  >
                    <Sparkles className="size-4" />
                    Generate Cadastral Map
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Drag/drop overlay */}
          {isDragging && (
            <div className="pointer-events-none absolute inset-0 z-20 grid place-items-center bg-slate-950/10">
              <div className="rounded-xl border-2 border-dashed border-slate-500 bg-white/95 px-10 py-8 text-center shadow-lg">
                <Upload className="mx-auto size-8 text-slate-600" />

                <p className="mt-3 text-sm font-semibold text-slate-900">
                  Drop imagery to import
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  JPG, JPEG, PNG, WEBP, TIF or TIFF
                </p>
              </div>
            </div>
          )}

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
                      {processingLabel}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Upload error */}
          {uploadError && uploadedDataset && (
            <div className="absolute bottom-20 left-1/2 z-30 w-[min(520px,calc(100%-2rem))] -translate-x-1/2">
              <div className="flex items-start justify-between gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-xs text-red-700 shadow-md">
                <p>{uploadError}</p>

                <button
                  type="button"
                  onClick={() =>
                    setUploadError(null)
                  }
                  className="shrink-0 rounded p-1 hover:bg-red-100"
                  aria-label="Dismiss error"
                >
                  <X className="size-3.5" />
                </button>
              </div>
            </div>
          )}
        </main>

        {/* =================================================
            RIGHT INSPECTOR — DESKTOP
        ================================================= */}

        {rightPanelOpen && (
          <aside className="hidden w-[360px] shrink-0 flex-col border-l border-slate-200 bg-white xl:flex">
            <div className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 px-5">
              <div>
                <p className="text-sm font-semibold">
                  Inspector
                </p>

                <p className="text-[11px] text-slate-400">
                  Feature properties
                </p>
              </div>

              <button
                type="button"
                onClick={() =>
                  setRightPanelOpen(false)
                }
                className={cn(
                  "grid size-8 place-items-center rounded-md text-slate-500 hover:bg-slate-100 active:bg-slate-200",
                  FOCUS_RING,
                )}
                aria-label="Close inspector"
              >
                <X className="size-4" />
              </button>
            </div>

            <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
              <InspectorPanelBody
                selectedFeature={selectedFeature}
                selectedParcel={selectedParcel}
                featuresGenerated={
                  featuresGenerated
                }
                processing={processing}
                onRunGeneration={
                  runGeneration
                }
                analysisResults={
                  analysisResults
                }
                onRunAnalysis={runAnalysis}
                parcels={parcels}
                selectedParcelId={
                  selectedParcelId
                }
                onSelectParcel={selectParcel}
              />
            </div>
          </aside>
        )}

        {/* =================================================
            RIGHT INSPECTOR — MOBILE/TABLET
        ================================================= */}

        {inspectorDrawerOpen && (
          <div className="fixed inset-0 z-40 flex justify-end xl:hidden">
            <button
              type="button"
              aria-label="Close inspector"
              onClick={() =>
                setInspectorDrawerOpen(false)
              }
              className="absolute inset-0 bg-slate-950/30"
            />

            <aside className="relative flex h-full w-[360px] max-w-[92vw] flex-col border-l border-slate-200 bg-white shadow-2xl">
              <div className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 px-5">
                <div>
                  <p className="text-sm font-semibold">
                    Inspector
                  </p>

                  <p className="text-[11px] text-slate-400">
                    Feature properties
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() =>
                    setInspectorDrawerOpen(
                      false,
                    )
                  }
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
                  selectedFeature={
                    selectedFeature
                  }
                  selectedParcel={
                    selectedParcel
                  }
                  featuresGenerated={
                    featuresGenerated
                  }
                  processing={processing}
                  onRunGeneration={
                    runGeneration
                  }
                  analysisResults={
                    analysisResults
                  }
                  onRunAnalysis={
                    runAnalysis
                  }
                  parcels={parcels}
                  selectedParcelId={
                    selectedParcelId
                  }
                  onSelectParcel={
                    selectParcel
                  }
                />
              </div>
            </aside>
          </div>
        )}

        {/* Open inspector button */}
        {!rightPanelOpen &&
          uploadedDataset && (
            <button
              type="button"
              onClick={() =>
                setRightPanelOpen(true)
              }
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

      {/* =================================================
          STATUS BAR
      ================================================= */}

      <footer className="flex h-8 shrink-0 items-center justify-between border-t border-slate-200 bg-white px-3 text-[10px] text-slate-500">
        <div className="flex items-center gap-4">
          <span>VISTARA WORKSPACE</span>

          <span>
            Dataset:{" "}
            {uploadedDataset
              ? uploadedDataset.file.name
              : "No dataset loaded"}
          </span>

          <span className="hidden sm:inline">
            {layers.length} layers
          </span>
        </div>

        <div className="flex items-center gap-4">
          <span className="hidden sm:inline">
            {processing
              ? "Processing"
              : uploadedDataset
                ? "Imagery loaded"
                : "Waiting for imagery"}
          </span>
        </div>
      </footer>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".jpg,.jpeg,.png,.webp,.tif,.tiff,image/jpeg,image/png,image/webp,image/tiff"
        className="hidden"
        onChange={handleFileInputChange}
      />
    </div>
  );
}

/* -------------------------------------------------------
   UI helpers
------------------------------------------------------- */

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
        "mb-1 grid size-10 place-items-center rounded-lg transition-colors",
        FOCUS_RING,
        disabled
          ? "cursor-not-allowed text-slate-600"
          : active
            ? "bg-white text-slate-950 shadow-sm"
            : "text-slate-400 hover:bg-white/10 hover:text-white active:bg-white/15",
      )}
    >
      {children}
    </button>
  );
}

function Property({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg bg-slate-50 px-3 py-2.5 ring-1 ring-inset ring-slate-200/80">
      <p className="text-[10px] font-medium uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-1 text-xs font-semibold text-slate-800">
        {value}
      </p>
    </div>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between border-b border-slate-100 py-2 last:border-0">
      <span className="text-xs text-slate-500">
        {label}
      </span>

      <span className="text-sm font-semibold text-slate-900">
        {value}
      </span>
    </div>
  );
}

function PlayIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      className="size-4"
      aria-hidden="true"
    >
      <path
        d="M8 5.5v13l10-6.5L8 5.5Z"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}