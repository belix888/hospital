import Link from 'next/link'
import { getStats } from '@/lib/db'

export const dynamic = 'force-dynamic'

export default async function HomePage() {
  let stats = {
    doctorsCount: 0,
    patientsCount: 0,
    appointmentsToday: 0,
    roomsCount: 0
  }

  try {
    stats = await getStats()
  } catch (e) {
    // Database not available during build
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Система управления больницей</h1>
        <p className="mt-2 text-gray-600">Добро пожаловать в систему управления записями</p>
      </div>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Активных врачей</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.doctorsCount}</dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Пациентов</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.patientsCount}</dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Записей сегодня</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.appointmentsToday}</dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">Свободных кабинетов</dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">{stats.roomsCount}</dd>
          </div>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2">
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Быстрые действия</h3>
          <div className="space-y-3">
            <Link
              href="/appointments/new"
              className="block w-full text-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              Создать новую запись
            </Link>
            <Link
              href="/doctors"
              className="block w-full text-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Список врачей
            </Link>
            <Link
              href="/schedule"
              className="block w-full text-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Расписание на сегодня
            </Link>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Информация</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li>• Система работает 24/7</li>
            <li>• Записи обновляются в реальном времени</li>
            <li>• Доступ к админке через /admin</li>
            <li>• База данных: PostgreSQL (Supabase)</li>
          </ul>
        </div>
      </div>
    </div>
  )
}