const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://docreaderbd-production.up.railway.app'

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
  const form = new FormData()
  form.append('file', file)
  form.append('engine', engine)
  const res = await fetch(`${API_URL}/ocr/process`, {
    method: 'POST', body: form
  })
  if (!res.ok) throw new Error('OCR failed')
  return res.json()
}

export async function saveTemplate(template: Template): Promise<{ template_id: string }> {
  const res = await fetch(`${API_URL}/template/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(template)
  })
  if (!res.ok) throw new Error('Save template failed')
  return res.json()
}

export async function getTemplates(documentType?: string): Promise<Template[]> {
  const url = documentType
    ? `${API_URL}/template/list?document_type=${documentType}`
    : `${API_URL}/template/list`
  const res = await fetch(url)
  if (!res.ok) throw new Error('Failed to fetch templates')
  const data = await res.json()
  return data.templates
}

export async function deleteTemplate(templateId: string): Promise<void> {
  await fetch(`${API_URL}/template/${templateId}`, { method: 'DELETE' })
}

export async function extractFields(
  file: File,
  templateId: string,
  engine: string = 'shobdoocr'
): Promise<ExtractionResult> {
  const form = new FormData()
  form.append('file', file)
  form.append('template_id', templateId)
  form.append('engine', engine)
  const res = await fetch(`${API_URL}/reader/extract`, {
    method: 'POST', body: form
  })
  if (!res.ok) throw new Error('Extraction failed')
  return res.json()
}
