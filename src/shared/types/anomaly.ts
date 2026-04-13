export type AnomalySeverity = "low" | "medium" | "high" | "critical";

export interface Anomaly {
  anomaly_id: string;
  start_time: string;
  end_time: string;
  impact_amount: number;
  severity: AnomalySeverity;
  root_cause_summary: string;
  likely_drivers: string[];
  likely_owner: string;
  data_freshness_timestamp: string;
}
