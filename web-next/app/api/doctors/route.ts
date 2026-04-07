import { getDoctors, createDoctor } from '@/lib/db'

export async function GET() {
  try {
    const doctors = await getDoctors()
    return Response.json(doctors)
  } catch (error) {
    return Response.json({ error: 'Failed to fetch doctors' }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { name, specialization, phone, email, telegramId } = body

    if (!name || !specialization) {
      return Response.json({ error: 'Name and specialization are required' }, { status: 400 })
    }

    const doctor = await createDoctor({ name, specialization, phone, email, telegramId })

    return Response.json(doctor)
  } catch (error) {
    return Response.json({ error: 'Failed to create doctor' }, { status: 500 })
  }
}