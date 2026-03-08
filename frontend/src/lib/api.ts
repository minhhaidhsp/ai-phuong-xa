import axios from 'axios'

const BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000') + '/api/v1'

export const api = axios.create({
  baseURL: BASE,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) config.headers.Authorization = 'Bearer ' + token
  }
  return config
})

api.interceptors.response.use(res => res, err => {
  if (err.response?.status === 401 && typeof window !== 'undefined') {
    localStorage.removeItem('access_token')
    window.location.href = '/login'
  }
  return Promise.reject(err)
})

export const authApi = {
  login: (u: string, p: string) => {
    const f = new URLSearchParams()
    f.append('username', u); f.append('password', p)
    return api.post('/auth/login', f, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
  },
  me: () => api.get('/auth/me'),
}

export const hoSoApi = {
  list:     (p?: object) => api.get('/ho-so', { params: p }),
  get:      (id: string) => api.get('/ho-so/' + id),
  traCuu:   (ma: string) => api.get('/ho-so/tra-cuu/' + ma),
  tiepNhan: (d: unknown) => api.post('/ho-so/tiep-nhan', d),
  update:   (id: string, d: unknown) => api.put('/ho-so/' + id, d),
}

export const ragApi = {
  query:  (question: string) => api.post('/rag/query', { question }),
  search: (query: string, limit?: number) => api.post('/rag/search', { query, limit }),
}

export const agentsApi = {
  classify: (d: unknown) => api.post('/agents/classify', d),
  validate: (d: unknown) => api.post('/agents/validate', d),
  draft:    (d: unknown) => api.post('/agents/draft', d),
}

export const reportApi = {
  dashboard:   () => api.get('/report/dashboard'),
  alerts:      () => api.get('/report/alerts'),
  thang:       (p?: object) => api.get('/report/thang', { params: p }),
  exportExcel: (p?: object) => api.get('/report/export/excel', { params: p, responseType: 'blob' }),
  exportPdf:   (p?: object) => api.get('/report/export/pdf',   { params: p, responseType: 'blob' }),
}

export const nhiemVuApi = {
  list:   (p?: object) => api.get('/nhiem-vu', { params: p }),
  get:    (id: string) => api.get('/nhiem-vu/' + id),
  create: (d: unknown) => api.post('/nhiem-vu', d),
  update: (id: string, d: unknown) => api.put('/nhiem-vu/' + id, d),
  kpiMe:  () => api.get('/kpi/me'),
  kpi:    (p?: object) => api.get('/kpi', { params: p }),
}

export const lgspApi = {
  status:     () => api.get('/lgsp/status'),
  ingest:     () => api.post('/lgsp/ingest'),
  syncStatus: (d: unknown) => api.post('/lgsp/sync-status', d),
}

export const ragasApi = {
  testSet:        () => api.get('/ragas/test-set'),
  evaluateSample: (d: unknown) => api.post('/ragas/evaluate-sample', d),
  runEval:        (d: unknown) => api.post('/ragas/run-eval', d),
}
