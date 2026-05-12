'use client'
import { useState } from 'react'

interface Props {
  word: { text: string; box: number[] }
  existingLabels: string[]
  onSave: (annotation: {
    field_name: string
    field_type: 'label' | 'value'
    for_label: string
  }) => void
  onClose: () => void
}

export default function FieldPopup({ word, existingLabels, onSave, onClose }: Props) {
  const [fieldType, setFieldType] = useState<'label' | 'value'>('label')
  const [fieldName, setFieldName] = useState('')
  const [forLabel, setForLabel] = useState(existingLabels[0] || '')

  const handleSave = () => {
    if (fieldType === 'label' && !fieldName.trim()) return
    if (fieldType === 'value' && !forLabel) return
    onSave({
      field_name: fieldType === 'label' ? fieldName.trim().toLowerCase().replace(/\s+/g, '_') : forLabel,
      field_type: fieldType,
      for_label: fieldType === 'value' ? forLabel : ''
    })
    onClose()
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl p-6 w-96 max-w-full mx-4">
        <h3 className="text-lg font-bold text-gray-900 mb-1">Annotate Word</h3>
        <p className="text-sm text-gray-500 mb-4">
          Selected: <span className="font-mono bg-gray-100 px-2 py-0.5 rounded text-gray-800">{word.text}</span>
        </p>

        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">This word is a:</p>
          <div className="flex gap-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="radio" name="type" value="label"
                checked={fieldType === 'label'}
                onChange={() => setFieldType('label')}
                className="accent-blue-600" />
              <span className="text-sm font-medium text-blue-700">Label</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="radio" name="type" value="value"
                checked={fieldType === 'value'}
                onChange={() => setFieldType('value')}
                className="accent-orange-500" />
              <span className="text-sm font-medium text-orange-600">Value</span>
            </label>
          </div>
        </div>

        {fieldType === 'label' && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Field name <span className="text-gray-400">(e.g. name, father, nid_no)</span>
            </label>
            <input
              type="text"
              value={fieldName}
              onChange={e => setFieldName(e.target.value)}
              placeholder="Enter field name..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              autoFocus
            />
          </div>
        )}

        {fieldType === 'value' && (
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              This is the value for:
            </label>
            {existingLabels.length === 0 ? (
              <p className="text-sm text-red-500">No labels defined yet. Define a label first.</p>
            ) : (
              <select
                value={forLabel}
                onChange={e => setForLabel(e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
              >
                {existingLabels.map(l => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            )}
          </div>
        )}

        <div className="flex gap-3 justify-end mt-2">
          <button onClick={onClose}
            className="px-4 py-2 text-sm rounded-lg border border-gray-300 text-gray-600 hover:bg-gray-50">
            Cancel
          </button>
          <button onClick={handleSave}
            disabled={fieldType === 'label' ? !fieldName.trim() : existingLabels.length === 0}
            className="px-4 py-2 text-sm rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed">
            Save
          </button>
        </div>
      </div>
    </div>
  )
}
