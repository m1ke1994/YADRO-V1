import http from './http'

export async function listMediaFiles({ site, fileType, search = '' }) {
  const { data } = await http.get('/api/client/media/', {
    params: {
      site,
      file_type: fileType,
      search: search || undefined,
    },
  })
  return Array.isArray(data) ? data : data?.results || []
}

export async function uploadMediaFile({ file, site, section, field }) {
  const formData = new FormData()
  formData.append('file', file)
  if (site !== undefined && site !== null && site !== '') {
    formData.append('site', String(site))
  }
  if (section !== undefined && section !== null && section !== '') {
    formData.append('section', String(section))
  }
  if (field !== undefined && field !== null && field !== '') {
    formData.append('field', String(field))
  }

  const { data } = await http.post('/api/uploads/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return data
}

export async function updateMediaFile(id, payload) {
  const { data } = await http.patch(`/api/client/media/${id}/`, payload)
  return data
}

export async function deleteMediaFile(id) {
  await http.delete(`/api/client/media/${id}/`)
}
