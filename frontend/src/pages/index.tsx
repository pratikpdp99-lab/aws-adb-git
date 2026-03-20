import { useEffect, useState } from "react";
import DatasetCard from "../components/DatasetCard";

interface Dataset {
  id: string;
  name: string;
  domain: string;
  environment: string;
  row_count: number;
  masking_applied: boolean;
}

export default function Home() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  useEffect(() => {
    fetch(`${apiUrl}/datasets/`)
      .then((r) => r.json())
      .then((data) => setDatasets(data.datasets ?? []));
  }, [apiUrl]);

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>TDM Deckers</h1>
      <p>Test Data Management Platform — Retail</p>
      <h2>Available Datasets</h2>
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        {datasets.map((ds) => (
          <DatasetCard key={ds.id} dataset={ds} />
        ))}
        {datasets.length === 0 && <p>No datasets found.</p>}
      </div>
    </main>
  );
}
