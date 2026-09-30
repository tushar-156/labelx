"use client";

import { useEffect, useState } from "react";
import { useProfile } from "../../store/profile";

export function HistoryPage() {
  const { userId } = useProfile();
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const url = userId ? `/api/history?user_id=${userId}` : "/api/history";
    fetch(url)
      .then(r => r.json())
      .then(data => {
        setHistory(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(e => {
        console.warn("Could not load history:", e);
        setHistory([]);
        setLoading(false);
      });
  }, [userId]);

  const handleExport = (sessionId: string) => {
    const baseUrl = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    window.location.href = `${baseUrl}/export/${sessionId}?format=csv`;
  };

  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-2xl font-semibold text-ink">Scan History</h1>
      <p className="text-inksoft text-sm">Your previous ingredient scan sessions and reports.</p>

      {loading ? (
        <p className="text-inksoft text-sm">Loading history...</p>
      ) : history.length === 0 ? (
        <p className="text-inksoft text-sm">No scan history found. Run a scan to see it here!</p>
      ) : (
        <div className="flex flex-col gap-3">
          {history.map((h, i) => (
            <div key={i} className="flex items-center justify-between p-4 border border-line rounded-lg bg-surface">
              <div>
                <p className="font-mono text-sm text-ink font-semibold">{h.id}</p>
                <p className="text-xs text-inksoft mt-1">{new Date(h.created_at).toLocaleString()}</p>
              </div>
              <button 
                onClick={() => handleExport(h.id)}
                className="px-4 py-1.5 border border-line rounded-md text-sm text-ink hover:bg-line/20 transition-colors"
              >
                Export CSV
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
