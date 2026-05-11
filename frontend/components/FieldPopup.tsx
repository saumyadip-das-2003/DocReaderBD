"use client";

import { useState } from "react";
import type { Annotation, WordBox } from "@/lib/api";

type FieldPopupProps = {
  word: WordBox;
  existingLabels: string[];
  onSave: (annotation: Annotation) => void;
  onClose: () => void;
};

export default function FieldPopup({ word, existingLabels, onSave, onClose }: FieldPopupProps) {
  const [fieldType, setFieldType] = useState<"label" | "value">("label");
  const [fieldName, setFieldName] = useState("");
  const [forLabel, setForLabel] = useState(existingLabels[0] || "");

  const canSave = fieldType === "label" ? fieldName.trim().length > 0 : forLabel.length > 0;

  function handleSave() {
    if (!canSave) {
      return;
    }

    onSave({
      field_type: fieldType,
      field_name: fieldType === "label" ? fieldName.trim() : forLabel,
      for_label: fieldType === "value" ? forLabel : "",
    });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-navy/60 px-4">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        <div>
          <p className="text-sm font-medium text-slate-500">Selected word</p>
          <h2 className="mt-1 text-2xl font-semibold text-navy">{word.text}</h2>
        </div>

        <div className="mt-6 grid gap-3">
          <label className="flex items-center gap-3 rounded-md border border-slate-200 p-3">
            <input
              type="radio"
              name="fieldType"
              checked={fieldType === "label"}
              onChange={() => setFieldType("label")}
            />
            <span className="font-medium text-slate-700">This is a Label</span>
          </label>
          <label className="flex items-center gap-3 rounded-md border border-slate-200 p-3">
            <input
              type="radio"
              name="fieldType"
              checked={fieldType === "value"}
              onChange={() => setFieldType("value")}
            />
            <span className="font-medium text-slate-700">This is a Value</span>
          </label>
        </div>

        {fieldType === "label" ? (
          <label className="mt-5 block">
            <span className="text-sm font-medium text-slate-700">Field name</span>
            <input
              value={fieldName}
              onChange={(event) => setFieldName(event.target.value)}
              placeholder="name"
              className="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2"
            />
          </label>
        ) : (
          <label className="mt-5 block">
            <span className="text-sm font-medium text-slate-700">Belongs to label</span>
            <select
              value={forLabel}
              onChange={(event) => setForLabel(event.target.value)}
              className="focus-ring mt-2 w-full rounded-md border border-slate-300 px-3 py-2"
            >
              {existingLabels.length === 0 ? <option value="">Define a label first</option> : null}
              {existingLabels.map((label) => (
                <option key={label} value={label}>
                  {label}
                </option>
              ))}
            </select>
          </label>
        )}

        <div className="mt-6 flex justify-end gap-3">
          <button type="button" onClick={onClose} className="focus-ring rounded-md border border-slate-300 px-4 py-2">
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            disabled={!canSave}
            className="focus-ring rounded-md bg-teal px-4 py-2 font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}
