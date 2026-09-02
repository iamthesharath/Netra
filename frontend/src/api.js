import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const getCases = () => api.get('/cases').then(r => r.data)

export const getCase = (id) => api.get(`/cases/${id}`).then(r => r.data)

export const createCase = (data) => api.post('/cases', data).then(r => r.data)

export const uploadPhoto = (caseId, file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post(`/cases/${caseId}/photos`, form).then(r => r.data)
}

export const uploadVideo = (caseId, file, cameraName) => {
  const form = new FormData()
  form.append('file', file)
  if (cameraName) form.append('camera_name', cameraName)
  return api.post(`/cases/${caseId}/videos`, form).then(r => r.data)
}

export const triggerScan = (caseId) => api.post(`/cases/${caseId}/scan`).then(r => r.data)

export const verifySighting = (sightingId, verified) =>
  api.patch(`/sightings/${sightingId}/verify`, { verified }).then(r => r.data)

export const deleteCase = (caseId) => api.delete(`/cases/${caseId}`).then(r => r.data)
