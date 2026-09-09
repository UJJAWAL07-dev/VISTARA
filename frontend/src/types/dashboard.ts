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

export type Building = {
  id: string;
  geometry: PolygonGeometry;
};

export type Road = {
  id: string;
  geometry: {
    type: "LineString";
    coordinates: Position[];
  };
};

export type LandUseZone = {
  id: string;
  category: string;
  geometry: PolygonGeometry;
};

export type ToolId =
  | "select"
  | "layers"
  | "inspect"
  | "generate"
  | "analysis"
  | "validation";

export type ValidationIssueSeverity = "low" | "medium" | "high";

export type ValidationIssueFeatureType = "parcel" | "building";

export type ValidationIssue = {
  id: string;
  featureType: ValidationIssueFeatureType;
  featureId: string;
  severity: ValidationIssueSeverity;
  title: string;
  message: string;
};

export type AnalysisResults = {
  parcelsDetected: number;
  buildingsDetected: number;
  validationIssues: number;
  issues: ValidationIssue[];
};