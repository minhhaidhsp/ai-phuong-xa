import type { Metadata } from 'next'
import { Toaster } from 'react-hot-toast'
import './globals.css'
export const metadata: Metadata = { title:'AI Phuong/Xa — TP.HCM' }
export default function RootLayout({ children }:{ children:React.ReactNode }) {
  return (
    <html lang="vi"><body>
      {children}
      <Toaster position="top-right" toastOptions={{ style:{ fontFamily:'Plus Jakarta Sans,sans-serif', fontSize:'13px', borderRadius:'10px' } }} />
    </body></html>
  )
}
