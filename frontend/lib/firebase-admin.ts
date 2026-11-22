import { cert, getApps, initializeApp, type ServiceAccount } from 'firebase-admin/app'
import { getFirestore } from 'firebase-admin/firestore'

export function getAdminDb() {
  if (!getApps().length) {
    const rawCredentials = process.env.FIREBASE_CREDENTIALS_JSON
    if (!rawCredentials) {
      throw new Error('FIREBASE_CREDENTIALS_JSON is not configured')
    }

    const credentials = JSON.parse(rawCredentials) as ServiceAccount & {
      private_key?: string
    }
    if (credentials.private_key) {
      credentials.private_key = credentials.private_key.replace(/\\n/g, '\n')
    }

    initializeApp({ credential: cert(credentials) })
  }

  return getFirestore()
}
