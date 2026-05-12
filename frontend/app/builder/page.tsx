'use client'
import { useState, useRef } from 'react'
import ImageAnnotator from '@/components/ImageAnnotator'
import { processOCR, saveTemplate, WordBox, TemplateField } from '@/lib/api'

const DOC_TYPES = [
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

export default function BuilderPage() {
  const [step, setStep] = useState(1)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imageUrl, setImageUrl] = useState('')
  const [imageSize, setImageSize] = useState({ width: 1, height: 1 })
  const [words, setWords] = useState<WordBox[]>([])
  const [fields, setFields] = useState<TemplateField[]>([])
  const [templateName, setTemplateName] = useState('')
  const [docType, setDocType] = useState('nid')
  const [engine, setEngine] = useState('shobdoocr')
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  const labels = fields.filter(f => f.field_type === 'label').length
  const values = fields.filter(f => f.field_type === 'value').length

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImageFile(file)
    const url = URL.createObjectURL(file)
    setImageUrl(url)
    const img = new Image()
    img.onload = () => setImageSize({ width: img.naturalWidth, height: img.naturalHeight })
    img.src = url
  }

  const handleRunOCR = async () => {
    if (!imageFile) return
    setLoading(true); setError('')
    try {
      const result = await processOCR(imageFile, engine)
      setWords(result.words)
      setStep(2)
    } catch (e) {
      setError('OCR failed. Check backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!templateName.trim() || fields.length === 0) return
    setLoading(true); setError('')
    try {
      await saveTemplate({
        template_name: templateName,
        document_type: docType,
        image_width: imageSize.width,
        image_height: imageSize.height,
        fields
      })
      setSaved(true)
      setStep(3)
    } catch (e) {
      setError('Failed to save template.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Template Builder</h1>
      <p className="text-gray-500 text-sm mb-6">
        Upload a document, run OCR, click word boxes to annotate fields, then save as a template.
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
      )}

      {step === 1 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Upload document image</label>
            <input type="file" accept="image/*" onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-700 file:font-medium hover:file:bg-blue-100" />
          </div>

          {imageUrl && (
            <img src={imageUrl} alt="Preview" className="max-h-64 rounded-lg border border-gray-200 object-contain" />
          )}

          <div className="flex gap-4 flex-wrap">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">OCR Engine</label>
              <select value={engine} onChange={e => setEngine(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                {ENGINES.map(e => <option key={e.value} value={e.value}>{e.label}</option>)}
              </select>
            </div>
          </div>

          <button onClick={handleRunOCR} disabled={!imageFile || loading}
            className="px-6 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed">
            {loading ? 'Running OCR...' : 'Run OCR & Continue'}
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
            Click any green word box to annotate it as a label or value.
            <span className="ml-2 font-medium">{labels} labels, {values} values defined.</span>
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <ImageAnnotator
              imageUrl={imageUrl}
              words={words}
              imageWidth={imageSize.width}
              imageHeight={imageSize.height}
              onAnnotationsChange={setFields}
            />
          </div>

          <div className="bg-white rounded-xl border border-gray-200 p-6 space-y-4">
            <h2 className="font-semibold text-gray-900">Save Template</h2>
            <div className="flex gap-4 flex-wrap">
              <div className="flex-1 min-w-48">
                <label className="block text-sm font-medium text-gray-700 mb-1">Template name</label>
                <input type="text" value={templateName} onChange={e => setTemplateName(e.target.value)}
                  placeholder="e.g. NID Card Template"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Document type</label>
                <select value={docType} onChange={e => setDocType(e.target.value)}
                  className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                  {DOC_TYPES.map(d => <option key={d.value} value={d.value}>{d.label}</option>)}
                </select>
              </div>
            </div>

            {fields.length > 0 && (
              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Defined fields:</p>
                <div className="flex flex-wrap gap-2">
                  {fields.map((f, i) => (
                    <span key={i} className={`px-2 py-1 rounded text-xs font-medium ${
                      f.field_type === 'label'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-orange-100 text-orange-700'
                    }`}>
                      {f.field_type === 'label' ? '🏷 ' : '📝 '}{f.field_name}
                      {f.field_type === 'value' && ` → ${f.for_label}`}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <button onClick={handleSave}
              disabled={!templateName.trim() || fields.length === 0 || loading}
              className="px-6 py-2.5 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed">
              {loading ? 'Saving...' : 'Save Template'}
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-8 text-center">
          <div className="text-4xl mb-3">✅</div>
          <h2 className="text-xl font-bold text-green-800 mb-2">Template saved!</h2>
          <p className="text-green-700 text-sm mb-6">
            Your template "{templateName}" has been saved. Go to Template Reader to use it.
          </p>
          <div className="flex gap-3 justify-center">
            <button onClick={() => { setStep(1); setWords([]); setFields([]); setTemplateName(''); setSaved(false); setImageUrl(''); setImageFile(null) }}
              className="px-4 py-2 text-sm rounded-lg border border-green-600 text-green-700 hover:bg-green-100">
              Create Another
            </button>
            <a href="/reader"
              className="px-4 py-2 text-sm rounded-lg bg-green-600 text-white hover:bg-green-700">
              Go to Reader →
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
