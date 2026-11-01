import React, { useEffect, useMemo, useState } from "react";
import "./style.css";

const API = "http://127.0.0.1:8000";
const PAGE_ITEMS = [
  ["Overview", "⌂"],
  ["Delivery Performance", "▥"],
  ["Delay Risk", "◈"],
  ["Shipping Modes", "⇄"],
  ["Regional Intelligence", "⌖"],
  ["Customer Segments", "♙"],
  ["Record Explorer", "▤"],
];
const EMPTY_FILTERS = {
  shipping_mode: "", region: "", market: "", segment: "", country: "", outcome: "",
};
const number = (value, digits = 0) => {
  if (value === null || value === undefined || value === "") return "—";
  const n = Number(value);
  if (!Number.isFinite(n)) return "—";
  return (Math.abs(n) < 0.005 ? 0 : n).toLocaleString("en-IN", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
};
const pct = value => value === null || value === undefined ? "—" : `${Number(value).toFixed(1)}%`;
const clean = value => String(value ?? "Unknown").replaceAll("_", " ");

function MetricCard({ icon, label, value, note, tone }) {
  return <article className={`metric-card ${tone}`}>
    <div className="metric-head"><span className="metric-icon">{icon}</span><span>{label}</span></div>
    <strong className="metric-value">{value}</strong>
    <small>{note}</small>
  </article>;
}

function Panel({ title, subtitle, children, className = "" }) {
  return <section className={`panel ${className}`}>
    <div className="panel-heading"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div></div>
    {children}
  </section>;
}

function HorizontalBars({ title, rows = [], labelKey, valueKey = "delay_rate", suffix = "%", onPick, colorize = false }) {
  const max = Math.max(1, ...rows.map(row => Math.max(0, Number(row[valueKey] || 0))));
  return <Panel title={title} subtitle="Select a row to inspect the matching shipment records.">
    <div className="horizontal-bars">
      {rows.slice(0, 10).map((row, index) => {
        const value = Number(row[valueKey] || 0);
        const label = row[labelKey] ?? "Unknown";
        return <button className="horizontal-row" key={`${label}-${index}`} onClick={() => onPick?.(label)}>
          <span className="horizontal-label">{clean(label)}</span>
          <span className="track"><i className={colorize ? `fill fill-${index % 4}` : "fill"} style={{ width: `${Math.max(value > 0 ? 1 : 0, value / max * 100)}%` }} /></span>
          <strong>{number(value, valueKey === "average_gap" ? 2 : 1)}{suffix}</strong>
        </button>;
      })}
      {!rows.length && <div className="empty-state">No matching data is available.</div>}
    </div>
  </Panel>;
}

function OutcomeDonut({ data }) {
  const early = Number(data.early_rate || 0);
  const onTime = Number(data.on_time_rate || 0);
  const delayed = Number(data.delayed_rate || 0);
  const total = Math.max(early + onTime + delayed, 0.0001);
  const earlyEnd = early / total * 100;
  const onTimeEnd = (early + onTime) / total * 100;
  const gradient = `conic-gradient(#19d49a 0 ${earlyEnd}%, #36a9f5 ${earlyEnd}% ${onTimeEnd}%, #ff626e ${onTimeEnd}% 100%)`;
  return <Panel title="Delivery Outcome Mix" subtitle="Share of early, on-time and delayed shipments.">
    <div className="donut-layout">
      <div className="donut" style={{ background: gradient }}>
        <div className="donut-hole"><strong>{number(data.total_shipments)}</strong><span>Shipments</span></div>
      </div>
      <div className="legend">
        <div><i className="dot early"/><span>Early</span><strong>{pct(data.early_rate)}</strong></div>
        <div><i className="dot ontime"/><span>On-time</span><strong>{pct(data.on_time_rate)}</strong></div>
        <div><i className="dot delayed"/><span>Delayed</span><strong>{pct(data.delayed_rate)}</strong></div>
      </div>
    </div>
  </Panel>;
}

function Insights({ rows = [] }) {
  const best = [...rows].sort((a, b) => Number(b.sla_compliance_rate || 0) - Number(a.sla_compliance_rate || 0))[0];
  const worst = [...rows].sort((a, b) => Number(b.delay_rate || 0) - Number(a.delay_rate || 0))[0];
  const gap = [...rows].sort((a, b) => Number(b.average_gap || 0) - Number(a.average_gap || 0))[0];
  const fastest = [...rows].sort((a, b) => Number(a.average_gap || 0) - Number(b.average_gap || 0))[0];
  const insights = [
    best && { icon: "✓", tone: "good", text: `${clean(best["Shipping Mode"])} has the highest SLA compliance (${pct(best.sla_compliance_rate)}).` },
    worst && { icon: "!", tone: "bad", text: `${clean(worst["Shipping Mode"])} has the highest delay rate (${pct(worst.delay_rate)}).` },
    gap && { icon: "↗", tone: "warn", text: `${clean(gap["Shipping Mode"])} has the largest average delivery gap (${number(gap.average_gap, 2)} days).` },
    fastest && { icon: "⌁", tone: "info", text: `${clean(fastest["Shipping Mode"])} has the lowest average delivery gap (${number(fastest.average_gap, 2)} days).` },
  ].filter(Boolean);
  return <Panel title="Key Insights" className="insights-panel">
    <div className="insights-list">{insights.map((item, index) => <div className="insight" key={index}><i className={item.tone}>{item.icon}</i><span>{item.text}</span></div>)}</div>
  </Panel>;
}

function DataTable({ columns, rows }) {
  return <div className="table-wrap"><table><thead><tr>{columns.map(col => <th key={col}>{col}</th>)}</tr></thead>
    <tbody>{rows.map((row, index) => <tr key={row._row_id ?? index}>{columns.map(col => <td key={col}>{row[col] == null ? "—" : String(row[col])}</td>)}</tr>)}</tbody></table>
    {!rows.length && <div className="empty-state">No records match the selected filters.</div>}
  </div>;
}

export default function App() {
  const [page, setPage] = useState("Shipping Modes");
  const [theme, setTheme] = useState("dark");
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [options, setOptions] = useState({});
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [records, setRecords] = useState([]);
  const [recordTotal, setRecordTotal] = useState(0);
  const [recordPage, setRecordPage] = useState(1);
  const [search, setSearch] = useState("");

  const query = useMemo(() => new URLSearchParams(Object.entries(filters).filter(([, value]) => value)), [filters]);

  async function loadDashboard() {
    setLoading(true);
    setError("");
    try {
      const [dashboardResponse, filterResponse] = await Promise.all([
        fetch(`${API}/dashboard?${query.toString()}`), fetch(`${API}/filters`),
      ]);
      if (!dashboardResponse.ok) {
        const body = await dashboardResponse.json().catch(() => ({}));
        throw new Error(body.detail || "Dashboard data could not be loaded");
      }
      if (!filterResponse.ok) throw new Error("Filter options could not be loaded");
      setData(await dashboardResponse.json());
      setOptions(await filterResponse.json());
    } catch (err) {
      setError(err.message || "Unable to connect to the analytics API");
    } finally {
      setLoading(false);
    }
  }

  async function loadRecords() {
    try {
      const params = new URLSearchParams(query);
      params.set("page", String(recordPage));
      params.set("page_size", "20");
      params.set("search", search);
      const response = await fetch(`${API}/records?${params.toString()}`);
      if (!response.ok) throw new Error("Could not load shipment records");
      const result = await response.json();
      setRecords(result.records || []);
      setRecordTotal(result.total || 0);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => { loadDashboard(); }, [query]);
  useEffect(() => { if (page === "Record Explorer") loadRecords(); }, [page, query, recordPage, search]);

  function changeFilter(key, value) {
    setFilters(previous => ({ ...previous, [key]: value }));
    setRecordPage(1);
  }
  function explore(key, value) {
    const filterKey = key === "Shipping Mode" ? "shipping_mode" : key;
    changeFilter(filterKey, value);
    setPage("Record Explorer");
  }
  function resetFilters() {
    setFilters(EMPTY_FILTERS);
    setRecordPage(1);
  }
  function exportCsv() {
    const params = new URLSearchParams(query);
    params.set("search", search);
    window.open(`${API}/records/export?${params.toString()}`, "_blank");
  }

  const shippingRows = data?.shipping_modes || [];
  const recordColumns = records.length ? Object.keys(records[0]) : [];
  const pageSubtitle = {
    "Overview": "A live view of delivery performance across the global supply chain.",
    "Delivery Performance": "Understand planned versus actual shipping duration and delivery outcomes.",
    "Delay Risk": "Explore the dataset's existing late-delivery risk labels and delay exposure.",
    "Shipping Modes": "Compare delivery efficiency, delay risk and SLA performance across shipping modes.",
    "Regional Intelligence": "Identify geographic patterns across regions, markets and countries.",
    "Customer Segments": "Compare delivery outcomes and service exposure across customer segments.",
    "Record Explorer": "Search, inspect and export the filtered shipment-level data.",
  }[page];

  return <div className={`app-shell ${theme}`}>
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark">◇</div><div><strong>LogiScope</strong><small>SUPPLY CHAIN INTELLIGENCE</small></div></div>
      <div className="nav-label">WORKSPACE</div>
      <nav className="navigation">{PAGE_ITEMS.map(([label, icon]) => <button key={label} className={page === label ? "nav-item active" : "nav-item"} onClick={() => setPage(label)}><span>{icon}</span>{label}</button>)}</nav>
      <div className="sidebar-port-image" aria-hidden="true" />
      <div className="sidebar-bottom"><div className="sidebar-promo"><strong>Global Supply Chain Analytics</strong><p>Data-driven delivery insights for operational excellence.</p></div><div className="sidebar-status"><i/> API analytics workspace</div></div>
    </aside>

    <main className="main-content">
      <header className="topbar">
        <div><div className="breadcrumb">⌁ / <strong>{page}</strong></div><h1>{page === "Shipping Modes" ? "Shipping Modes Analysis" : page}</h1><p>{pageSubtitle}</p></div>
        <div className="top-actions"><button className="date-chip" title={options.date_filter_available === false ? "No identifiable date field exists in the supplied dataset" : "Date filtering is available in the dataset"}>▦ &nbsp;{options.date_filter_available === false ? "No Date Range" : "Date Range"}⌄</button><button className="round-action" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} title="Toggle theme">{theme === "dark" ? "☼" : "☾"}</button><button className="round-action" onClick={loadDashboard} title="Refresh dashboard">↻</button><div className="avatar">L</div></div>
      </header>

      <section className="filter-bar">
        {[["shipping_mode", "Shipping Mode", "shipping_modes"], ["region", "Order Region", "regions"], ["market", "Market", "markets"], ["segment", "Customer Segment", "segments"], ["country", "Order Country", "countries"], ["outcome", "Delivery Outcome", null]].map(([key, label, optionKey]) => <label key={key} className="filter-field"><span>{label}</span><select value={filters[key]} onChange={event => changeFilter(key, event.target.value)}><option value="">All</option>{(optionKey ? options[optionKey] || [] : ["Early", "On-time", "Delayed"]).map(value => <option key={value} value={value}>{clean(value)}</option>)}</select></label>)}
        <button className="reset-button" onClick={resetFilters}>↻ &nbsp;Reset</button>
      </section>

      {error && <div className="error-banner">{error}. Check that the FastAPI backend is running at 127.0.0.1:8000.</div>}
      {loading && !data && <div className="loading-state">Loading LogiScope analytics…</div>}

      {data && <>
        <section className="metrics-grid">
          <MetricCard icon="▣" label="Total Shipments" value={number(data.total_shipments)} note="In current filter selection" tone="purple" />
          <MetricCard icon="✓" label="On-time Rate" value={pct(data.on_time_rate)} note={`${number(data.on_time_count)} on-time shipments`} tone="green" />
          <MetricCard icon="!" label="Delayed Rate" value={pct(data.delayed_rate)} note={`${number(data.delayed_count)} delayed shipments`} tone="red" />
          <MetricCard icon="▦" label="Average Delivery Gap" value={`${number(data.average_delay, 2)} days`} note="Actual minus scheduled" tone="blue" />
          <MetricCard icon="△" label="Late Delivery Risk" value={pct(data.late_risk_rate)} note="Existing dataset label" tone="amber" />
        </section>

        {page === "Shipping Modes" && <>
          <section className="analysis-grid three-columns">
            <HorizontalBars title="Delay Rate by Shipping Mode" rows={shippingRows} labelKey="Shipping Mode" valueKey="delay_rate" onPick={value => explore("shipping_mode", value)} colorize />
            <HorizontalBars title="Average Delivery Gap by Shipping Mode" rows={shippingRows} labelKey="Shipping Mode" valueKey="average_gap" suffix=" days" onPick={value => explore("shipping_mode", value)} colorize />
            <OutcomeDonut data={data} />
          </section>
          <section className="lower-grid">
            <Panel title="Shipment Volume and SLA Compliance" subtitle="SLA-compliant shipments are classified as early or on-time against scheduled shipping duration.">
              <div className="table-wrap"><table><thead><tr><th>Shipping Mode</th><th>Total Shipments</th><th>Delayed</th><th>On-time</th><th>Early</th><th>Delay Rate</th><th>SLA Compliance</th></tr></thead><tbody>
                {shippingRows.map((row, index) => <tr key={index}><td><span className={`mode-dot mode-${index % 4}`}/>{clean(row["Shipping Mode"])}</td><td>{number(row.shipments)}</td><td>{number(row.delayed)}</td><td>{number(row.on_time)}</td><td>{number(row.early)}</td><td><span className="pill danger">{pct(row.delay_rate)}</span></td><td><span className={`pill ${Number(row.sla_compliance_rate) >= 50 ? "success" : "danger"}`}>{pct(row.sla_compliance_rate)}</span></td></tr>)}
              </tbody></table></div>
            </Panel>
            <Insights rows={shippingRows} />
          </section>
        </>}

        {page === "Overview" && <>
          <section className="analysis-grid two-columns"><OutcomeDonut data={data}/><HorizontalBars title="Delay Rate by Shipping Mode" rows={shippingRows} labelKey="Shipping Mode" valueKey="delay_rate" onPick={value => explore("shipping_mode", value)}/></section>
          <section className="analysis-grid two-columns"><HorizontalBars title="Regional Delay Rate" rows={data.regions || []} labelKey="Order Region" onPick={value => explore("region", value)}/><HorizontalBars title="Market Delay Rate" rows={data.markets || []} labelKey="Market" onPick={value => explore("market", value)}/></section>
        </>}

        {page === "Delivery Performance" && <>
          <section className="analysis-grid two-columns"><Panel title="Delivery Outcome Summary"><div className="summary-stats"><div><b>{number(data.early_count)}</b><span>Early shipments</span></div><div><b>{number(data.on_time_count)}</b><span>On-time shipments</span></div><div><b>{number(data.delayed_count)}</b><span>Delayed shipments</span></div></div></Panel><Panel title="Duration Gap Distribution" subtitle="Actual shipping days minus scheduled shipping days. Negative = early, zero = on-time, positive = delayed."><div className="histogram">{(data.histogram || []).map((item, index) => <div key={index} title={`${item.range}: ${number(item.count)}`}><i style={{ height: `${Math.max(3, item.count / Math.max(1, ...data.histogram.map(x => x.count)) * 150)}px` }}/><span>{item.range}</span></div>)}</div></Panel></section>
          <div className="notice-banner">Delivery outcomes are calculated from actual shipping days minus scheduled shipping days. The date selector is unavailable because no date column was identified in the supplied data.</div>
        </>}

        {page === "Delay Risk" && <>
          <section className="analysis-grid two-columns"><Panel title="Dataset-provided Risk Labels" subtitle="These are existing dataset labels, not predictions from a trained model."><div className="risk-list">{(data.risk_distribution || []).map(item => <div key={item.label}><span>Risk {item.label}</span><strong>{number(item.count)}</strong></div>)}</div></Panel><HorizontalBars title="Delay Rate by Region" rows={data.regions || []} labelKey="Order Region" onPick={value => explore("region", value)}/></section>
          <div className="notice-banner">Important: late_delivery_risk is an existing dataset label. It should not be presented as a model-generated prediction.</div>
        </>}

        {page === "Regional Intelligence" && <>
          <section className="analysis-grid two-columns"><HorizontalBars title="Region-wise Delay Rate" rows={data.regions || []} labelKey="Order Region" onPick={value => explore("region", value)}/><HorizontalBars title="Market-wise Delay Rate" rows={data.markets || []} labelKey="Market" onPick={value => explore("market", value)}/></section>
          <Panel title="Country-level Delay Index"><div className="table-wrap"><table><thead><tr><th>Country</th><th>Shipments</th><th>Delayed</th><th>Delay Rate</th><th>Average Gap</th></tr></thead><tbody>{(data.countries || []).map((row, index) => <tr key={index}><td>{clean(row["Order Country"])}</td><td>{number(row.shipments)}</td><td>{number(row.delayed)}</td><td>{pct(row.delay_rate)}</td><td>{number(row.average_gap, 2)} days</td></tr>)}</tbody></table></div></Panel>
          <div className="notice-banner">The supplied latitude and longitude fields represent customer locations, not confirmed delivery-destination coordinates. A destination heatmap is therefore not fabricated.</div>
        </>}

        {page === "Customer Segments" && <>
          <section className="analysis-grid two-columns"><HorizontalBars title="Segment-wise Delay Rate" rows={data.segments || []} labelKey="Customer Segment" onPick={value => explore("segment", value)}/><HorizontalBars title="Average Delay Gap by Segment" rows={data.segments || []} labelKey="Customer Segment" valueKey="average_gap" suffix=" days" onPick={value => explore("segment", value)}/></section>
          <Panel title="Customer Segment Delivery Scorecard"><div className="table-wrap"><table><thead><tr><th>Customer Segment</th><th>Shipments</th><th>Delayed</th><th>On-time</th><th>Early</th><th>Delay Rate</th><th>SLA Compliance</th></tr></thead><tbody>{(data.segments || []).map((row, index) => <tr key={index}><td>{clean(row["Customer Segment"])}</td><td>{number(row.shipments)}</td><td>{number(row.delayed)}</td><td>{number(row.on_time)}</td><td>{number(row.early)}</td><td>{pct(row.delay_rate)}</td><td>{pct(row.sla_compliance_rate)}</td></tr>)}</tbody></table></div></Panel>
        </>}

        {page === "Record Explorer" && <>
          <Panel title="Shipment-level Records" subtitle={`${number(recordTotal)} matching rows. Personal customer names and street addresses are excluded.`}>
            <div className="record-tools"><input value={search} onChange={event => { setSearch(event.target.value); setRecordPage(1); }} placeholder="Search product, city, country, region…"/><button className="export-button" onClick={exportCsv}>↓ Export CSV</button></div>
            <DataTable columns={recordColumns} rows={records}/>
            <div className="pagination"><span>Page {recordPage} of {Math.max(1, Math.ceil(recordTotal / 20))}</span><div><button disabled={recordPage <= 1} onClick={() => setRecordPage(value => value - 1)}>Previous</button><button disabled={recordPage * 20 >= recordTotal} onClick={() => setRecordPage(value => value + 1)}>Next</button></div></div>
          </Panel>
        </>}
      </>}

      <footer className="footer"><span>LOGISCOPE · GLOBAL SUPPLY CHAIN INTELLIGENCE</span><span>Operational decision support · Dataset-derived metrics</span></footer>
    </main>
  </div>;
}
