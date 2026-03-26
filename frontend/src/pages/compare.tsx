/**
 * /compare — Deckers D2C Product Comparator & Recommendation Engine
 *
 * Three sections:
 *  1. Product selector  — filter by brand / category / gender, pick 2–4 products
 *  2. Comparison table  — side-by-side attribute matrix with winner highlighted
 *  3. Recommendation    — scored picks driven by activity, budget, season, segment
 */

import { useEffect, useState } from "react";
import type { User, DeckersProduct, CompareResult, RecommendResult, RecommendRequest } from "../types";
import Badge from "../components/Badge";
import { fetchProducts, compareProducts, getRecommendations } from "../lib/api";
import {
  Search, SlidersHorizontal, BarChart3, Star, Trophy,
  Leaf, ShoppingBag, CheckCircle2, XCircle, Sparkles,
  ChevronDown, ChevronUp,
} from "lucide-react";

interface Props { user: User }

// ── Brand accent colours ───────────────────────────────────────────────────────
const BRAND_COLORS: Record<string, { bg: string; text: string; border: string; dot: string }> = {
  UGG:        { bg: "bg-amber-50",   text: "text-amber-700",   border: "border-amber-300",   dot: "bg-amber-500"   },
  HOKA:       { bg: "bg-indigo-50",  text: "text-indigo-700",  border: "border-indigo-300",  dot: "bg-indigo-500"  },
  Teva:       { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-300", dot: "bg-emerald-500" },
  Sanuk:      { bg: "bg-violet-50",  text: "text-violet-700",  border: "border-violet-300",  dot: "bg-violet-500"  },
  Koolaburra: { bg: "bg-rose-50",    text: "text-rose-700",    border: "border-rose-300",    dot: "bg-rose-500"    },
};

const BRANDS    = ["UGG", "HOKA", "Teva", "Sanuk", "Koolaburra"];
const CATS      = ["boots", "slippers", "road_running", "trail", "sandals", "hiking", "casual"];
const GENDERS   = ["women", "men", "unisex"];
const ACTIVITIES= ["running", "hiking", "casual", "comfort", "outdoor", "trail-running"];
const SEASONS   = ["spring", "summer", "fall", "winter"];
const SEGMENTS  = ["athlete", "outdoor", "casual", "premium"];

// ── Attribute display config ───────────────────────────────────────────────────
const ATTR_META: Record<string, { label: string; icon: React.ReactNode }> = {
  price:               { label: "Price",              icon: <ShoppingBag size={13} /> },
  rating:              { label: "Rating",             icon: <Star size={13} /> },
  review_count:        { label: "Reviews",            icon: <BarChart3 size={13} /> },
  colors_available:    { label: "Colors",             icon: <SlidersHorizontal size={13} /> },
  sustainability_score:{ label: "Sustainability",     icon: <Leaf size={13} /> },
  return_rate_pct:     { label: "Return Rate",        icon: <BarChart3 size={13} /> },
  feature_count:       { label: "Features",           icon: <CheckCircle2 size={13} /> },
  in_stock:            { label: "In Stock",           icon: <CheckCircle2 size={13} /> },
  d2c_exclusive:       { label: "D2C Exclusive",      icon: <Sparkles size={13} /> },
  gender:              { label: "Gender",             icon: <SlidersHorizontal size={13} /> },
  seasons:             { label: "Seasons",            icon: <SlidersHorizontal size={13} /> },
};

function BrandBadge({ brand }: { brand: string }) {
  const c = BRAND_COLORS[brand] ?? { bg: "bg-slate-100", text: "text-slate-600", border: "border-slate-200", dot: "bg-slate-400" };
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold border ${c.bg} ${c.text} ${c.border}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {brand}
    </span>
  );
}

function StarRating({ rating }: { rating: number }) {
  return (
    <span className="inline-flex items-center gap-1 text-amber-500 font-semibold text-sm">
      <Star size={13} fill="currentColor" />
      {rating.toFixed(1)}
    </span>
  );
}

export default function ComparePage({ user: _user }: Props) {
  const [products, setProducts]       = useState<DeckersProduct[]>([]);
  const [loading, setLoading]         = useState(true);
  const [search, setSearch]           = useState("");
  const [filterBrand, setFilterBrand] = useState<string | null>(null);
  const [filterCat, setFilterCat]     = useState<string | null>(null);

  const [selected, setSelected] = useState<string[]>([]);
  const [comparing, setComparing]   = useState(false);
  const [compareResult, setCompareResult] = useState<CompareResult | null>(null);

  // Recommendation filters
  const [recActivity,  setRecActivity]  = useState("");
  const [recBudget,    setRecBudget]    = useState("");
  const [recSeason,    setRecSeason]    = useState("");
  const [recGender,    setRecGender]    = useState("");
  const [recSegment,   setRecSegment]   = useState("");
  const [recLoading,   setRecLoading]   = useState(false);
  const [recResult,    setRecResult]    = useState<RecommendResult | null>(null);
  const [recOpen,      setRecOpen]      = useState(true);

  useEffect(() => {
    fetchProducts().then((p) => { setProducts(p); setLoading(false); });
  }, []);

  const filtered = products.filter((p) => {
    if (filterBrand && p.brand !== filterBrand) return false;
    if (filterCat   && p.category !== filterCat) return false;
    if (search && !p.name.toLowerCase().includes(search.toLowerCase()) &&
        !p.brand.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  function toggleSelect(id: string) {
    setSelected((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= 4)  return prev;   // max 4
      return [...prev, id];
    });
    setCompareResult(null);
  }

  async function runCompare() {
    if (selected.length < 2) return;
    setComparing(true);
    setCompareResult(null);
    const result = await compareProducts(selected);
    setCompareResult(result);
    setComparing(false);
  }

  async function runRecommend() {
    setRecLoading(true);
    const req: RecommendRequest = {};
    if (recActivity)  req.activity         = recActivity;
    if (recBudget)    req.budget_max        = parseFloat(recBudget);
    if (recSeason)    req.season            = recSeason;
    if (recGender)    req.gender            = recGender;
    if (recSegment)   req.customer_segment  = recSegment;
    const result = await getRecommendations(req);
    setRecResult(result);
    setRecLoading(false);
  }

  const selectedProducts = products.filter((p) => selected.includes(p.product_id));

  return (
    <div className="max-w-7xl mx-auto space-y-8">

      {/* ── Page header ──────────────────────────────────────────────────────── */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            <BarChart3 size={20} className="text-brand-600" />
            Product Comparator &amp; Recommender
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Compare Deckers D2C products side-by-side · get AI-scored recommendations
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          {BRANDS.map((b) => <BrandBadge key={b} brand={b} />)}
        </div>
      </div>

      {/* ════════════════════════════════════════════════════════════════════════
          SECTION 1 — Product selector
      ════════════════════════════════════════════════════════════════════════ */}
      <div className="card overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between flex-wrap gap-3">
          <h2 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
            <SlidersHorizontal size={15} className="text-slate-400" />
            Step 1 — Select Products to Compare
            <span className="text-slate-400 font-normal">(pick 2–4)</span>
          </h2>
          <div className="flex items-center gap-2 flex-wrap">
            {/* Search */}
            <div className="relative">
              <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
              <input className="input pl-8 text-xs h-8 w-44" placeholder="Search products…"
                value={search} onChange={(e) => setSearch(e.target.value)} />
            </div>
            {/* Brand filter */}
            <select className="input text-xs h-8 pr-7"
              value={filterBrand ?? ""} onChange={(e) => setFilterBrand(e.target.value || null)}>
              <option value="">All brands</option>
              {BRANDS.map((b) => <option key={b} value={b}>{b}</option>)}
            </select>
            {/* Category filter */}
            <select className="input text-xs h-8 pr-7"
              value={filterCat ?? ""} onChange={(e) => setFilterCat(e.target.value || null)}>
              <option value="">All categories</option>
              {CATS.map((c) => <option key={c} value={c}>{c.replace("_", " ")}</option>)}
            </select>
          </div>
        </div>

        {/* Product grid */}
        <div className="p-5">
          {loading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="h-28 bg-slate-100 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              {filtered.map((p) => {
                const isSelected = selected.includes(p.product_id);
                const isDisabled = !isSelected && selected.length >= 4;
                const c = BRAND_COLORS[p.brand] ?? BRAND_COLORS["UGG"];
                return (
                  <button
                    key={p.product_id}
                    disabled={isDisabled}
                    onClick={() => toggleSelect(p.product_id)}
                    className={`relative text-left p-3.5 rounded-xl border-2 transition-all
                      ${isSelected
                        ? `${c.border} ${c.bg} shadow-sm`
                        : isDisabled
                          ? "border-slate-100 bg-slate-50 opacity-40 cursor-not-allowed"
                          : "border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm"
                      }`}
                  >
                    {isSelected && (
                      <CheckCircle2 size={14} className={`absolute top-2 right-2 ${c.text}`} />
                    )}
                    <BrandBadge brand={p.brand} />
                    <p className="text-xs font-semibold text-slate-800 mt-1.5 leading-snug line-clamp-2">
                      {p.name}
                    </p>
                    <div className="flex items-center justify-between mt-1.5">
                      <StarRating rating={p.rating} />
                      <span className="text-xs font-bold text-slate-700">${p.price}</span>
                    </div>
                    {!p.in_stock && (
                      <span className="text-[10px] text-rose-500 font-medium mt-1 block">Out of stock</span>
                    )}
                  </button>
                );
              })}
              {filtered.length === 0 && (
                <div className="col-span-4 text-center py-10 text-sm text-slate-400">
                  No products match your filters.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Selection bar */}
        {selected.length > 0 && (
          <div className="px-5 py-3 border-t border-slate-100 bg-slate-50 flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs text-slate-500 font-medium">Selected:</span>
              {selectedProducts.map((p) => (
                <span key={p.product_id}
                  className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white
                    border border-slate-200 text-xs font-medium text-slate-700">
                  {p.name}
                  <button onClick={() => toggleSelect(p.product_id)}
                    className="text-slate-400 hover:text-rose-500 transition-colors">
                    <XCircle size={12} />
                  </button>
                </span>
              ))}
            </div>
            <button
              disabled={selected.length < 2 || comparing}
              onClick={runCompare}
              className="btn-primary text-xs disabled:opacity-40 disabled:cursor-not-allowed">
              {comparing ? "Comparing…" : `Compare ${selected.length} Products`}
            </button>
          </div>
        )}
      </div>

      {/* ════════════════════════════════════════════════════════════════════════
          SECTION 2 — Comparison matrix
      ════════════════════════════════════════════════════════════════════════ */}
      {compareResult && (
        <div className="card overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
            <BarChart3 size={15} className="text-brand-600" />
            <h2 className="text-sm font-semibold text-slate-800">Step 2 — Side-by-Side Comparison</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[600px]">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100">
                  <th className="th w-36 text-left">Attribute</th>
                  {compareResult.products.map((p) => {
                    const isWinner = p.product_id === compareResult.recommended_winner;
                    const c = BRAND_COLORS[p.brand] ?? BRAND_COLORS["UGG"];
                    return (
                      <th key={p.product_id}
                        className={`th text-center ${isWinner ? c.bg : ""}`}>
                        <div className="flex flex-col items-center gap-1">
                          {isWinner && (
                            <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5
                              rounded-full ${c.bg} ${c.text} border ${c.border}`}>
                              <Trophy size={9} /> Recommended
                            </span>
                          )}
                          <BrandBadge brand={p.brand} />
                          <span className="text-xs font-semibold text-slate-800 leading-snug max-w-[120px]">
                            {p.name}
                          </span>
                          <StarRating rating={p.rating} />
                        </div>
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {compareResult.matrix.map((row) => {
                  const meta = ATTR_META[row.attribute];
                  return (
                    <tr key={row.attribute} className="hover:bg-slate-50 transition-colors">
                      <td className="td">
                        <div className="flex items-center gap-1.5 text-xs font-medium text-slate-600">
                          {meta?.icon}
                          {meta?.label ?? row.attribute.replace(/_/g, " ")}
                        </div>
                      </td>
                      {compareResult.products.map((p) => {
                        const val     = row.values[p.product_id];
                        const isWin   = row.winner === p.product_id;
                        const c       = BRAND_COLORS[p.brand] ?? BRAND_COLORS["UGG"];
                        return (
                          <td key={p.product_id}
                            className={`td text-center ${isWin ? c.bg : ""}`}>
                            <span className={`text-sm font-semibold ${isWin ? c.text : "text-slate-700"}`}>
                              {val}
                            </span>
                            {isWin && (
                              <Trophy size={10} className={`inline ml-1 ${c.text}`} />
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Feature lists */}
          <div className="px-5 py-4 border-t border-slate-100">
            <p className="text-xs font-semibold text-slate-600 mb-3 uppercase tracking-wide">Key Features</p>
            <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${compareResult.products.length}, 1fr)` }}>
              {compareResult.products.map((p) => {
                const c = BRAND_COLORS[p.brand] ?? BRAND_COLORS["UGG"];
                return (
                  <div key={p.product_id}>
                    <p className={`text-xs font-semibold mb-2 ${c.text}`}>{p.name}</p>
                    <ul className="space-y-1">
                      {p.features.map((f, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-xs text-slate-600">
                          <CheckCircle2 size={11} className={`flex-shrink-0 mt-0.5 ${c.text}`} />
                          {f}
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recommendation callout */}
          <div className="mx-5 mb-5 p-4 rounded-xl bg-brand-50 border border-brand-200">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center flex-shrink-0">
                <Trophy size={14} className="text-white" />
              </div>
              <div>
                <p className="text-xs font-bold text-brand-800 uppercase tracking-wide mb-0.5">
                  TDM Recommendation
                </p>
                <p className="text-sm text-brand-700">{compareResult.recommendation_reason}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ════════════════════════════════════════════════════════════════════════
          SECTION 3 — Recommendation engine
      ════════════════════════════════════════════════════════════════════════ */}
      <div className="card overflow-hidden">
        <button
          onClick={() => setRecOpen((v) => !v)}
          className="w-full px-5 py-4 border-b border-slate-100 bg-slate-50 flex items-center
            justify-between hover:bg-slate-100 transition-colors">
          <h2 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
            <Sparkles size={15} className="text-brand-600" />
            Step 3 — D2C Recommendation Engine
          </h2>
          {recOpen ? <ChevronUp size={15} className="text-slate-400" /> : <ChevronDown size={15} className="text-slate-400" />}
        </button>

        {recOpen && (
          <div className="p-5 space-y-5">
            {/* Filter row */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Activity</label>
                <select className="input text-xs w-full"
                  value={recActivity} onChange={(e) => setRecActivity(e.target.value)}>
                  <option value="">Any activity</option>
                  {ACTIVITIES.map((a) => <option key={a} value={a}>{a}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Max Budget ($)</label>
                <input type="number" min={0} className="input text-xs w-full" placeholder="e.g. 150"
                  value={recBudget} onChange={(e) => setRecBudget(e.target.value)} />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Season</label>
                <select className="input text-xs w-full"
                  value={recSeason} onChange={(e) => setRecSeason(e.target.value)}>
                  <option value="">Any season</option>
                  {SEASONS.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Gender</label>
                <select className="input text-xs w-full"
                  value={recGender} onChange={(e) => setRecGender(e.target.value)}>
                  <option value="">Any</option>
                  {GENDERS.map((g) => <option key={g} value={g}>{g}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-500 mb-1">Customer Segment</label>
                <select className="input text-xs w-full"
                  value={recSegment} onChange={(e) => setRecSegment(e.target.value)}>
                  <option value="">All segments</option>
                  {SEGMENTS.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={runRecommend}
                disabled={recLoading}
                className="btn-primary text-xs disabled:opacity-40">
                {recLoading ? "Finding matches…" : "Get Recommendations"}
              </button>
              {recResult && (
                <span className="text-xs text-slate-400">{recResult.context_summary}</span>
              )}
            </div>

            {/* Results */}
            {recResult && (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {recResult.recommendations.map((rec, idx) => {
                  const p = rec.product;
                  const c = BRAND_COLORS[p.brand] ?? BRAND_COLORS["UGG"];
                  const scoreColor =
                    rec.score >= 85 ? "text-emerald-600 bg-emerald-50 border-emerald-200" :
                    rec.score >= 70 ? "text-amber-600  bg-amber-50  border-amber-200"  :
                                     "text-slate-600  bg-slate-50  border-slate-200";
                  return (
                    <div key={p.product_id}
                      className={`rounded-xl border-2 p-4 space-y-3 ${
                        idx === 0 ? `${c.border} ${c.bg}` : "border-slate-100 bg-white"}`}>
                      {/* Rank + score */}
                      <div className="flex items-center justify-between">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${scoreColor}`}>
                          #{idx + 1} Match · {rec.score.toFixed(0)}/100
                        </span>
                        {idx === 0 && (
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${c.bg} ${c.text} ${c.border}`}>
                            <Trophy size={9} className="inline mr-1" />Top Pick
                          </span>
                        )}
                      </div>

                      {/* Brand + name */}
                      <div>
                        <BrandBadge brand={p.brand} />
                        <p className="text-sm font-bold text-slate-900 mt-1 leading-snug">{p.name}</p>
                        <div className="flex items-center gap-3 mt-1">
                          <StarRating rating={p.rating} />
                          <span className="text-sm font-bold text-slate-700">${p.price}</span>
                          {!p.in_stock && (
                            <Badge label="Out of stock" variant="error" />
                          )}
                          {p.d2c_exclusive && (
                            <Badge label="D2C Only" variant="purple" />
                          )}
                        </div>
                      </div>

                      {/* Match reasons */}
                      <ul className="space-y-1">
                        {rec.match_reasons.slice(0, 3).map((r, i) => (
                          <li key={i} className="flex items-start gap-1.5 text-xs text-slate-600">
                            <CheckCircle2 size={11} className="text-emerald-500 flex-shrink-0 mt-0.5" />
                            {r}
                          </li>
                        ))}
                      </ul>

                      {/* Score bar */}
                      <div>
                        <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                          <span>Match score</span>
                          <span>{rec.score.toFixed(0)}%</span>
                        </div>
                        <div className="h-1.5 rounded-full bg-slate-100 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all ${
                              idx === 0 ? c.dot : "bg-slate-400"
                            }`}
                            style={{ width: `${rec.score}%` }}
                          />
                        </div>
                      </div>

                      {/* Sustainability */}
                      <div className="flex items-center gap-1.5 text-xs text-slate-500">
                        <Leaf size={11} className="text-emerald-500" />
                        Sustainability: <span className="font-semibold text-slate-700">{p.sustainability_score}/100</span>
                        <span className="ml-auto text-slate-400">{p.review_count.toLocaleString()} reviews</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
