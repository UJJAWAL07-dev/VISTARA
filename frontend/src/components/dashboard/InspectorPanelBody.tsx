import {
  BarChart3,
  CheckCircle2,
  FileCheck2,
  Play,
  Sparkles,
} from "lucide-react";

import { cn } from "@/lib/utils";

import type {
  AnalysisResults,
  Building,
  LandUseZone,
  Parcel,
  Road,
  ValidationIssue,
} from "@/types/dashboard";

const FOCUS_RING =
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2";

export type InspectedFeature =
  | { type: "parcel"; id: string }
  | { type: "building"; id: string }
  | { type: "road"; id: string }
  | { type: "land-use"; id: string };

type InspectorPanelBodyProps = {
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
  onSelectFeature: (feature: InspectedFeature) => void;
  buildings: Building[];
  roads: Road[];
  landUseZones: LandUseZone[];
};

export default function InspectorPanelBody({
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
  onSelectFeature,
  buildings,
  roads,
  landUseZones,
}: InspectorPanelBodyProps) {
  const validParcels = parcels.filter(
    (parcel) => parcel.status === "Validated",
  ).length;

  const reviewParcels = parcels.filter(
    (parcel) => parcel.status === "Review",
  ).length;

 const totalArea = parcels.reduce(
  (total, parcel) => total + Number(parcel.area),
  0,
);
  const averageParcelArea =
    parcels.length > 0 ? Math.round(totalArea / parcels.length) : 0;

  return (
    <>
      {/* Selected feature */}
      <div className="border-b border-slate-200 px-5 py-4">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Selected feature
        </p>

        {selectedFeature?.type === "parcel" && selectedParcel ? (
          <>
            <div className="mt-3 flex items-start justify-between gap-3">
              <h2 className="text-lg font-semibold tracking-tight text-slate-950">
                {selectedParcel.id}
              </h2>

              <span
                className={cn(
                  "rounded-full border px-2.5 py-1 text-[10px] font-semibold",
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

            <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50/50 px-3">
              <Property label="Area" value={selectedParcel.area} />
              <Property label="Land use" value={selectedParcel.landUse} />
              <Property
                label="Confidence"
                value={`${selectedParcel.confidence}%`}
              />
              <Property
                label="Geometry"
                value={selectedParcel.geometry.type}
              />
              <Property label="Source" value="AI + GIS" />
            </div>
          </>
        ) : selectedFeature?.type === "building" ? (
          <>
            <h2 className="mt-3 text-lg font-semibold tracking-tight text-slate-950">
              {selectedFeature.id}
            </h2>

            <p className="mt-1 text-[11px] font-medium text-slate-400">
              Building
            </p>

            <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50/50 px-3">
              <Property label="Type" value="Building footprint" />

              <Property
                label="Geometry"
                value={
                  buildings.find(
                    (building) => building.id === selectedFeature.id,
                  )?.geometry.type ?? "Polygon"
                }
              />
            </div>
          </>
        ) : selectedFeature?.type === "road" ? (
          <>
            <h2 className="mt-3 text-lg font-semibold tracking-tight text-slate-950">
              {selectedFeature.id}
            </h2>

            <p className="mt-1 text-[11px] font-medium text-slate-400">
              Road
            </p>

            <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50/50 px-3">
              <Property label="Type" value="Road network" />

              <Property
                label="Geometry"
                value={
                  roads.find((road) => road.id === selectedFeature.id)
                    ?.geometry.type ?? "LineString"
                }
              />
            </div>
          </>
        ) : selectedFeature?.type === "land-use" ? (
          <>
            <h2 className="mt-3 text-lg font-semibold tracking-tight text-slate-950">
              {selectedFeature.id}
            </h2>

            <p className="mt-1 text-[11px] font-medium text-slate-400">
              Land-use zone
            </p>

            <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50/50 px-3">
              <Property
                label="Category"
                value={
                  landUseZones.find(
                    (zone) => zone.id === selectedFeature.id,
                  )?.category ?? "Unknown"
                }
              />

              <Property label="Geometry" value="Polygon" />
            </div>
          </>
        ) : (
          <div className="mt-3 rounded-lg border border-dashed border-slate-300 bg-slate-50/50 p-4 text-sm text-slate-500">
            <p className="font-medium text-slate-700">No feature selected</p>
            <p className="mt-1">
              Select a feature on the map to inspect its properties.
            </p>
          </div>
        )}
      </div>

      {/* Generation */}
      <div className="border-b border-slate-200 px-5 py-4">
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
            "mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-slate-950 px-3 py-2.5 text-sm font-medium text-white transition-colors hover:bg-slate-800 active:bg-slate-900 disabled:cursor-not-allowed disabled:opacity-50",
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

           {/* Analysis */}
      <div className="border-b border-slate-200 px-5 py-4">
        <div className="flex items-center justify-between">
          <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
            Analysis
          </p>

          <BarChart3 className="size-4 text-slate-400" />
        </div>

        {analysisResults ? (
          <>
            <div className="mt-3 grid grid-cols-2 gap-2">
              <Metric
                label="Total parcels"
                value={parcels.length.toLocaleString()}
              />

              <Metric
                label="Valid parcels"
                value={validParcels.toLocaleString()}
              />

              <Metric
                label="Needs review"
                value={reviewParcels.toLocaleString()}
              />

              <Metric
                label="Buildings"
                value={analysisResults.buildingsDetected.toLocaleString()}
              />

              <Metric
                label="Total area"
                value={`${totalArea.toLocaleString()} m²`}
              />

              <Metric
                label="Avg. parcel area"
                value={`${averageParcelArea.toLocaleString()} m²`}
              />
            </div>

            <div className="mt-2">
              <Metric
                label="Validation issues"
                value={analysisResults.validationIssues}
              />
            </div>
          </>
        ) : (
          <div className="mt-3 rounded-lg border border-dashed border-slate-300 bg-slate-50/50 p-4 text-sm text-slate-500">
            <p className="font-medium text-slate-700">
              Analysis not run yet
            </p>

            <p className="mt-1 text-xs leading-5">
              Run validation to calculate parcel statistics and identify
              spatial issues.
            </p>
          </div>
        )}

        <button
          type="button"
          onClick={onRunAnalysis}
          disabled={processing || !featuresGenerated}
          className={cn(
            "mt-4 flex w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm font-medium text-slate-800 transition-colors hover:bg-slate-50 active:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50",
            FOCUS_RING,
          )}
        >
          <FileCheck2 className="size-4" />

          {analysisResults ? "Re-run validation" : "Run validation"}
        </button>

        {!featuresGenerated && (
          <p className="mt-2 text-center text-[10px] text-slate-400">
            Generate features before running validation.
          </p>
        )}

        {analysisResults && !processing && (
          <div className="mt-3 flex items-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
            <CheckCircle2 className="size-4" />
            Validation completed successfully.
          </div>
        )}

        {analysisResults && analysisResults.issues.length > 0 && (
          <div className="mt-4">
            <div className="flex items-center justify-between">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Issues
              </p>

              <span className="text-[10px] font-semibold text-slate-500">
                {analysisResults.issues.length}
              </span>
            </div>

            <div className="mt-2 space-y-2">
              {analysisResults.issues.map((issue: ValidationIssue) => (
                <button
                  key={issue.id}
                  type="button"
                  onClick={() =>
                    onSelectFeature({
                      type: issue.featureType,
                      id: issue.featureId,
                    })
                  }
                  className={cn(
                    "w-full rounded-lg border border-slate-200 bg-white p-3 text-left transition-colors hover:bg-slate-50 active:bg-slate-100",
                    FOCUS_RING,
                  )}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-slate-900">
                        {issue.title}
                      </p>

                      <p className="mt-1 text-[11px] leading-4 text-slate-500">
                        {issue.message}
                      </p>
                    </div>

                    <span
                      className={cn(
                        "shrink-0 rounded-full px-2 py-1 text-[9px] font-bold uppercase tracking-wide",
                        issue.severity === "high"
                          ? "bg-red-50 text-red-700"
                          : issue.severity === "medium"
                            ? "bg-amber-50 text-amber-700"
                            : "bg-slate-100 text-slate-600",
                      )}
                    >
                      {issue.severity}
                    </span>
                  </div>

                  <p className="mt-2 text-[10px] font-semibold text-slate-400">
                    {issue.featureId} · Select to inspect
                  </p>
                </button>
              ))}
            </div>
          </div>
        )}

        {analysisResults &&
          analysisResults.issues.length === 0 &&
          !processing && (
            <div className="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3">
              <p className="text-xs font-semibold text-emerald-800">
                No validation issues detected.
              </p>

              <p className="mt-1 text-[11px] leading-4 text-emerald-700">
                The current demo dataset passed the available frontend
                validation checks.
              </p>
            </div>
          )}
      </div>

      {/* Recent parcels */}
      <div className="px-5 py-4">
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
                "flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-left transition-colors hover:bg-slate-50 active:bg-slate-100",
                FOCUS_RING,
                selectedParcelId === parcel.id && "bg-slate-100",
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
      </div>
    </>
  );
}

function Property({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="flex items-center justify-between border-b border-slate-200 py-2.5 last:border-b-0">
      <span className="text-xs text-slate-400">{label}</span>
      <span className="text-xs font-medium text-slate-700">{value}</span>
    </div>
  );
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-slate-50/50 px-3 py-2.5">
      <span className="text-xs text-slate-500">{label}</span>
      <span className="text-sm font-semibold text-slate-900">{value}</span>
    </div>
  );
}