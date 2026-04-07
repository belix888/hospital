'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

interface Doctor {
  id: string
  name: string
  specialization: string
}

interface Patient {
  id: string
  name: string
  phone: string
}

interface Room {
  id: string
  name: string
  isAvailable: boolean
}

export default function NewAppointmentPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [doctors, setDoctors] = useState<Doctor[]>([])
  const [patients, setPatients] = useState<Patient[]>([])
  const [rooms, setRooms] = useState<Room[]>([])
  const [formData, setFormData] = useState({
    doctorId: '',
    patientId: '',
    roomId: '',
    date: '',
    time: '',
    durationMinutes: 60,
    notes: ''
  })
  const [newPatient, setNewPatient] = useState({ name: '', phone: '' })

  useEffect(() => {
    Promise.all([
      fetch('/api/doctors').then(r => r.json()),
      fetch('/api/patients').then(r => r.json()),
      fetch('/api/rooms').then(r => r.json())
    ]).then(([d, p, r]) => {
      setDoctors(d)
      setPatients(p)
      setRooms(r.filter((room: Room) => room.isAvailable))
    })
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const res = await fetch('/api/appointments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          appointmentDate: formData.date,
          appointmentTime: `${formData.date}T${formData.time}:00`
        })
      })

      if (res.ok) {
        router.push('/schedule')
      } else {
        alert('Ошибка при создании записи')
      }
    } catch (err) {
      alert('Ошибка при создании записи')
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePatient = async () => {
    if (!newPatient.name || !newPatient.phone) {
      alert('Введите имя и телефон пациента')
      return
    }

    const res = await fetch('/api/patients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newPatient)
    })

    if (res.ok) {
      const patient = await res.json()
      setPatients([...patients, patient])
      setFormData({ ...formData, patientId: patient.id })
      setNewPatient({ name: '', phone: '' })
    }
  }

  return (
    <div className="px-4 py-6 sm:px-0 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Создание новой записи</h1>

      <form onSubmit={handleSubmit} className="bg-white shadow rounded-lg p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Врач</label>
          <select
            required
            value={formData.doctorId}
            onChange={e => setFormData({ ...formData, doctorId: e.target.value })}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="">Выберите врача</option>
            {doctors.map(d => (
              <option key={d.id} value={d.id}>{d.name} ({d.specialization})</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Пациент</label>
          {patients.length > 0 ? (
            <select
              required
              value={formData.patientId}
              onChange={e => setFormData({ ...formData, patientId: e.target.value })}
              className="w-full px-3 py-2 border rounded-md"
            >
              <option value="">Выберите пациента</option>
              {patients.map(p => (
                <option key={p.id} value={p.id}>{p.name} ({p.phone})</option>
              ))}
            </select>
          ) : (
            <div className="space-y-3">
              <input
                type="text"
                placeholder="ФИО пациента"
                value={newPatient.name}
                onChange={e => setNewPatient({ ...newPatient, name: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
              />
              <input
                type="tel"
                placeholder="Телефон"
                value={newPatient.phone}
                onChange={e => setNewPatient({ ...newPatient, phone: e.target.value })}
                className="w-full px-3 py-2 border rounded-md"
              />
              <button
                type="button"
                onClick={handleCreatePatient}
                className="text-sm text-blue-600 hover:underline"
              >
                Добавить нового пациента
              </button>
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Кабинет</label>
          <select
            required
            value={formData.roomId}
            onChange={e => setFormData({ ...formData, roomId: e.target.value })}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="">Выберите кабинет</option>
            {rooms.map(r => (
              <option key={r.id} value={r.id}>{r.name}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Дата</label>
            <input
              type="date"
              required
              value={formData.date}
              onChange={e => setFormData({ ...formData, date: e.target.value })}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Время</label>
            <input
              type="time"
              required
              value={formData.time}
              onChange={e => setFormData({ ...formData, time: e.target.value })}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Длительность (минут)</label>
          <select
            value={formData.durationMinutes}
            onChange={e => setFormData({ ...formData, durationMinutes: parseInt(e.target.value) })}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value={30}>30 минут</option>
            <option value={60}>60 минут</option>
            <option value={90}>90 минут</option>
            <option value={120}>120 минут</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Заметки</label>
          <textarea
            value={formData.notes}
            onChange={e => setFormData({ ...formData, notes: e.target.value })}
            rows={3}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>

        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Создание...' : 'Создать запись'}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Отмена
          </button>
        </div>
      </form>
    </div>
  )
}