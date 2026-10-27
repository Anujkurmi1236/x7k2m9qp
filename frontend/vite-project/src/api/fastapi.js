import axios from 'axios'

const fastApiBaseUrl = import.meta.env.VITE_FASTAPI_BASE_URL
const normalizedBaseUrl = (fastApiBaseUrl || 'http://127.0.0.1:8000').replace(
  /\/+$/,
  '',
)

export const fastApiClient = axios.create({
  baseURL: `${normalizedBaseUrl}/api`,
  headers: {
    Accept: 'application/json',
  },
})

export async function getHealth() {
  const { data } = await fastApiClient.get('/health')
  return data
}

export async function getForecast({ date, cutoff = '09:00' }) {
  const { data } = await fastApiClient.get('/forecast', {
    params: {
      date,
      cutoff,
    },
  })
  return data
}

export async function getAccuracy({ dateFrom, dateTo, cutoff = '09:00' }) {
  const { data } = await fastApiClient.get('/accuracy', {
    params: {
      date_from: dateFrom,
      date_to: dateTo,
      cutoff,
    },
  })
  return data
}
