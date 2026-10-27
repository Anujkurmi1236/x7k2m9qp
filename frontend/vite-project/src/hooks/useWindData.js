import { useEffect, useState } from 'react'
import { getAccuracy, getForecast } from '../api/fastapi'

function useRequest(request, deps) {
  const [state, setState] = useState({ data: null, loading: true, error: null })

  useEffect(() => {
    let live = true
    setState((s) => ({ ...s, loading: true, error: null }))
    request()
      .then((data) => live && setState({ data, loading: false, error: null }))
      .catch((err) => {
        if (!live) return
        const message = err.response?.data?.detail ?? err.message
        setState({ data: null, loading: false, error: message })
      })
    return () => {
      live = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return state
}

export function useForecast({ date, cutoff }) {
  return useRequest(() => getForecast({ date, cutoff }), [date, cutoff])
}

export function useAccuracy({ dateFrom, dateTo, cutoff }) {
  return useRequest(
    () => getAccuracy({ dateFrom, dateTo, cutoff }),
    [dateFrom, dateTo, cutoff],
  )
}