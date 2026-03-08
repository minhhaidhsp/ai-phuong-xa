"use client"
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
import Sidebar from '@/components/layout/Sidebar'
import Topbar from '@/components/layout/Topbar'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { token, restoreSession } = useAuthStore()
  const router = useRouter()
  const [hydrated, setHydrated] = useState(false)

  useEffect(() => {
    restoreSession().finally(() => setHydrated(true))
  }, [])

  useEffect(() => {
    if (hydrated && !token) router.replace('/login')
  }, [hydrated, token, router])

  if (!hydrated) return (
    <div style={{ display:'flex', height:'100vh', alignItems:'center', justifyContent:'center', background:'#eef2f7' }}>
      <div style={{ fontSize:'13px', color:'#5c738a' }}>⏳ Đang tải...</div>
    </div>
  )

  if (!token) return null

  return (
    <div style={{ display:'flex', height:'100vh', overflow:'hidden' }}>
      <Sidebar/>
      <div style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden', minWidth:0 }}>
        <Topbar/>
        <main style={{ flex:1, overflowY:'auto', padding:'20px 22px', overflowX:'hidden' }}>
          {children}
        </main>
      </div>
    </div>
  )
}
