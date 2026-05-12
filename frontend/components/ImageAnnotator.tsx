'use client'
import { useState } from 'react'
import { WordBox, TemplateField } from '@/lib/api'
import FieldPopup from './FieldPopup'

interface Annotation {
  field_name: string
  field_type: 'label' | 'value'
  for_label: string
}

interface Props {
  imageUrl: string
  words: WordBox[]
  imageWidth: number
  imageHeight: number
  onAnnotationsChange: (fields: TemplateField[]) => void
}

export default function ImageAnnotator({
  imageUrl, words, imageWidth, imageHeight, onAnnotationsChange
}: Props) {
  const [firstClick, setFirstClick] = useState<WordBox | null>(null)
  const [selectedWords, setSelectedWords] = useState<WordBox[]>([])
  const [showPopup, setShowPopup] = useState(false)
  const [annotations, setAnnotations] = useState<Map<string, Annotation>>(new Map())

  const existingLabels = Array.from(annotations.values())
    .filter(a => a.field_type === 'label')
    .map(a => a.field_name)
    .filter((v, i, a) => a.indexOf(v) === i)

  // Get words between two clicked words on same row
  const getWordsBetween = (w1: WordBox, w2: WordBox): WordBox[] => {
    const cy1 = (w1.box[1] + w1.box[3]) / 2
    const cy2 = (w2.box[1] + w2.box[3]) / 2
    const avgCy = (cy1 + cy2) / 2
    const threshold = imageHeight * 0.04

    const minX = Math.min(w1.box[0], w2.box[0])
    const maxX = Math.max(w1.box[2], w2.box[2])

    return words
      .filter(w => {
        const cy = (w.box[1] + w.box[3]) / 2
        const cx = (w.box[0] + w.box[2]) / 2
        return Math.abs(cy - avgCy) <= threshold
          && cx >= minX && cx <= maxX
      })
      .sort((a, b) => a.box[0] - b.box[0])
  }

  const handleWordClick = (word: WordBox) => {
    if (!firstClick) {
      // First click - start selection
      setFirstClick(word)
      setSelectedWords([word])
    } else {
      // Second click - complete selection
      const between = getWordsBetween(firstClick, word)
      const selected = between.length > 0 ? between : [word]
      setSelectedWords(selected)
      setShowPopup(true)
    }
  }

  const handleAnnotate = (annotation: Annotation) => {
    const next = new Map(annotations)
    selectedWords.forEach(w => {
      next.set(w.box.join(','), annotation)
    })
    setAnnotations(next)

    const fields: TemplateField[] = []
    // Group annotated words by field
    const fieldGroups = new Map<string, {ann: Annotation, words: WordBox[]}>()
    
    words.forEach(w => {
      const k = w.box.join(',')
      const ann = next.get(k)
      if (ann) {
        const groupKey = `${ann.field_type}_${ann.field_name}_${ann.for_label}`
        if (!fieldGroups.has(groupKey)) {
          fieldGroups.set(groupKey, { ann, words: [] })
        }
        fieldGroups.get(groupKey)!.words.push(w)
      }
    })

    fieldGroups.forEach(({ ann, words: gWords }) => {
      gWords.sort((a, b) => a.box[0] - b.box[0])
      const x1 = Math.min(...gWords.map(w => w.box[0]))
      const y1 = Math.min(...gWords.map(w => w.box[1]))
      const x2 = Math.max(...gWords.map(w => w.box[2]))
      const y2 = Math.max(...gWords.map(w => w.box[3]))
      fields.push({
        field_name: ann.field_name,
        field_type: ann.field_type,
        for_label: ann.for_label,
        box: [x1, y1, x2, y2],
        word: gWords.map(w => w.text).join(' ')
      })
    })

    onAnnotationsChange(fields)
    setFirstClick(null)
    setSelectedWords([])
    setShowPopup(false)
  }

  const getBoxStyle = (word: WordBox) => {
    const key = word.box.join(',')
    
    // Currently being selected - yellow
    if (selectedWords.some(w => w.box.join(',') === key)) {
      return { border: '2px solid #ca8a04', background: 'rgba(234,179,8,0.25)' }
    }
    // First click waiting - yellow outline
    if (firstClick && firstClick.box.join(',') === key) {
      return { border: '2px solid #ca8a04', background: 'rgba(234,179,8,0.2)' }
    }

    const ann = annotations.get(key)
    if (!ann) return { border: '2px solid #16a34a', background: 'rgba(22,163,74,0.08)' }
    if (ann.field_type === 'label') return { border: '2px solid #2563eb', background: 'rgba(37,99,235,0.15)' }
    return { border: '2px solid #ea580c', background: 'rgba(234,88,12,0.15)' }
  }

  const handleCancel = () => {
    setFirstClick(null)
    setSelectedWords([])
    setShowPopup(false)
  }

  return (
    <div className="relative w-full select-none">
      <img
        src={imageUrl}
        alt="Document"
        className="w-full h-auto block"
        draggable={false}
      />

      <div className="absolute inset-0">
        {words.map((word, i) => {
          const [x1, y1, x2, y2] = word.box
          const left   = (x1 / imageWidth)  * 100
          const top    = (y1 / imageHeight) * 100
          const width  = ((x2 - x1) / imageWidth)  * 100
          const height = ((y2 - y1) / imageHeight) * 100

          return (
            <div
              key={i}
              onClick={() => handleWordClick(word)}
              style={{
                position: 'absolute',
                left: `${left}%`,
                top: `${top}%`,
                width: `${width}%`,
                height: `${height}%`,
                cursor: 'pointer',
                boxSizing: 'border-box',
                ...getBoxStyle(word)
              }}
              title={word.text}
            />
          )
        })}
      </div>

      {/* Instruction bar */}
      <div className="absolute top-2 left-2 right-2">
        {firstClick ? (
          <div className="bg-yellow-50 border border-yellow-300 rounded-lg px-3 py-1.5 text-xs text-yellow-800 flex justify-between items-center">
            <span>First word selected: <strong>{firstClick.text}</strong> - now click the last word of this field</span>
            <button onClick={handleCancel} className="ml-2 text-yellow-600 hover:text-yellow-800 font-medium">Cancel</button>
          </div>
        ) : (
          <div className="bg-blue-50 border border-blue-200 rounded-lg px-3 py-1.5 text-xs text-blue-800">
            Click the <strong>first word</strong> of a field, then click the <strong>last word</strong> to select a range
          </div>
        )}
      </div>

      {showPopup && (
        <FieldPopup
          word={{ text: selectedWords.map(w => w.text).join(' '), box: selectedWords[0]?.box || [] }}
          existingLabels={existingLabels}
          onSave={handleAnnotate}
          onClose={handleCancel}
        />
      )}

      <div className="mt-2 flex gap-4 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded border-2 border-green-600 bg-green-100"></span>
          Unannotated
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded border-2 border-yellow-500 bg-yellow-100"></span>
          Selecting
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded border-2 border-blue-600 bg-blue-100"></span>
          Label
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-3 rounded border-2 border-orange-500 bg-orange-100"></span>
          Value
        </span>
      </div>
    </div>
  )
}
