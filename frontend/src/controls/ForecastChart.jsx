import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export const hhmm = (iso) => new Date(iso).toISOString().slice(11, 16)
const mw = (v) => (v == null ? '–' : `${Math.round(v).toLocaleString('en-GB')} MW`)

export default function ForecastChart({ rows }) {
  return (
    <ResponsiveContainer width="100%" height={340}>
      <LineChart data={rows} syncId="day" margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
        <CartesianGrid stroke="var(--line)" vertical={false} />
        <XAxis dataKey="startTime" tickFormatter={hhmm} minTickGap={40} stroke="var(--muted)" />
        <YAxis tickFormatter={(v) => `${v / 1000}k`} stroke="var(--muted)" width={44} />
        <Tooltip
          labelFormatter={(l) => `${hhmm(l)} UTC`}
          formatter={(v, name) => [mw(v), name]}
        />
        <Legend verticalAlign="top" align="right" height={32} iconType="plainline" />
        <Line name="Forecast" dataKey="forecast" stroke="var(--forecast)" strokeWidth={2} strokeDasharray="5 4" dot={false} />
        <Line name="Actual" dataKey="actual" stroke="var(--actual)" strokeWidth={2.5} dot={false} connectNulls={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}