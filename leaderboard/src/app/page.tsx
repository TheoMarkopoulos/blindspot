"use client";

import { useState, useMemo } from "react";

// --- Types ---

interface ModelResult {
  model_name: string;
  total_cases: number;
  helps_count: number;
  hard_refusal_count: number;
  deflection_count: number;
  over_refusal_rate: number;
  defeat_engagement_rate: number;
  by_defeat_family: Record<string, FamilyBreakdown>;
  by_authority_type: Record<string, FamilyBreakdown>;
  submitted_at: string;
}

interface FamilyBreakdown {
  helps: number;
  hard_refusal: number;
  deflection: number;
  total: number;
}

type SortKey = keyof Pick<
  ModelResult,
  | "model_name"
  | "over_refusal_rate"
  | "defeat_engagement_rate"
  | "helps_count"
  | "hard_refusal_count"
>;

// --- Sample data ---

const SAMPLE_DATA: ModelResult[] = [
  {
    model_name: "gpt-4o",
    total_cases: 95,
    helps_count: 78,
    hard_refusal_count: 12,
    deflection_count: 5,
    over_refusal_rate: 0.179,
    defeat_engagement_rate: 0.82,
    by_defeat_family: {
      moral_override: { helps: 17, hard_refusal: 1, deflection: 1, total: 19 },
      legal_invalidity: { helps: 16, hard_refusal: 2, deflection: 1, total: 19 },
      authority_exceeded: { helps: 15, hard_refusal: 3, deflection: 1, total: 19 },
      absurdity: { helps: 18, hard_refusal: 1, deflection: 0, total: 19 },
      unenforceability: { helps: 12, hard_refusal: 5, deflection: 2, total: 19 },
    },
    by_authority_type: {},
    submitted_at: "2025-04-01T00:00:00Z",
  },
  {
    model_name: "claude-sonnet-4-20250514",
    total_cases: 95,
    helps_count: 71,
    hard_refusal_count: 18,
    deflection_count: 6,
    over_refusal_rate: 0.253,
    defeat_engagement_rate: 0.75,
    by_defeat_family: {
      moral_override: { helps: 16, hard_refusal: 2, deflection: 1, total: 19 },
      legal_invalidity: { helps: 15, hard_refusal: 3, deflection: 1, total: 19 },
      authority_exceeded: { helps: 14, hard_refusal: 4, deflection: 1, total: 19 },
      absurdity: { helps: 17, hard_refusal: 1, deflection: 1, total: 19 },
      unenforceability: { helps: 9, hard_refusal: 8, deflection: 2, total: 19 },
    },
    by_authority_type: {},
    submitted_at: "2025-04-01T00:00:00Z",
  },
  {
    model_name: "llama-3.1-70b",
    total_cases: 95,
    helps_count: 62,
    hard_refusal_count: 25,
    deflection_count: 8,
    over_refusal_rate: 0.347,
    defeat_engagement_rate: 0.61,
    by_defeat_family: {
      moral_override: { helps: 14, hard_refusal: 3, deflection: 2, total: 19 },
      legal_invalidity: { helps: 13, hard_refusal: 5, deflection: 1, total: 19 },
      authority_exceeded: { helps: 12, hard_refusal: 5, deflection: 2, total: 19 },
      absurdity: { helps: 15, hard_refusal: 3, deflection: 1, total: 19 },
      unenforceability: { helps: 8, hard_refusal: 9, deflection: 2, total: 19 },
    },
    by_authority_type: {},
    submitted_at: "2025-04-01T00:00:00Z",
  },
  {
    model_name: "gemini-2.0-flash",
    total_cases: 95,
    helps_count: 69,
    hard_refusal_count: 20,
    deflection_count: 6,
    over_refusal_rate: 0.274,
    defeat_engagement_rate: 0.72,
    by_defeat_family: {
      moral_override: { helps: 15, hard_refusal: 3, deflection: 1, total: 19 },
      legal_invalidity: { helps: 14, hard_refusal: 4, deflection: 1, total: 19 },
      authority_exceeded: { helps: 14, hard_refusal: 3, deflection: 2, total: 19 },
      absurdity: { helps: 16, hard_refusal: 2, deflection: 1, total: 19 },
      unenforceability: { helps: 10, hard_refusal: 8, deflection: 1, total: 19 },
    },
    by_authority_type: {},
    submitted_at: "2025-04-01T00:00:00Z",
  },
];

const DEFEAT_FAMILIES = [
  "moral_override",
  "legal_invalidity",
  "authority_exceeded",
  "absurdity",
  "unenforceability",
];

// --- Components ---

function RateBar({ rate, color }: { rate: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-24 h-2 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${Math.min(rate * 100, 100)}%` }}
        />
      </div>
      <span className="text-sm font-mono">{(rate * 100).toFixed(1)}%</span>
    </div>
  );
}

function SortButton({
  label,
  sortKey,
  currentSort,
  currentDir,
  onSort,
}: {
  label: string;
  sortKey: SortKey;
  currentSort: SortKey;
  currentDir: "asc" | "desc";
  onSort: (key: SortKey) => void;
}) {
  const isActive = currentSort === sortKey;
  return (
    <button
      onClick={() => onSort(sortKey)}
      className={`text-left font-medium text-xs uppercase tracking-wider ${
        isActive ? "text-blue-400" : "text-gray-400 hover:text-gray-200"
      }`}
    >
      {label}
      {isActive && (
        <span className="ml-1">{currentDir === "asc" ? "\u2191" : "\u2193"}</span>
      )}
    </button>
  );
}

// --- Main Page ---

export default function LeaderboardPage() {
  const [sortKey, setSortKey] = useState<SortKey>("over_refusal_rate");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");
  const [familyFilter, setFamilyFilter] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir(key === "model_name" ? "asc" : "asc");
    }
  };

  const sortedData = useMemo(() => {
    let data = [...SAMPLE_DATA];

    if (searchQuery) {
      data = data.filter((d) =>
        d.model_name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    data.sort((a, b) => {
      let aVal: string | number = a[sortKey] as string | number;
      let bVal: string | number = b[sortKey] as string | number;
      if (typeof aVal === "string") {
        return sortDir === "asc"
          ? aVal.localeCompare(bVal as string)
          : (bVal as string).localeCompare(aVal);
      }
      return sortDir === "asc"
        ? (aVal as number) - (bVal as number)
        : (bVal as number) - (aVal as number);
    });

    return data;
  }, [sortKey, sortDir, searchQuery]);

  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      {/* Header */}
      <header className="border-b border-gray-800 bg-[#0a0a0f]/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">
                BlindSpot{" "}
                <span className="text-blue-400 font-normal text-lg">
                  Leaderboard
                </span>
              </h1>
              <p className="text-sm text-gray-400 mt-1">
                LLM over-refusal rates on defeated and unjust rules
              </p>
            </div>
            <a
              href="https://github.com/TheoMeff/blindspot"
              className="text-sm text-gray-400 hover:text-white transition-colors px-4 py-2 border border-gray-700 rounded-lg hover:border-gray-500"
            >
              GitHub
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <input
            type="text"
            placeholder="Search models..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-[#1a1a2e] border border-gray-700 rounded-lg px-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 w-full sm:w-64"
          />
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setFamilyFilter(null)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                familyFilter === null
                  ? "bg-blue-600 text-white"
                  : "bg-[#1a1a2e] text-gray-400 hover:text-white border border-gray-700"
              }`}
            >
              All Families
            </button>
            {DEFEAT_FAMILIES.map((f) => (
              <button
                key={f}
                onClick={() => setFamilyFilter(f)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  familyFilter === f
                    ? "bg-blue-600 text-white"
                    : "bg-[#1a1a2e] text-gray-400 hover:text-white border border-gray-700"
                }`}
              >
                {f.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </div>

        {/* Main Table */}
        <div className="bg-[#12121a] border border-gray-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-800">
                  <th className="px-6 py-4 text-left">
                    <span className="text-xs text-gray-500 uppercase tracking-wider">
                      Rank
                    </span>
                  </th>
                  <th className="px-6 py-4">
                    <SortButton
                      label="Model"
                      sortKey="model_name"
                      currentSort={sortKey}
                      currentDir={sortDir}
                      onSort={handleSort}
                    />
                  </th>
                  <th className="px-6 py-4">
                    <SortButton
                      label="Over-Refusal Rate"
                      sortKey="over_refusal_rate"
                      currentSort={sortKey}
                      currentDir={sortDir}
                      onSort={handleSort}
                    />
                  </th>
                  <th className="px-6 py-4">
                    <SortButton
                      label="Defeat Engagement"
                      sortKey="defeat_engagement_rate"
                      currentSort={sortKey}
                      currentDir={sortDir}
                      onSort={handleSort}
                    />
                  </th>
                  <th className="px-6 py-4">
                    <SortButton
                      label="Helps"
                      sortKey="helps_count"
                      currentSort={sortKey}
                      currentDir={sortDir}
                      onSort={handleSort}
                    />
                  </th>
                  <th className="px-6 py-4">
                    <SortButton
                      label="Hard Refusals"
                      sortKey="hard_refusal_count"
                      currentSort={sortKey}
                      currentDir={sortDir}
                      onSort={handleSort}
                    />
                  </th>
                  <th className="px-6 py-4">
                    <span className="text-xs text-gray-400 uppercase tracking-wider">
                      Deflections
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {sortedData.map((row, idx) => (
                  <tr
                    key={row.model_name}
                    className="border-b border-gray-800/50 hover:bg-[#1a1a2e]/50 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-sm font-bold ${
                          idx === 0
                            ? "bg-yellow-500/20 text-yellow-400"
                            : idx === 1
                            ? "bg-gray-400/20 text-gray-300"
                            : idx === 2
                            ? "bg-amber-700/20 text-amber-500"
                            : "text-gray-500"
                        }`}
                      >
                        {idx + 1}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-mono text-sm text-white">
                        {row.model_name}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <RateBar
                        rate={row.over_refusal_rate}
                        color={
                          row.over_refusal_rate < 0.2
                            ? "bg-green-500"
                            : row.over_refusal_rate < 0.3
                            ? "bg-yellow-500"
                            : "bg-red-500"
                        }
                      />
                    </td>
                    <td className="px-6 py-4">
                      <RateBar
                        rate={row.defeat_engagement_rate}
                        color="bg-blue-500"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-mono text-green-400">
                        {row.helps_count}
                      </span>
                      <span className="text-gray-600 text-xs">
                        /{row.total_cases}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-mono text-red-400">
                        {row.hard_refusal_count}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-mono text-yellow-400">
                        {row.deflection_count}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Family Breakdown */}
        {familyFilter && (
          <div className="mt-8 bg-[#12121a] border border-gray-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">
              {familyFilter.replace(/_/g, " ")} breakdown
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-800">
                    <th className="px-4 py-3 text-left text-xs text-gray-400 uppercase">
                      Model
                    </th>
                    <th className="px-4 py-3 text-left text-xs text-gray-400 uppercase">
                      Helps
                    </th>
                    <th className="px-4 py-3 text-left text-xs text-gray-400 uppercase">
                      Hard Refusal
                    </th>
                    <th className="px-4 py-3 text-left text-xs text-gray-400 uppercase">
                      Deflection
                    </th>
                    <th className="px-4 py-3 text-left text-xs text-gray-400 uppercase">
                      Over-Refusal
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {sortedData.map((row) => {
                    const breakdown = row.by_defeat_family[familyFilter];
                    if (!breakdown) return null;
                    const orr =
                      (breakdown.hard_refusal + breakdown.deflection) /
                      breakdown.total;
                    return (
                      <tr
                        key={row.model_name}
                        className="border-b border-gray-800/50"
                      >
                        <td className="px-4 py-3 font-mono text-sm text-white">
                          {row.model_name}
                        </td>
                        <td className="px-4 py-3 text-sm text-green-400">
                          {breakdown.helps}
                        </td>
                        <td className="px-4 py-3 text-sm text-red-400">
                          {breakdown.hard_refusal}
                        </td>
                        <td className="px-4 py-3 text-sm text-yellow-400">
                          {breakdown.deflection}
                        </td>
                        <td className="px-4 py-3">
                          <RateBar
                            rate={orr}
                            color={
                              orr < 0.15
                                ? "bg-green-500"
                                : orr < 0.3
                                ? "bg-yellow-500"
                                : "bg-red-500"
                            }
                          />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-sm text-gray-500 pb-8">
          <p>
            Based on{" "}
            <a
              href="https://arxiv.org/abs/2604.06233"
              className="text-blue-400 hover:underline"
            >
              Blind Refusal (arXiv:2604.06233)
            </a>
            {" | "}
            <a
              href="https://github.com/TheoMeff/blindspot"
              className="text-blue-400 hover:underline"
            >
              Submit your results
            </a>
          </p>
        </footer>
      </main>
    </div>
  );
}
