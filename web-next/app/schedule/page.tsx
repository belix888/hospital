'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Appointment {
  id: string
  appointmentDate: string
  appointmentTime: string
  status: string
  doctor_name: string
  doctor_specialization: string
  patient_name: string
  patient_phone: string
  room_name: string
}

export default function SchedulePage() {
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`/api/appointments?date=${date}`)
      .then(res => res.json())
      .then(data => setAppointments(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false))
  }, [date])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled': return 'bg-yellow-100 text-yellow-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'cancelled': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Расписание</h1>
        <div className="flex items-center space-x-4">
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="px-4 py-2 border rounded-md"
          />
          <Link
            href="/appointments/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Новая запись
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">Загрузка...</div>
      ) : appointments.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg">
          <p className="text-gray-500">Нет записей на {date}</p>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Время
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Врач
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Пациент
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Кабинет
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Статус
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {appointments.map((apt) => (
                <tr key={apt.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {formatTime(apt.appointmentTime)}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{apt.doctor_name}</div>
                    <div className="text-sm text-gray-500">{apt.doctor_specialization}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{apt.patient_name}</div>
                    <div className="text-sm text-gray-500">{apt.patient_phone}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{apt.room_name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(apt.status)}`}>
                      {apt.status === 'scheduled' ? 'Запланировано' : 
                       apt.status === 'completed' ? 'Завершено' : 'Отменено'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}