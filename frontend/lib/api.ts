const SHOBDOOCR_API_URL = (
  process.env.NEXT_PUBLIC_SHOBDOOCR_API_URL ||
  'https://sarjinkhan2003-shobdoocr-web.hf.space'
).replace(/\/$/, '')
const SHOBDOOCR_TIMEOUT_MS = 120_000

export interface WordBox {
  text: string
  box: [number, number, number, number]
  script: string
  conf: number
}

export interface TemplateField {
  field_name: string
  field_type: 'label' | 'value'
  for_label: string
  box: [number, number, number, number]
  word: string
}

export interface Template {
  id?: string
  template_name: string
  document_type: string
  image_width: number
  image_height: number
  fields: TemplateField[]
  created_at?: string
}

export interface OCRResponse {
  text: string
  words: WordBox[]
  word_count: number
  engine: string
}

export interface ExtractionResult {
  document_type: string
  template_name: string
  fields: Record<string, string>
  raw_words: WordBox[]
  word_count: number
}

export async function processOCR(
  file: File,
  engine: string = 'shobdoocr'
): Promise<OCRResponse> {
  if (engine === 'shobdoocr') {
    const form = new FormData()
    form.append('file', file)

    const controller = new AbortController()
    const timeout = window.setTimeout(
      () => controller.abort(),
      SHOBDOOCR_TIMEOUT_MS
    )

    try {
      // Do not set Content-Type: the browser must add the multipart boundary.
      const res = await fetch(`${SHOBDOOCR_API_URL}/ocr`, {
        method: 'POST',
        body: form,
        signal: controller.signal,
      })
      if (!res.ok) {
        let detail = `ShobdoOCR returned HTTP ${res.status}`
        try {
          const errorBody = await res.json()
          if (errorBody?.detail) detail += `: ${errorBody.detail}`
        } catch {}
        throw new Error(detail)
      }

      const payload = await res.json()
      if (typeof payload.full_text !== 'string') {
        throw new Error('ShobdoOCR returned an invalid response')
      }

      const words: WordBox[] = Array.isArray(payload.words)
        ? payload.words
            .filter((word: any) => word?.text && Array.isArray(word?.box))
            .map((word: any) => ({
              text: String(word.text),
              box: word.box as [number, number, number, number],
              script: String(word.script || 'unknown'),
              conf: Number(word.confidence ?? word.conf ?? 0),
            }))
        : []

      return {
        text: payload.full_text,
        words,
        word_count: words.length,
        engine: 'shobdoocr',
      }
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw new Error('ShobdoOCR timed out after 120 seconds')
      }
      throw error
    } finally {
      window.clearTimeout(timeout)
    }
  }

  throw new Error(`${engine} requires the optional local Python backend`)
}

export async function saveTemplate(template: Template): Promise<{ template_id: string }> {
  const res = await fetch('/api/templates', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(template)
  })
  if (!res.ok) throw new Error('Save template failed')
  return res.json()
}

export async function getTemplates(documentType?: string): Promise<Template[]> {
  const url = documentType
    ? `/api/templates?document_type=${encodeURIComponent(documentType)}`
    : '/api/templates'
  const res = await fetch(url)
  if (!res.ok) throw new Error('Failed to fetch templates')
  const data = await res.json()
  return data.templates
}

export async function deleteTemplate(templateId: string): Promise<void> {
  const res = await fetch(`/api/templates/${encodeURIComponent(templateId)}`, {
    method: 'DELETE',
  })
  if (!res.ok) throw new Error('Failed to delete template')
}

export async function extractFields(
  file: File,
  templateId: string,
  engine: string = 'shobdoocr'
): Promise<ExtractionResult> {
  if (engine !== 'shobdoocr') {
    throw new Error(`${engine} requires the optional local Python backend`)
  }

  const [templateRes, ocrResult, dimensions] = await Promise.all([
    fetch(`/api/templates/${encodeURIComponent(templateId)}`),
    processOCR(file, engine),
    getImageDimensions(file),
  ])
  if (!templateRes.ok) throw new Error('Failed to load template')

  const template: Template = await templateRes.json()
  const fields = extractTemplateFields(
    ocrResult.words,
    template,
    dimensions.width,
    dimensions.height
  )

  return {
    document_type: template.document_type,
    template_name: template.template_name,
    fields,
    raw_words: ocrResult.words,
    word_count: ocrResult.word_count,
  }
}

async function getImageDimensions(file: File): Promise<{ width: number; height: number }> {
  const bitmap = await createImageBitmap(file)
  const dimensions = { width: bitmap.width, height: bitmap.height }
  bitmap.close()
  return dimensions
}

function extractTemplateFields(
  words: WordBox[],
  template: Template,
  imageWidth: number,
  imageHeight: number
): Record<string, string> {
  const scaleX = imageWidth / template.image_width
  const scaleY = imageHeight / template.image_height
  const labels = new Map(
    template.fields
      .filter(field => field.field_type === 'label')
      .map(field => [field.field_name, field])
  )
  const result: Record<string, string> = {}

  for (const field of template.fields.filter(item => item.field_type === 'value')) {
    const fieldName = field.for_label || field.field_name
    const [, y1, x2, y2] = field.box
    const rowCenter = ((y1 + y2) / 2) * scaleY
    const rowHeight = Math.max((y2 - y1) * scaleY, 10)
    const label = labels.get(fieldName)
    const horizontalStart = label ? label.box[2] * scaleX : field.box[0] * scaleX

    result[fieldName] = words
      .filter(word => {
        const [wordX1, wordY1, wordX2, wordY2] = word.box
        const centerX = (wordX1 + wordX2) / 2
        const centerY = (wordY1 + wordY2) / 2
        return Math.abs(centerY - rowCenter) <= rowHeight * 0.7 && centerX >= horizontalStart
      })
      .sort((a, b) => a.box[0] - b.box[0])
      .map(word => word.text)
      .join(' ')
  }

  return result
}
