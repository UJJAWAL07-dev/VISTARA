export type LayerId =
  | "parcels"
  | "buildings"
  | "roads"
  | "land-use";

export type Layer = {
  id: LayerId;
  name: string;
  type: string;
  visible: boolean;
};

export type ParcelStatus = "Validated" | "Review";

export type Position = [number, number];

export type PolygonGeometry = {
  type: "Polygon";
  coordinates: Position[][];
};

export type Parcel = {
  id: string;
  area: string;
  landUse: string;
  confidence: number;
  status: ParcelStatus;
  geometry: PolygonGeometry;
};

export type ToolId =
  | "select"
  | "layers"
  | "inspect"
  | "generate"
  | "analysis"
  | "validation";

export type AnalysisResults = {
  parcelsDetected: number;
  buildingsDetected: number;
  validationIssues: number;
};