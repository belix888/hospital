import { getRooms, createRoom } from '@/lib/db'

export async function GET() {
  try {
    const rooms = await getRooms()
    return Response.json(rooms)
  } catch (error) {
    return Response.json({ error: 'Failed to fetch rooms' }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json()
    const { name, isAvailable } = body

    if (!name) {
      return Response.json({ error: 'Name is required' }, { status: 400 })
    }

    const room = await createRoom({ name, isAvailable })

    return Response.json(room)
  } catch (error) {
    return Response.json({ error: 'Failed to create room' }, { status: 500 })
  }
}