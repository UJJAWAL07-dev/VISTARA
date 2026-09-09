import { useEffect, useRef } from "react";
import L from "leaflet";

import type {
  Building,
  LandUseZone,
  Layer,
  Parcel,
  Road,
} from "@/types/dashboard";

type SelectedFeature =
  | { type: "parcel"; id: string }
  | { type: "building"; id: string }
  | { type: "road"; id: string }
  | { type: "land-use"; id: string }
  | null;

type MapGridProps = {
  layers: Layer[];
  parcels: Parcel[];
  buildings: Building[];
  roads: Road[];
  landUseZones: LandUseZone[];
  selectedFeature: SelectedFeature;
  zoom: number;
  onZoomChange: (zoom: number) => void;
  onResetView: () => void;
  onSelectFeature: (feature: NonNullable<SelectedFeature>) => void;
};

const DEFAULT_CENTER: L.LatLngExpression = [18.5204, 73.8567];
const DEFAULT_ZOOM = 16;

/*
 * The current prototype geometry uses local/sample coordinates such as
 * [72, 15]. We transform those coordinates into a small area around Pune
 * until the backend supplies real geographic coordinates.
 */
function toLatLng(position: [number, number]): L.LatLngExpression {
  const [x, y] = position;

  const longitude = 73.84 + (x - 70) * 0.003;
  const latitude = 18.50 + (y - 10) * 0.003;

  return [latitude, longitude];
}

function polygonCoordinates(
  coordinates: [number, number][][],
): L.LatLngExpression[][] {
  return coordinates.map((ring) => ring.map(toLatLng));
}

function lineCoordinates(
  coordinates: [number, number][],
): L.LatLngExpression[] {
  return coordinates.map(toLatLng);
}

function isLayerVisible(layers: Layer[], id: string) {
  return layers.some((layer) => layer.id === id && layer.visible);
}

export default function MapGrid({
  layers,
  parcels,
  buildings,
  roads,
  landUseZones,
  selectedFeature,
  zoom,
  onZoomChange,
  onSelectFeature,
}: MapGridProps) {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const featureLayerRef = useRef<L.LayerGroup | null>(null);

  const onZoomChangeRef = useRef(onZoomChange);
  const onSelectFeatureRef = useRef(onSelectFeature);

  useEffect(() => {
    onZoomChangeRef.current = onZoomChange;
  }, [onZoomChange]);

  useEffect(() => {
    onSelectFeatureRef.current = onSelectFeature;
  }, [onSelectFeature]);

  /*
   * Create the Leaflet map once.
   */
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) {
      return;
    }

    const map = L.map(mapContainerRef.current, {
      center: DEFAULT_CENTER,
      zoom: DEFAULT_ZOOM,
      zoomControl: false,
      attributionControl: true,
    });

    L.tileLayer(
      "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      {
        maxZoom: 20,
        attribution:
          '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      },
    ).addTo(map);

    featureLayerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    map.on("zoomend", () => {
      onZoomChangeRef.current(map.getZoom());
    });

    return () => {
      map.remove();
      mapRef.current = null;
      featureLayerRef.current = null;
    };
  }, []);

  /*
   * Keep Leaflet zoom synchronized with dashboard state.
   */
  useEffect(() => {
    const map = mapRef.current;

    if (!map) {
      return;
    }

    if (map.getZoom() !== zoom) {
      map.setZoom(zoom, { animate: false });
    }
  }, [zoom]);

  /*
   * Draw all currently visible GIS layers.
   */
  useEffect(() => {
    const group = featureLayerRef.current;

    if (!group) {
      return;
    }

    group.clearLayers();

    // Parcels
    if (isLayerVisible(layers, "parcels")) {
      parcels.forEach((parcel) => {
        const polygon = L.polygon(
          polygonCoordinates(parcel.geometry.coordinates),
          {
            color:
              parcel.status === "Validated" ? "#16a34a" : "#d97706",
            weight: 2,
            fillColor:
              parcel.status === "Validated" ? "#22c55e" : "#f59e0b",
            fillOpacity: 0.12,
          },
        );

        polygon.on("click", () => {
          onSelectFeatureRef.current({
            type: "parcel",
            id: parcel.id,
          });
        });

        polygon.bindTooltip(parcel.id, {
          sticky: true,
        });

        polygon.addTo(group);
      });
    }

    // Buildings
    if (isLayerVisible(layers, "buildings")) {
      buildings.forEach((building) => {
        const polygon = L.polygon(
          polygonCoordinates(building.geometry.coordinates),
          {
            color: "#2563eb",
            weight: 1.5,
            fillColor: "#3b82f6",
            fillOpacity: 0.3,
          },
        );

        polygon.on("click", () => {
          onSelectFeatureRef.current({
            type: "building",
            id: building.id,
          });
        });

        polygon.bindTooltip(building.id, {
          sticky: true,
        });

        polygon.addTo(group);
      });
    }

    // Roads
    if (isLayerVisible(layers, "roads")) {
      roads.forEach((road) => {
        const line = L.polyline(
          lineCoordinates(road.geometry.coordinates),
          {
            color: "#475569",
            weight: 4,
            opacity: 0.85,
          },
        );

        line.on("click", () => {
          onSelectFeatureRef.current({
            type: "road",
            id: road.id,
          });
        });

        line.bindTooltip(road.id, {
          sticky: true,
        });

        line.addTo(group);
      });
    }

    // Land use
    if (isLayerVisible(layers, "land-use")) {
      landUseZones.forEach((zone) => {
        const polygon = L.polygon(
          polygonCoordinates(zone.geometry.coordinates),
          {
            color: "#7c3aed",
            weight: 1.5,
            fillColor: "#8b5cf6",
            fillOpacity: 0.12,
            dashArray: "5 4",
          },
        );

        polygon.on("click", () => {
          onSelectFeatureRef.current({
            type: "land-use",
            id: zone.id,
          });
        });

        polygon.bindTooltip(`${zone.id} · ${zone.category}`, {
          sticky: true,
        });

        polygon.addTo(group);
      });
    }
  }, [
    layers,
    parcels,
    buildings,
    roads,
    landUseZones,
  ]);

  /*
   * Highlight the currently selected feature.
   */
  useEffect(() => {
    const group = featureLayerRef.current;

    if (!group || !selectedFeature) {
      return;
    }

    const selectedId = selectedFeature.id;

    group.eachLayer((layer) => {
      const leafletLayer = layer as L.Path;

      if (!leafletLayer.options) {
        return;
      }

      const tooltip = (layer as L.Layer & {
        getTooltip?: () => L.Tooltip | undefined;
      }).getTooltip?.();

      const tooltipText = tooltip?.getContent();

      if (
        typeof tooltipText === "string" &&
        tooltipText.includes(selectedId)
      ) {
        leafletLayer.setStyle({
          weight: 4,
          fillOpacity: 0.3,
          opacity: 1,
        });

        if ("bringToFront" in leafletLayer) {
          (
            leafletLayer as L.Path & {
              bringToFront: () => void;
            }
          ).bringToFront();
        }
      }
    });
  }, [selectedFeature, layers]);

  return (
    <div className="absolute inset-0 overflow-hidden bg-slate-100">
      <div
        ref={mapContainerRef}
        className="h-full w-full"
        aria-label="VISTARA WebGIS map"
      />
    </div>
  );
}