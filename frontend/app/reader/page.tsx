'use client'
import { useState, useEffect } from 'react'
import { getTemplates, extractFields, Template, ExtractionResult } from '@/lib/api'

const DOC_TYPES = [
  { value: '', label: 'All types' },
  { value: 'nid', label: 'NID Card' },
  { value: 'birth_cert', label: 'Birth Certificate' },
  { value: 'invoice', label: 'Invoice' },
  { value: 'custom', label: 'Custom' },
]

const ENGINES = [
  { value: 'shobdoocr', label: 'ShobdoOCR' },
  { value: 'tesseract', label: 'Tesseract' },
  { value: 'easyocr', label: 'EasyOCR' },
]

export default function ReaderPage() {
  const [docType, setDocType] = useState('')
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [engine, setEngine] = useState('shobdoocr')
  const [result, setResult] = useState<ExtractionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const list = await getTemplates(docType || undefined)
        setTemplates(list)
        setSelectedTemplate('')
      } catch { setError('Failed to load templates') }
    }
    load()
  }, [docType])

  const handleExtract = async () => {
    if (!imageFile || !selectedTemplate) return
    setLoading(true); setError(''); setResult(null)
    try {
      const res = await extractFields(imageFile, selectedTemplate, engine)
      setResult(res)
    } catch (e) {
      setError('Extraction failed. Check backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (!result) return
    const blob = new Blob([JSON.stringify(result.fields, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `${result.template_name}_extraction.json`
    a.click()
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Template Reader</h1>
      <p className="text-gray-500 text-sm mb-6">
        Select a saved template, upload a document of the same type, and extract structured fields.
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4 mb-6">
        <div className="flex gap-4 flex-wrap">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Document type</label>
            <select value={docType} onChange={e => setDocType(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              {DOC_TYPES.map(d => <option key={d.value} value={d.value}>{d.label}</option>)}
            </select>
          </div>

          <div className="flex-1 min-w-48">
            <label className="block text-sm font-medium text-gray-700 mb-1">Select template</label>
            <select value={selectedTemplate} onChange={e => setSelectedTemplate(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="">-- Select a template --</option>
              {templates.map(t => (
                <option key={t.id} value={t.id}>{t.template_name} ({t.document_type})</option>
              ))}
            </select>
            {templates.length === 0 && (
              <p className="text-xs text-gray-400 mt-1">No templates found. Create one in Template Builder.</p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Upload document image</label>
          <input type="file" accept="image/*" onChange={e => setImageFile(e.target.files?.[0] || null)}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-700 file:font-medium hover:file:bg-blue-100" />
        </div>

        <div className="flex gap-4 items-end flex-wrap">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">OCR Engine</label>
            <select value={engine} onChange={e => setEngine(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
              {ENGINES.map(e => <option key={e.value} value={e.value}>{e.label}</option>)}
            </select>
          </div>

          <button onClick={handleExtract}
            disabled={!imageFile || !selectedTemplate || loading}
            className="px-6 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
            {loading ? 'Extracting...' : 'Extract Fields'}
          </button>
        </div>
      </div>

      {result && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="font-bold text-gray-900">{result.template_name}</h2>
              <p className="text-xs text-gray-500">{result.word_count} words detected · {Object.keys(result.fields).length} fields extracted</p>
            </div>
            <button onClick={handleDownload}
              className="px-4 py-2 text-sm rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium">
              ↓ Download JSON
            </button>
          </div>

          <div className="divide-y divide-gray-100">
            {Object.entries(result.fields).map(([key, value]) => (
              <div key={key} className="py-3 flex gap-4">
                <span className="text-sm font-medium text-gray-600 w-40 flex-shrink-0">{key}</span>
                <span className="text-sm text-gray-900 font-mono">{value || '—'}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
