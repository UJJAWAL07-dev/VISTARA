import type {
  AnalysisResults,
  Building,
  Parcel,
  ValidationIssue,
} from "@/types/dashboard";

/**
 * Runs cadastral feature generation.
 *
 * This is intentionally a local mock for now.
 * A real GIS/API implementation can replace this function later
 * without changing DashboardPage's UI logic.
 */
export async function generateCadastralFeatures(
  generatedParcels: Parcel[],
): Promise<Parcel[]> {
  await new Promise((resolve) => {
    window.setTimeout(resolve, 1800);
  });

  return generatedParcels;
}

/**
 * Runs analysis/validation against the current dataset.
 *
 * The calculations are derived from the actual feature arrays,
 * rather than hardcoded dashboard numbers.
 */
export async function runCadastralAnalysis(
  parcels: Parcel[],
  buildings: Building[],
): Promise<AnalysisResults> {
  await new Promise((resolve) => {
    window.setTimeout(resolve, 1200);
  });

  const issues: ValidationIssue[] = [];

  parcels.forEach((parcel) => {
    if (parcel.status === "Review") {
      issues.push({
        id: `VAL-${parcel.id}`,
        featureType: "parcel",
        featureId: parcel.id,
        severity: "medium",
        title: "Parcel requires review",
        message: "This parcel is marked for manual review before approval.",
      });
    }

    if (parcel.confidence < 90) {
      issues.push({
        id: `CONF-${parcel.id}`,
        featureType: "parcel",
        featureId: parcel.id,
        severity: "high",
        title: "Low confidence",
        message: `Feature confidence is ${parcel.confidence}%, below the 90% validation threshold.`,
      });
    }

    const ring = parcel.geometry.coordinates[0] ?? [];
    const first = ring[0];
    const last = ring[ring.length - 1];
    const isClosed =
      ring.length >= 4 &&
      first !== undefined &&
      last !== undefined &&
      first[0] === last[0] &&
      first[1] === last[1];

    if (!isClosed) {
      issues.push({
        id: `GEOM-${parcel.id}`,
        featureType: "parcel",
        featureId: parcel.id,
        severity: "high",
        title: "Invalid parcel geometry",
        message: "The polygon ring is not closed and should be repaired before export.",
      });
    }
  });

  buildings.forEach((building) => {
    const ring = building.geometry.coordinates[0] ?? [];
    const first = ring[0];
    const last = ring[ring.length - 1];
    const isClosed =
      ring.length >= 4 &&
      first !== undefined &&
      last !== undefined &&
      first[0] === last[0] &&
      first[1] === last[1];

    if (!isClosed) {
      issues.push({
        id: `GEOM-${building.id}`,
        featureType: "building",
        featureId: building.id,
        severity: "high",
        title: "Invalid building geometry",
        message: "The building polygon ring is not closed and should be repaired.",
      });
    }
  });

  return {
    parcelsDetected: parcels.length,
    buildingsDetected: buildings.length,
    validationIssues: issues.length,
    issues,
  };
}