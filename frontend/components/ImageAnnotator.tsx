"use client";

import { useMemo, useState } from "react";
import FieldPopup from "@/components/FieldPopup";
import type { Annotation, WordBox } from "@/lib/api";

type ImageAnnotatorProps = {
  imageUrl: string;
  words: WordBox[];
  onAnnotate: (word: WordBox, annotation: Annotation) => void;
};

function wordKey(word: WordBox) {
  return `${word.text}-${word.box.join("-")}`;
}

function rectClass(annotation?: Annotation) {
  if (annotation?.field_type === "label") {
    return "fill-blue-500/20 stroke-blue-600";
  }
  if (annotation?.field_type === "value") {
    return "fill-orange-500/25 stroke-orange-600";
  }
  return "fill-transparent stroke-emerald-600";
}

export default function ImageAnnotator({ imageUrl, words, onAnnotate }: ImageAnnotatorProps) {
  const [selectedWord, setSelectedWord] = useState<WordBox | null>(null);
  const [annotations, setAnnotations] = useState<Map<string, Annotation>>(new Map());

  const dimensions = useMemo(() => {
    const width = Math.max(...words.map((word) => word.box[2]), 1);
    const height = Math.max(...words.map((word) => word.box[3]), 1);
    return { width, height };
  }, [words]);

  const existingLabels = useMemo(
    () =>
      Array.from(annotations.values())
        .filter((annotation) => annotation.field_type === "label")
        .map((annotation) => annotation.field_name),
    [annotations],
  );

  function handleSave(annotation: Annotation) {
    if (!selectedWord) {
      return;
    }

    setAnnotations((current) => {
      const next = new Map(current);
      next.set(wordKey(selectedWord), annotation);
      return next;
    });
    onAnnotate(selectedWord, annotation);
    setSelectedWord(null);
  }

  return (
    <div>
      <div className="overflow-auto rounded-lg border border-slate-200 bg-slate-100">
        <div className="relative mx-auto w-full min-w-[320px]" style={{ maxWidth: dimensions.width }}>
          <img src={imageUrl} alt="Uploaded document" className="block h-auto w-full" />
          <svg
            className="absolute inset-0 h-full w-full"
            viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
            preserveAspectRatio="none"
          >
            {words.map((word) => {
              const key = wordKey(word);
              const annotation = annotations.get(key);
              const [x1, y1, x2, y2] = word.box;

              return (
                <rect
                  key={key}
                  x={x1}
                  y={y1}
                  width={Math.max(x2 - x1, 1)}
                  height={Math.max(y2 - y1, 1)}
                  className={`${rectClass(annotation)} cursor-pointer stroke-[2] transition hover:fill-teal/20`}
                  onClick={() => setSelectedWord(word)}
                />
              );
            })}
          </svg>
        </div>
      </div>

      {selectedWord ? (
        <FieldPopup
          word={selectedWord}
          existingLabels={existingLabels}
          onSave={handleSave}
          onClose={() => setSelectedWord(null)}
        />
      ) : null}
    </div>
  );
}
