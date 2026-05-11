const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type WordBox = {
  text: string;
  box: number[];
  script: string;
  conf: number;
};

export type OCRResponse = {
  text: string;
  words: WordBox[];
  word_count: number;
  engine: string;
};

export type Annotation = {
  field_name: string;
  field_type: "label" | "value";
  for_label: string;
};

export type TemplateField = Annotation & {
  box: number[];
  word: string;
};

export type Template = {
  id?: string;
  template_name: string;
  document_type: string;
  fields: TemplateField[];
  image_width: number;
  image_height: number;
  image_url?: string;
};

export type ExtractionResult = {
  document_type: string;
  template_name: string;
  fields: Record<string, string>;
  raw_words: WordBox[];
};

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function processOCR(file: File, engine: string): Promise<OCRResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("engine", engine);

  const response = await fetch(`${API_URL}/ocr/process`, {
    method: "POST",
    body: formData,
  });

  return parseResponse<OCRResponse>(response);
}

export async function saveTemplate(template: Template, imageFile: File): Promise<{ template_id: string }> {
  const formData = new FormData();
  formData.append("template", JSON.stringify(template));
  formData.append("image", imageFile);

  const response = await fetch(`${API_URL}/template/save`, {
    method: "POST",
    body: formData,
  });

  return parseResponse<{ template_id: string }>(response);
}

export async function getTemplates(documentType?: string): Promise<Template[]> {
  const params = documentType ? `?document_type=${encodeURIComponent(documentType)}` : "";
  const response = await fetch(`${API_URL}/template/list${params}`, {
    cache: "no-store",
  });

  return parseResponse<Template[]>(response);
}

export async function extractFields(file: File, templateId: string): Promise<ExtractionResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("template_id", templateId);

  const response = await fetch(`${API_URL}/reader/extract`, {
    method: "POST",
    body: formData,
  });

  return parseResponse<ExtractionResult>(response);
}
