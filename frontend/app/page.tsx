import Link from "next/link";

const documentTypes = ["NID Card", "Birth Certificate", "Invoice", "Custom"];

export default function HomePage() {
  return (
    <div className="bg-white">
      <section className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-wide text-teal">DocReader BD</p>
          <h1 className="mt-3 text-4xl font-bold tracking-normal text-navy sm:text-5xl">
            Intelligent Document Processing for Bangladeshi Enterprises.
          </h1>
          <p className="mt-5 text-lg leading-8 text-slate-600">
            Build reusable document templates, read scanned Bangla and English forms, and extract structured data from
            NID cards, certificates, invoices, and custom business documents.
          </p>
        </div>

        <div className="mt-10 grid gap-5 md:grid-cols-2">
          <Link
            href="/builder"
            className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition hover:border-teal hover:shadow-md"
          >
            <h2 className="text-2xl font-semibold text-navy">Template Builder</h2>
            <p className="mt-3 text-slate-600">
              Upload a sample document, run OCR, click detected words, and define label-value mappings for repeatable
              extraction.
            </p>
            <span className="mt-6 inline-flex rounded-md bg-teal px-4 py-2 text-sm font-semibold text-white">
              Start building
            </span>
          </Link>

          <Link
            href="/reader"
            className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition hover:border-teal hover:shadow-md"
          >
            <h2 className="text-2xl font-semibold text-navy">Template Reader</h2>
            <p className="mt-3 text-slate-600">
              Select a saved template, upload a matching document, and extract clean field values into a reviewable
              table.
            </p>
            <span className="mt-6 inline-flex rounded-md bg-navy px-4 py-2 text-sm font-semibold text-white">
              Extract data
            </span>
          </Link>
        </div>

        <section className="mt-12">
          <h2 className="text-xl font-semibold text-navy">Supported document types</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {documentTypes.map((type) => (
              <div key={type} className="rounded-lg border border-slate-200 bg-slate-50 px-4 py-4 text-slate-700">
                {type}
              </div>
            ))}
          </div>
        </section>
      </section>
    </div>
  );
}
