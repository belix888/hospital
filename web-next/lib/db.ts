import { Pool } from 'pg'

const globalForPool = globalThis as unknown as {
  pool: Pool | undefined
}

export const pool = globalForPool.pool ?? new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  }
})

if (process.env.NODE_ENV !== 'production') globalForPool.pool = pool

// Doctors
export async function getDoctors() {
  const result = await pool.query('SELECT * FROM "Doctor" WHERE "isActive" = true ORDER BY name')
  return result.rows
}

export async function getAllDoctors() {
  const result = await pool.query('SELECT * FROM "Doctor" ORDER BY name')
  return result.rows
}

export async function createDoctor(data: { name: string; specialization: string; phone?: string; email?: string; telegramId?: bigint }) {
  const result = await pool.query(
    `INSERT INTO "Doctor" (name, specialization, phone, email, "telegramId", "isActive", "createdAt", "updatedAt")
     VALUES ($1, $2, $3, $4, $5, true, NOW(), NOW())
     RETURNING *`,
    [data.name, data.specialization, data.phone || null, data.email || null, data.telegramId || null]
  )
  return result.rows[0]
}

// Patients
export async function getPatients() {
  const result = await pool.query('SELECT * FROM "Patient" ORDER BY name')
  return result.rows
}

export async function createPatient(data: { name: string; phone: string; birthDate?: Date }) {
  const result = await pool.query(
    `INSERT INTO "Patient" (name, phone, "birthDate", "createdAt", "updatedAt")
     VALUES ($1, $2, $3, NOW(), NOW())
     RETURNING *`,
    [data.name, data.phone, data.birthDate || null]
  )
  return result.rows[0]
}

// Rooms
export async function getRooms() {
  const result = await pool.query('SELECT * FROM "Room" WHERE "isDeleted" = false ORDER BY name')
  return result.rows
}

export async function createRoom(data: { name: string; isAvailable?: boolean }) {
  const result = await pool.query(
    `INSERT INTO "Room" (name, "isAvailable", "isDeleted", "createdAt", "updatedAt")
     VALUES ($1, $2, false, NOW(), NOW())
     RETURNING *`,
    [data.name, data.isAvailable ?? true]
  )
  return result.rows[0]
}

// Appointments
export async function getAppointments(filters?: { date?: string; doctorId?: string }) {
  let query = `
    SELECT a.*, d.name as doctor_name, d.specialization as doctor_specialization,
           p.name as patient_name, p.phone as patient_phone,
           r.name as room_name
    FROM "Appointment" a
    JOIN "Doctor" d ON a."doctorId" = d.id
    JOIN "Patient" p ON a."patientId" = p.id
    JOIN "Room" r ON a."roomId" = r.id
  `
  
  const conditions: string[] = []
  const params: any[] = []
  
  if (filters?.date) {
    params.push(filters.date + ' 00:00:00', filters.date + ' 23:59:59')
    conditions.push(`a."appointmentDate" >= $${params.length - 1} AND a."appointmentDate" <= $${params.length}`)
  }
  
  if (filters?.doctorId) {
    params.push(filters.doctorId)
    conditions.push(`a."doctorId" = $${params.length}`)
  }
  
  if (conditions.length > 0) {
    query += ' WHERE ' + conditions.join(' AND ')
  }
  
  query += ' ORDER BY a."appointmentDate", a."appointmentTime"'
  
  const result = await pool.query(query, params)
  return result.rows
}

export async function createAppointment(data: {
  doctorId: string
  patientId: string
  roomId: string
  appointmentDate: Date
  appointmentTime: Date
  durationMinutes?: number
  notes?: string
}) {
  const result = await pool.query(
    `INSERT INTO "Appointment" 
     ("doctorId", "patientId", "roomId", "appointmentDate", "appointmentTime", "durationMinutes", "notes", "status", "createdAt", "updatedAt")
     VALUES ($1, $2, $3, $4, $5, $6, $7, 'scheduled', NOW(), NOW())
     RETURNING *`,
    [
      data.doctorId,
      data.patientId,
      data.roomId,
      data.appointmentDate,
      data.appointmentTime,
      data.durationMinutes || 60,
      data.notes || ''
    ]
  )
  return result.rows[0]
}

// Stats
export async function getStats() {
  const doctors = await pool.query('SELECT COUNT(*) as count FROM "Doctor" WHERE "isActive" = true')
  const patients = await pool.query('SELECT COUNT(*) as count FROM "Patient"')
  const rooms = await pool.query('SELECT COUNT(*) as count FROM "Room" WHERE "isAvailable" = true AND "isDeleted" = false')
  const appointments = await pool.query('SELECT COUNT(*) as count FROM "Appointment"')
  
  const today = new Date().toISOString().split('T')[0]
  const todayAppointments = await pool.query(
    `SELECT COUNT(*) as count FROM "Appointment" 
     WHERE "appointmentDate" >= $1 AND "appointmentDate" < $2`,
    [today + ' 00:00:00', today + ' 23:59:59']
  )
  
  return {
    doctorsCount: parseInt(doctors.rows[0].count),
    patientsCount: parseInt(patients.rows[0].count),
    roomsCount: parseInt(rooms.rows[0].count),
    appointmentsToday: parseInt(todayAppointments.rows[0].count),
    totalAppointments: parseInt(appointments.rows[0].count)
  }
}