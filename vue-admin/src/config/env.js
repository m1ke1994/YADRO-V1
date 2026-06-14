const legacyApiBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim()
const configuredBackendUrl = String(import.meta.env.VITE_BACKEND_URL || legacyApiBaseUrl).trim()
const configuredApiUrl = String(
  import.meta.env.VITE_API_URL || (configuredBackendUrl ? `${configuredBackendUrl}/api` : ''),
).trim()
const configuredSiteUrl = String(
  import.meta.env.VITE_PUBLIC_SITE_URL || import.meta.env.VITE_SITE_URL || configuredBackendUrl,
).trim()

if (!configuredApiUrl || !configuredBackendUrl || !configuredSiteUrl) {
  throw new Error('VITE_API_URL, VITE_BACKEND_URL and VITE_SITE_URL must be set')
}

export const BACKEND_URL = configuredBackendUrl.replace(/\/+$/, '')
export const API_URL = configuredApiUrl.replace(/\/+$/, '')
export const SITE_URL = configuredSiteUrl.replace(/\/+$/, '')

export function toPublicUrl(value) {
  const normalized = String(value || '').trim().replace(/\/+$/, '')
  if (!normalized || /^https?:\/\//i.test(normalized)) {
    return normalized
  }

  let protocol = 'http:'
  try {
    protocol = new URL(SITE_URL).protocol || protocol
  } catch (_) {
    // SITE_URL is validated by the required configuration check above.
  }
  return `${protocol}//${normalized}`
}
