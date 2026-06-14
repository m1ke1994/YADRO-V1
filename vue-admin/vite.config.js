import { writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

function xmlEscape(value) {
  return value.replace(/[<>&'"]/g, (character) => ({
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
    "'": '&apos;',
    '"': '&quot;',
  })[character])
}

export default defineConfig(({ mode }) => {
  const fileEnv = loadEnv(mode, process.cwd(), '')
  const siteUrl = String(
    process.env.VITE_PUBLIC_SITE_URL ||
      process.env.VITE_SITE_URL ||
      fileEnv.VITE_PUBLIC_SITE_URL ||
      fileEnv.VITE_SITE_URL ||
      'http://localhost:5173',
  ).replace(/\/+$/, '')

  return {
    plugins: [
      vue(),
      {
        name: 'production-seo-files',
        closeBundle() {
          const robots = [
            'User-agent: *',
            'Allow: /',
            'Disallow: /api/',
            'Disallow: /admin/',
            'Disallow: /dashboard',
            'Disallow: /login',
            'Disallow: /sites/',
            'Disallow: /mini',
            '',
            `Sitemap: ${siteUrl}/sitemap.xml`,
            '',
          ].join('\n')
          const sitemap = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            '  <url>',
            `    <loc>${xmlEscape(siteUrl)}/</loc>`,
            '    <changefreq>weekly</changefreq>',
            '    <priority>1.0</priority>',
            '  </url>',
            '</urlset>',
            '',
          ].join('\n')

          writeFileSync(resolve('dist/robots.txt'), robots, 'utf8')
          writeFileSync(resolve('dist/sitemap.xml'), sitemap, 'utf8')
        },
      },
    ],
  }
})
