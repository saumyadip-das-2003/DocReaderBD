import { getAdminDb } from '@/lib/firebase-admin'

const COLLECTION = 'templates'

export async function GET(request: Request) {
  try {
    const documentType = new URL(request.url).searchParams.get('document_type')
    let query: FirebaseFirestore.Query = getAdminDb().collection(COLLECTION)
    if (documentType) {
      query = query.where('document_type', '==', documentType)
    }
    const snapshot = await query.get()
    return Response.json({ templates: snapshot.docs.map(doc => doc.data()) })
  } catch (error) {
    console.error('Failed to list templates', error)
    return Response.json({ detail: 'Template database is unavailable' }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const template = await request.json()
    if (
      !template?.template_name ||
      !template?.document_type ||
      !Number.isFinite(template?.image_width) ||
      !Number.isFinite(template?.image_height) ||
      !Array.isArray(template?.fields)
    ) {
      return Response.json({ detail: 'Invalid template payload' }, { status: 400 })
    }

    const doc = getAdminDb().collection(COLLECTION).doc()
    await doc.set({
      ...template,
      id: doc.id,
      created_at: new Date().toISOString(),
    })
    return Response.json({ success: true, template_id: doc.id })
  } catch (error) {
    console.error('Failed to save template', error)
    return Response.json({ detail: 'Template database is unavailable' }, { status: 500 })
  }
}
