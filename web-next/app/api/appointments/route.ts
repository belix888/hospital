import { getAppointments, createAppointment } from '@/lib/db'

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const date = searchParams.get('date')
    const doctorId = searchParams.get('doctorId')

    const appointments = await getAppointments({ date: date || undefined, doctorId: doctorId || undefined })
    return Response.json(appointments)
  } catch (error) {
    return Response.json({ error: 'Failed to fetch appointments' }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { doctorId, patientId, roomId, appointmentDate, appointmentTime, durationMinutes, notes } = body

    if (!doctorId || !patientId || !roomId || !appointmentDate || !appointmentTime) {
      return Response.json({ error: 'Missing required fields' }, { status: 400 })
    }

    const appointment = await createAppointment({
      doctorId,
      patientId,
      roomId,
      appointmentDate: new Date(appointmentDate),
      appointmentTime: new Date(appointmentTime),
      durationMinutes,
      notes
    })

    return Response.json(appointment)
  } catch (error) {
    console.error('Error creating appointment:', error)
    return Response.json({ error: 'Failed to create appointment' }, { status: 500 })
  }
}