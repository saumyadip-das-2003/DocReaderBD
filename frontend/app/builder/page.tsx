"use client";

import { useMemo, useState } from "react";
import ImageAnnotator from "@/components/ImageAnnotator";
import { processOCR, saveTemplate, type Annotation, type TemplateField, type WordBox } from "@/lib/api";

const documentTypes = [
  { label: "NID", value: "nid" },
  { label: "Birth Certificate", value: "birth_cert" },
  { label: "Invoice", value: "invoice" },
  { label: "Custom", value: "custom" },
];

function wordKey(word: WordBox) {
  return `${word.text}-${word.box.join("-")}`;
}

export default function BuilderPage() {
  const [file, setFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState("");
  const [words, setWords] = useState<WordBox[]>([]);
  const [annotations, setAnnotations] = useState<Map<string, TemplateField>>(new Map());
  const [templateName, setTemplateName] = useState("");
  const [documentType, setDocumentType] = useState("nid");
  const [engine, setEngine] = useState("shobdoocr");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  const annotationList = useMemo(() => Array.from(annotations.values()), [annotations]);
  const labelCount = annotationList.filter((item) => item.field_type === "label").length;
  const valueCount = annotationList.filter((item) => item.field_type === "value").length;

  async function handleFileChange(nextFile: File | null) {
    setFile(nextFile);
    setWords([]);
    setAnnotations(new Map());
    setStatus("");
    if (imageUrl) {
      URL.revokeObjectURL(imageUrl);
    }
    setImageUrl(nextFile ? URL.createObjectURL(nextFile) : "");
  }

  async function handleRunOCR() {
    if (!file) {
      setStatus("Upload a document image first.");
      return;
    }

    setBusy(true);
    setStatus("Running OCR...");
    try {
      const result = await processOCR(file, engine);
      setWords(result.words);
      setStatus(`Detected ${result.word_count} words with ${result.engine}.`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "OCR failed.");
    } finally {
      setBusy(false);
    }
  }

  function handleAnnotate(word: WordBox, annotation: Annotation) {
    setAnnotations((current) => {
      const next = new Map(current);
      next.set(wordKey(word), {
        ...annotation,
        box: word.box,
        word: word.text,
      });
      return next;
    });
  }

  async function handleSaveTemplate() {
    if (!file || !templateName.trim() || annotationList.length === 0) {
      setStatus("Add an image, template name, and at least one annotation.");
      return;
    }

    const image = new Image();
    image.src = imageUrl;
    await image.decode();

    setBusy(true);
    setStatus("Saving template...");
    try {
      const result = await saveTemplate(
        {
          template_name: templateName.trim(),
          document_type: documentType,
          fields: annotationList,
          image_width: image.naturalWidth,
          image_height: image.naturalHeight,
        },
        file,
      );
      setStatus(`Template saved: ${result.template_id}`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Template save failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-2">
        <p className="text-sm font-semibold uppercase tracking-wide text-teal">Template Builder</p>
        <h1 className="text-3xl font-bold tracking-normal text-navy">Create a reusable extraction template</h1>
      </div>

      <section className="mt-8 grid gap-4 rounded-lg border border-slate-200 bg-white p-5 md:grid-cols-3">
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Document image</span>
          <input
            type="file"
            accept="image/*"
            className="mt-2 w-full text-sm"
            onChange={(event) => handleFileChange(event.target.files?.[0] || null)}
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">OCR engine</span>
          <select
            value={engine}
            onChange={(event) => setEngine(event.target.value)}
            className="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2"
          >
            <option value="shobdoocr">ShobdoOCR</option>
            <option value="tesseract">Tesseract</option>
            <option value="easyocr">EasyOCR</option>
          </select>
        </label>
        <div className="flex items-end">
          <button
            type="button"
            onClick={handleRunOCR}
            disabled={busy}
            className="focus-ring w-full rounded-md bg-teal px-4 py-2 font-semibold text-white disabled:bg-slate-300"
          >
            Run OCR
          </button>
        </div>
      </section>

      <div className="mt-4 text-sm font-medium text-slate-600">
        {labelCount} labels defined, {valueCount} values assigned
      </div>

      {imageUrl && words.length > 0 ? (
        <section className="mt-5">
          <ImageAnnotator imageUrl={imageUrl} words={words} onAnnotate={handleAnnotate} />
        </section>
      ) : null}

      <section className="mt-8 grid gap-4 rounded-lg border border-slate-200 bg-white p-5 md:grid-cols-3">
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Template name</span>
          <input
            value={templateName}
            onChange={(event) => setTemplateName(event.target.value)}
            className="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2"
            placeholder="NID front standard"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Document type</span>
          <select
            value={documentType}
            onChange={(event) => setDocumentType(event.target.value)}
            className="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2"
          >
            {documentTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </label>
        <div className="flex items-end">
          <button
            type="button"
            onClick={handleSaveTemplate}
            disabled={busy}
            className="focus-ring w-full rounded-md bg-navy px-4 py-2 font-semibold text-white disabled:bg-slate-300"
          >
            Save Template
          </button>
        </div>
      </section>

      {status ? <p className="mt-4 rounded-md bg-slate-100 px-4 py-3 text-sm text-slate-700">{status}</p> : null}
    </div>
  );
}
