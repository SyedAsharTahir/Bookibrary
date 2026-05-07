import React, { useEffect, useState } from "react";
import API from "../api/axios";

function Recommendations() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await API.get("recommendations/?limit=8");
      setItems(res.data.recommendations || []);
    } catch (err) {
      setError("Failed to load recommendations.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-2">
      <h1 className="text-2xl font-bold mb-2">AI Book Recommendations</h1>
      <p className="text-gray-500 mb-6">
        Personalized suggestions based on borrowing history, preferred category,
        and author patterns.
      </p>

      {loading && <p>Loading recommendations...</p>}
      {error && <p className="text-red-600">{error}</p>}

      {!loading && !error && items.length === 0 && (
        <p>No recommendations yet. Borrow a few books first.</p>
      )}

      {!loading && !error && items.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {items.map((book) => (
            <div
              key={book.id}
              className="border border-gray-200 rounded-lg p-4 shadow-sm bg-white"
            >
              <h2 className="font-semibold text-lg mb-1">{book.title}</h2>
              <p className="text-sm text-gray-600">
                Author: {book["author__name"] || "Unknown"}
              </p>
              <p className="text-sm text-gray-600">
                Category: {book["category__name"] || "Uncategorized"}
              </p>
              <p className="text-sm text-gray-600">
                Publisher: {book["publisher__name"] || "Unknown"}
              </p>
              <p className="text-sm text-gray-700 mt-2">
                Available: {book.quantity}
              </p>
              <div className="mt-3 flex gap-2 text-xs">
                <span className="bg-indigo-100 text-indigo-700 px-2 py-1 rounded">
                  AI Score: {book.ai_score ?? 0}
                </span>
                <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded">
                  Popularity: {book.popularity ?? 0}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Recommendations;
