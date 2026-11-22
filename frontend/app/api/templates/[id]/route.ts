import { getAdminDb } from '@/lib/firebase-admin'

const COLLECTION = 'templates'
type RouteContext = { params: { id: string } }

export async function GET(_request: Request, { params }: RouteContext) {
  try {
    const snapshot = await getAdminDb().collection(COLLECTION).doc(params.id).get()
    if (!snapshot.exists) {
      return Response.json({ detail: 'Template not found' }, { status: 404 })
    }
    return Response.json(snapshot.data())
  } catch (error) {
    console.error('Failed to load template', error)
    return Response.json({ detail: 'Template database is unavailable' }, { status: 500 })
  }
}

export async function DELETE(_request: Request, { params }: RouteContext) {
  try {
    await getAdminDb().collection(COLLECTION).doc(params.id).delete()
    return Response.json({ success: true })
  } catch (error) {
    console.error('Failed to delete template', error)
    return Response.json({ detail: 'Template database is unavailable' }, { status: 500 })
  }
}
