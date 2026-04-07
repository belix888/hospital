import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Больница - Система управления',
  description: 'Система управления записями больницы',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          <nav className="bg-white shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex">
                  <div className="flex-shrink-0 flex items-center">
                    <span className="text-xl font-bold text-blue-600">🏥 Больница</span>
                  </div>
                  <div className="ml-6 flex space-x-4">
                    <a href="/" className="text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                      Главная
                    </a>
                    <a href="/doctors" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                      Врачи
                    </a>
                    <a href="/appointments" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                      Записи
                    </a>
                    <a href="/schedule" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                      Расписание
                    </a>
                  </div>
                </div>
                <div className="flex items-center">
                  <a href="/admin" className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium">
                    Админка
                  </a>
                </div>
              </div>
            </div>
          </nav>
          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}