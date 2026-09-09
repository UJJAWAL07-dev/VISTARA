import {
  Eye,
  EyeOff,
  FileImage,
  Map,
  Upload,
} from "lucide-react";

import { cn } from "@/lib/utils";

import type {
  Layer,
  LayerId,
} from "@/types/dashboard";

const FOCUS_RING =
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2";

export type LayerListDataset = {
  name: string;
  size: string;
};

function LayerListPanel({
  layers,
  onToggleLayer,
  dataset = null,
}: {
  layers: Layer[];
  onToggleLayer: (id: LayerId) => void;
  dataset?: LayerListDataset | null;
}) {
  const visibleLayerCount = layers.filter(
    (layer) => layer.visible,
  ).length;

  return (
    <div className="flex h-full min-h-0 flex-col bg-white">
      {/* ================================
          HEADER
          ================================ */}
      <div className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 px-4">
        <div>
          <p className="text-sm font-semibold text-slate-900">
            Layers
          </p>

          <p className="text-[11px] text-slate-400">
            {visibleLayerCount} visible
          </p>
        </div>

        <button
          type="button"
          className={cn(
            "grid size-8 place-items-center rounded-md text-slate-400",
            FOCUS_RING,
          )}
          aria-label="Add layer"
          title={
            dataset
              ? "Add layer (coming soon)"
              : "Import imagery first"
          }
          disabled
        >
          <Upload className="size-4" />
        </button>
      </div>

      {/* ================================
          DATASET
          ================================ */}
      <div className="border-b border-slate-200 p-3">
        <div className="rounded-lg border border-slate-200 bg-slate-50/80 p-3">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Dataset
              </p>

              {dataset ? (
                <>
                  <p
                    className="mt-1 truncate text-sm font-medium text-slate-900"
                    title={dataset.name}
                  >
                    {dataset.name}
                  </p>

                  <p className="mt-2 text-xs text-slate-500">
                    Urban imagery · {dataset.size}
                  </p>
                </>
              ) : (
                <>
                  <p className="mt-1 text-sm font-medium text-slate-700">
                    No dataset loaded
                  </p>

                  <p className="mt-2 text-xs text-slate-400">
                    Import drone imagery to begin
                  </p>
                </>
              )}
            </div>

            {dataset ? (
              <FileImage className="mt-0.5 size-4 shrink-0 text-slate-400" />
            ) : (
              <Map className="mt-0.5 size-4 shrink-0 text-slate-300" />
            )}
          </div>
        </div>
      </div>

      {/* ================================
          MAP LAYERS
          ================================ */}
      <div className="min-h-0 flex-1 overflow-y-auto p-2">
        <p className="px-2 py-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Map layers
        </p>

        {layers.length === 0 ? (
          <div className="px-3 py-8 text-center">
            <div className="mx-auto grid size-9 place-items-center rounded-md bg-slate-50 text-slate-300">
              <Map className="size-4" />
            </div>

            <p className="mt-3 text-xs font-medium text-slate-500">
              No layers available
            </p>

            <p className="mt-1 text-[11px] leading-5 text-slate-400">
              Layers will appear here after cadastral
              features are generated.
            </p>
          </div>
        ) : (
          layers.map((layer) => (
            <button
              key={layer.id}
              type="button"
              onClick={() => onToggleLayer(layer.id)}
              title={
                layer.visible
                  ? `Hide ${layer.name}`
                  : `Show ${layer.name}`
              }
              aria-label={
                layer.visible
                  ? `Hide ${layer.name}`
                  : `Show ${layer.name}`
              }
              aria-pressed={layer.visible}
              className={cn(
                "flex w-full items-center gap-3 rounded-lg px-2.5 py-2.5 text-left transition-colors",
                "hover:bg-slate-50 active:bg-slate-100",
                FOCUS_RING,
              )}
            >
              {/* Visibility icon */}
              <span className="grid size-7 shrink-0 place-items-center rounded-md bg-slate-50 text-slate-500">
                {layer.visible ? (
                  <Eye className="size-4" />
                ) : (
                  <EyeOff className="size-4 text-slate-300" />
                )}
              </span>

              {/* Layer information */}
              <span className="min-w-0 flex-1">
                <span
                  className={cn(
                    "block truncate text-sm font-medium",
                    !layer.visible && "text-slate-400",
                  )}
                >
                  {layer.name}
                </span>

                <span className="block text-[10px] text-slate-400">
                  {layer.type}
                </span>
              </span>
            </button>
          ))
        )}
      </div>
    </div>
  );
}

export default LayerListPanel;