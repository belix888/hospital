import { getPatients, createPatient } from '@/lib/db'

export async function GET() {
  try {
    const patients = await getPatients()
    return Response.json(patients)
  } catch (error) {
    return Response.json({ error: 'Failed to fetch patients' }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { name, phone, birthDate } = body

    if (!name || !phone) {
      return Response.json({ error: 'Name and phone are required' }, { status: 400 })
    }

    const patient = await createPatient({ name, phone, birthDate: birthDate ? new Date(birthDate) : undefined })

    return Response.json(patient)
  } catch (error) {
    return Response.json({ error: 'Failed to create patient' }, { status: 500 })
  }
}