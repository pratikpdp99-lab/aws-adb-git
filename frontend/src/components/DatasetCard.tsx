interface Dataset {
  id: string;
  name: string;
  domain: string;
  environment: string;
  row_count: number;
  masking_applied: boolean;
}

export default function DatasetCard({ dataset }: { dataset: Dataset }) {
  return (
    <div style={{
      border: "1px solid #ccc",
      borderRadius: 8,
      padding: "1rem",
      minWidth: 220,
      background: "#f9f9f9",
    }}>
      <h3 style={{ margin: "0 0 0.5rem" }}>{dataset.name}</h3>
      <p style={{ margin: 0 }}>Domain: <strong>{dataset.domain}</strong></p>
      <p style={{ margin: 0 }}>Env: <strong>{dataset.environment}</strong></p>
      <p style={{ margin: 0 }}>Rows: <strong>{dataset.row_count.toLocaleString()}</strong></p>
      <p style={{ margin: 0 }}>Masked: <strong>{dataset.masking_applied ? "Yes" : "No"}</strong></p>
    </div>
  );
}
