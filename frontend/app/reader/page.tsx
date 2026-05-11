"use client";

import { useEffect, useMemo, useState } from "react";
import { extractFields, getTemplates, type ExtractionResult, type Template } from "@/lib/api";

const documentTypes = [
  { label: "NID", value: "nid" },
  { label: "Birth Certificate", value: "birth_cert" },
  { label: "Invoice", value: "invoice" },
  { label: "Custom", value: "custom" },
];

export default function ReaderPage() {
  const [documentType, setDocumentType] = useState("nid");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [templateId, setTemplateId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    async function loadTemplates() {
      setStatus("Loading templates...");
      try {
        const items = await getTemplates(documentType);
        setTemplates(items);
        setTemplateId(items[0]?.id || "");
        setStatus(items.length ? "" : "No templates found for this document type.");
      } catch (error) {
        setStatus(error instanceof Error ? error.message : "Could not load templates.");
      }
    }

    loadTemplates();
  }, [documentType]);

  const rows = useMemo(() => Object.entries(result?.fields || {}), [result]);

  async function handleExtract() {
    if (!file || !templateId) {
      setStatus("Select a template and upload a document image.");
      return;
    }

    setBusy(true);
    setStatus("Extracting fields...");
    try {
      const extraction = await extractFields(file, templateId);
      setResult(extraction);
      setStatus("Extraction complete.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Extraction failed.");
    } finally {
      setBusy(false);
    }
  }

  function handleDownload() {
    if (!result) {
      return;
    }

    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "docreaderbd-extraction.json";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-2">
        <p className="text-sm font-semibold uppercase tracking-wide text-teal">Template Reader</p>
        <h1 className="text-3xl font-bold tracking-normal text-navy">Extract fields from a document</h1>
      </div>

      <section className="mt-8 grid gap-4 rounded-lg border border-slate-200 bg-white p-5 md:grid-cols-4">
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
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Template</span>
          <select
            value={templateId}
            onChange={(event) => setTemplateId(event.target.value)}
            className="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2"
          >
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.template_name}
              </option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Document image</span>
          <input
            type="file"
            accept="image/*"
            className="mt-2 w-full text-sm"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
          />
        </label>
        <div className="flex items-end">
          <button
            type="button"
            onClick={handleExtract}
            disabled={busy}
            className="focus-ring w-full rounded-md bg-teal px-4 py-2 font-semibold text-white disabled:bg-slate-300"
          >
            Extract
          </button>
        </div>
      </section>

      {status ? <p className="mt-4 rounded-md bg-slate-100 px-4 py-3 text-sm text-slate-700">{status}</p> : null}

      {result ? (
        <section className="mt-8 rounded-lg border border-slate-200 bg-white">
          <div className="flex flex-col gap-3 border-b border-slate-200 p-5 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-xl font-semibold text-navy">{result.template_name}</h2>
              <p className="text-sm text-slate-500">{result.document_type}</p>
            </div>
            <button
              type="button"
              onClick={handleDownload}
              className="focus-ring rounded-md bg-navy px-4 py-2 text-sm font-semibold text-white"
            >
              Download JSON
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[520px] border-collapse text-left">
              <thead className="bg-slate-50 text-sm text-slate-500">
                <tr>
                  <th className="px-5 py-3 font-semibold">Field</th>
                  <th className="px-5 py-3 font-semibold">Value</th>
                  <th className="px-5 py-3 font-semibold">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(([field, value]) => (
                  <tr key={field} className="border-t border-slate-100">
                    <td className="px-5 py-4 font-medium text-navy">{field}</td>
                    <td className="px-5 py-4 text-slate-700">{value}</td>
                    <td className="px-5 py-4">
                      <span className="rounded-full bg-teal/10 px-3 py-1 text-sm font-semibold text-teal">
                        Estimated
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </div>
  );
}
