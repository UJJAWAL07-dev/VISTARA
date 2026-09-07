import { MapPin, RotateCcw, ZoomIn, ZoomOut } from "lucide-react";
import type { Layer, LayerId, Parcel } from "@/types/dashboard";
import { cn } from "@/lib/utils";

const DEFAULT_ZOOM = 14;

const FOCUS_RING =
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-900";

const PARCEL_POSITIONS: Record<
  string,
  { left: string; top: string }
> = {
  "P-1042": { left: "70%", top: "32%" },
  "P-1043": { left: "39%", top: "43%" },
  "P-1044": { left: "50%", top: "62%" },
  "P-1045": { left: "25%", top: "72%" },
  "P-1046": { left: "80%", top: "48%" },
  "P-1047": { left: "30%", top: "55%" },
};

interface MapGridProps {
  layers: Layer[];
  parcels: Parcel[];
  selectedParcelId: string | null;
  zoom: number;
  onZoomChange: (zoom: number) => void;
  onResetView: () => void;
  onSelectParcel: (parcelId: string) => void;
}

function MapGrid({
  layers,
  parcels,
  selectedParcelId,
  zoom,
  onZoomChange,
  onResetView,
  onSelectParcel,
}: MapGridProps) {
  const isLayerVisible = (id: LayerId) =>
    layers.find((layer) => layer.id === id)?.visible ?? false;

  const scale = zoom / DEFAULT_ZOOM;

  const zoomIn = () => {
    onZoomChange(Math.min(20, zoom + 1));
  };

  const zoomOut = () => {
    onZoomChange(Math.max(10, zoom - 1));
  };

  return (
    <div className="relative h-full w-full overflow-hidden bg-slate-100">
      {/* Map controls */}
      <div className="absolute left-4 top-4 z-20 flex flex-col overflow-hidden rounded-md border border-slate-200 bg-white shadow-sm">
        <button
          type="button"
          title="Zoom in"
          aria-label="Zoom in"
          onClick={zoomIn}
          disabled={zoom >= 20}
          className={cn(
            "flex h-10 w-10 items-center justify-center border-b border-slate-200 text-slate-700 transition-colors hover:bg-slate-50 active:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40",
            FOCUS_RING
          )}
        >
          <ZoomIn className="h-4 w-4" />
        </button>

        <button
          type="button"
          title="Zoom out"
          aria-label="Zoom out"
          onClick={zoomOut}
          disabled={zoom <= 10}
          className={cn(
            "flex h-10 w-10 items-center justify-center text-slate-700 transition-colors hover:bg-slate-50 active:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40",
            FOCUS_RING
          )}
        >
          <ZoomOut className="h-4 w-4" />
        </button>
      </div>

      {/* Reset view */}
      <button
        type="button"
        onClick={onResetView}
        title="Reset map view"
        className={cn(
          "absolute right-4 top-4 z-20 flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50 active:bg-slate-100",
          FOCUS_RING
        )}
      >
        <RotateCcw className="h-4 w-4" />
        Reset view
      </button>

      {/* Scalable map surface */}
      <div
        className="absolute inset-0 origin-center transition-transform duration-200"
        style={{
          transform: `scale(${scale})`,
        }}
      >
        {/* Grid */}
        <div
          className="absolute inset-0 opacity-80"
          style={{
            backgroundImage:
              "linear-gradient(to right, rgba(100,116,139,0.12) 1px, transparent 1px), linear-gradient(to bottom, rgba(100,116,139,0.12) 1px, transparent 1px)",
            backgroundSize: "28px 28px",
          }}
        />

        {/* Roads */}
        {isLayerVisible("roads") && (
          <>
            <div className="absolute left-[-10%] top-[48%] h-10 w-[120%] rotate-[-10deg] bg-white shadow-sm" />
            <div className="absolute left-[15%] top-[-20%] h-[140%] w-8 rotate-[24deg] bg-white shadow-sm" />
            <div className="absolute left-[65%] top-[-20%] h-[140%] w-8 rotate-[24deg] bg-white shadow-sm" />
          </>
        )}

        {/* Land use */}
        {isLayerVisible("land-use") && (
          <>
            <div className="absolute left-[8%] top-[16%] h-[23%] w-[25%] bg-emerald-100/35" />
            <div className="absolute left-[42%] top-[48%] h-[25%] w-[28%] bg-amber-100/35" />
            <div className="absolute left-[72%] top-[15%] h-[28%] w-[20%] bg-blue-100/35" />
          </>
        )}

        {/* Building footprints */}
        {isLayerVisible("buildings") && (
          <>
            <div className="absolute left-[10%] top-[17%] h-[18%] w-[18%] border border-slate-500/70 bg-white/30" />

            <div className="absolute left-[35%] top-[12%] h-[17%] w-[22%] border border-slate-500/70 bg-white/30" />

            <div className="absolute left-[68%] top-[16%] h-[19%] w-[16%] border border-slate-500/70 bg-white/30" />

            <div className="absolute left-[22%] top-[58%] h-[20%] w-[20%] border border-slate-500/70 bg-white/30" />

            <div className="absolute left-[48%] top-[54%] h-[15%] w-[16%] border border-slate-500/70 bg-white/30" />

            <div className="absolute left-[74%] top-[57%] h-[22%] w-[14%] border border-slate-500/70 bg-white/30" />
          </>
        )}

        {/* Parcel markers */}
        {isLayerVisible("parcels") &&
          parcels.map((parcel) => {
            const position =
              PARCEL_POSITIONS[parcel.id] ?? {
                left: "50%",
                top: "50%",
              };

            const isSelected = parcel.id === selectedParcelId;

            return (
              <button
                key={parcel.id}
                type="button"
                aria-label={`Select parcel ${parcel.id}`}
                title={parcel.id}
                onClick={() => onSelectParcel(parcel.id)}
                className={cn(
                  "absolute z-10 -translate-x-1/2 -translate-y-full rounded-full transition-transform hover:scale-110 active:scale-95",
                  FOCUS_RING,
                  isSelected && "z-20"
                )}
                style={{
                  left: position.left,
                  top: position.top,
                }}
              >
                <MapPin
                  className={cn(
                    "drop-shadow-sm",
                    isSelected
                      ? "h-6 w-6 fill-white stroke-slate-900 stroke-[2.5]"
                      : "h-5 w-5 fill-slate-700 stroke-white stroke-[1.5]"
                  )}
                />
              </button>
            );
          })}
      </div>

      {/* Map workspace label */}
      <div className="absolute left-5 top-24 z-10 border border-slate-200 bg-white px-4 py-3 shadow-sm">
        <p className="text-[11px] font-medium uppercase tracking-[0.14em] text-slate-400">
          Map workspace
        </p>

        <p className="mt-1 text-sm font-medium text-slate-900">
          Generated cadastral features
        </p>
      </div>

      {/* Bottom map information */}
      <div className="absolute bottom-4 left-5 z-10 border border-slate-200 bg-white px-3 py-2 text-xs text-slate-600 shadow-sm">
        Sample urban cadastral workspace
      </div>

      <div className="absolute bottom-4 right-5 z-10 flex border border-slate-200 bg-white text-xs text-slate-600 shadow-sm">
        <span className="border-r border-slate-200 px-3 py-2">100 m</span>
        <span className="px-3 py-2">EPSG:4326</span>
      </div>
    </div>
  );
}

export default MapGrid;