import { useState } from 'react'
import Controls from './components/Controls'
import ErrorChart from './components/ErrorChart'
import ForecastChart from './components/ForecastChart'
import Metrics from './components/Metrics'
import { useAccuracy, useForecast } from './hooks/useWindData'
import './App.css'

const DEFAULTS = {
  date: '2026-01-15',
  cutoff: '09:00',
  dateFrom: '2026-01-01',
  dateTo: '2026-01-31',
}

function Status({ loading, error, children }) {
  if (error) return <p className="status status--error">{error}</p>
  if (loading) return <p className="status">Loading…</p>
  return children
}

export default function App() {
  const [params, setParams] = useState(DEFAULTS)
  const forecast = useForecast({ date: params.date, cutoff: params.cutoff })
  const accuracy = useAccuracy({
    dateFrom: params.dateFrom,
    dateTo: params.dateTo,
    cutoff: params.cutoff,
  })

  return (
    <main className="page">
      <header className="page__head">
        <h1>Wind forecast vs actual</h1>
        <p>
          GB wind generation. Each half-hour uses the latest forecast published
          before the cutoff on the day before delivery. All times UTC.
        </p>
      </header>

      <Controls values={params} onChange={setParams} />

      <section>
        <h2>Accuracy, {params.dateFrom} to {params.dateTo}</h2>
        <Status loading={accuracy.loading} error={accuracy.error}>
          {accuracy.data && <Metrics data={accuracy.data} />}
        </Status>
      </section>

      <section>
        <h2>{params.date}</h2>
        <Status loading={forecast.loading} error={forecast.error}>
          {forecast.data && (
            <>
              <ForecastChart rows={forecast.data} />
              <h3>Forecast error (forecast minus actual)</h3>
              <ErrorChart rows={forecast.data} />
            </>
          )}
        </Status>
      </section>
    </main>
  )
}