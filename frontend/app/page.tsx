import Link from 'next/link'

export default function Home() {
  return (
    <main className="max-w-4xl mx-auto px-4 py-16">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">DocReader BD</h1>
        <p className="text-lg text-gray-500 max-w-xl mx-auto">
          Intelligent document processing for Bangladeshi enterprises.
          Annotate once, extract forever.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
        <Link href="/builder" className="group block bg-white rounded-2xl border border-gray-200 p-8 hover:border-blue-400 hover:shadow-lg transition-all">
          <div className="text-3xl mb-3">🏗️</div>
          <h2 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600">Template Builder</h2>
          <p className="text-gray-500 text-sm">Upload a document, run OCR, click word boxes to define field labels and values. Save as a reusable template.</p>
          <span className="inline-block mt-4 text-sm font-medium text-blue-600">Build a template →</span>
        </Link>

        <Link href="/reader" className="group block bg-white rounded-2xl border border-gray-200 p-8 hover:border-green-400 hover:shadow-lg transition-all">
          <div className="text-3xl mb-3">📄</div>
          <h2 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-green-600">Template Reader</h2>
          <p className="text-gray-500 text-sm">Select a saved template, upload any document of the same type, and extract structured JSON fields automatically.</p>
          <span className="inline-block mt-4 text-sm font-medium text-green-600">Extract fields →</span>
        </Link>
      </div>

      <div className="bg-gray-50 rounded-xl p-6 text-center">
        <p className="text-sm font-medium text-gray-600 mb-3">Supported document types</p>
        <div className="flex gap-3 justify-center flex-wrap">
          {['NID Card','Birth Certificate','Invoice','Land Deed','Custom Forms'].map(t => (
            <span key={t} className="px-3 py-1 bg-white border border-gray-200 rounded-full text-xs text-gray-600 font-medium">{t}</span>
          ))}
        </div>
      </div>
    </main>
  )
}
