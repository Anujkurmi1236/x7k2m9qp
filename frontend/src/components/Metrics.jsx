const fmt = (n, digits = 0) =>
  Number(n).toLocaleString('en-GB', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })

export default function Metrics({ data }) {
  const items = [
    { label: 'Mean absolute error', value: `${fmt(data.mae)} MW`, note: `${fmt(data.mae_pct_of_mean, 1)}% of mean output` },
    { label: 'RMSE', value: `${fmt(data.rmse)} MW`, note: 'Penalises large misses' },
    {
      label: 'Bias',
      value: `${data.bias > 0 ? '+' : ''}${fmt(data.bias)} MW`,
      note: data.bias > 0 ? 'Forecast runs high' : 'Forecast runs low',
    },
    { label: '90th percentile error', value: `${fmt(data.p90_abs_error)} MW`, note: '1 in 10 half-hours is worse' },
    { label: 'Mean actual output', value: `${fmt(data.mean_actual)} MW`, note: `${fmt(data.count)} half-hours compared` },
  ]

  return (
    <dl className="metrics">
      {items.map((m) => (
        <div key={m.label} className="metric">
          <dt>{m.label}</dt>
          <dd>{m.value}</dd>
          <p>{m.note}</p>
        </div>
      ))}
    </dl>
  )
}