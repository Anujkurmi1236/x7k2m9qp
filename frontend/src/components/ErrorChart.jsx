import { Bar, BarChart, Cell, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { hhmm } from './ForecastChart'

export default function ErrorChart({ rows }) {
  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={rows} syncId="day" margin={{ top: 4, right: 12, bottom: 0, left: 0 }}>
        <CartesianGrid stroke="var(--line)" vertical={false} />
        <XAxis dataKey="startTime" tickFormatter={hhmm} minTickGap={40} stroke="var(--muted)" />
        <YAxis tickFormatter={(v) => `${v / 1000}k`} stroke="var(--muted)" width={44} />
        <ReferenceLine y={0} stroke="var(--muted)" />
        <Tooltip
          labelFormatter={(l) => `${hhmm(l)} UTC`}
          formatter={(v) => [v == null ? '–' : `${Math.round(v).toLocaleString('en-GB')} MW`, 'Error']}
        />
        <Bar dataKey="error" isAnimationActive={false}>
          {rows.map((r) => (
            <Cell key={r.startTime} fill={r.error >= 0 ? 'var(--over)' : 'var(--under)'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}