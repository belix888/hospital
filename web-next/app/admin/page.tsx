import Link from 'next/link'
import { getStats } from '@/lib/db'

export const dynamic = 'force-dynamic'

export default async function AdminPage() {
  const stats = await getStats()

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Админ-панель</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{stats.doctorsCount}</div>
          <div className="text-sm text-gray-600">Врачей</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{stats.patientsCount}</div>
          <div className="text-sm text-gray-600">Пациентов</div>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-yellow-600">{stats.totalAppointments}</div>
          <div className="text-sm text-gray-600">Всего записей</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">{stats.roomsCount}</div>
          <div className="text-sm text-gray-600">Кабинетов</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Управление</h2>
          <div className="space-y-3">
            <Link href="/admin/doctors" className="block py-2 px-4 bg-gray-100 rounded hover:bg-gray-200">
              👨‍⚕️ Управление врачами
            </Link>
            <Link href="/admin/patients" className="block py-2 px-4 bg-gray-100 rounded hover:bg-gray-200">
              👤 Управление пациентами
            </Link>
            <Link href="/admin/rooms" className="block py-2 px-4 bg-gray-100 rounded hover:bg-gray-200">
              🚪 Управление кабинетами
            </Link>
            <Link href="/admin/appointments" className="block py-2 px-4 bg-gray-100 rounded hover:bg-gray-200">
              📅 Все записи
            </Link>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Быстрые ссылки</h2>
          <div className="space-y-3">
            <Link href="/" className="block py-2 px-4 bg-blue-100 rounded hover:bg-blue-200 text-blue-700">
              🏠 На главную
            </Link>
            <Link href="/schedule" className="block py-2 px-4 bg-green-100 rounded hover:bg-green-200 text-green-700">
              📅 Расписание
            </Link>
            <Link href="/doctors" className="block py-2 px-4 bg-purple-100 rounded hover:bg-purple-200 text-purple-700">
              👨‍⚕️ Врачи
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}