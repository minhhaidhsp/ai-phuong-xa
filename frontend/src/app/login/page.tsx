"use client"
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'
export default function LoginPage() {
  const [u,setU]=useState(''); const [p,setP]=useState('')
  const {login,isLoading,error,clearError}=useAuthStore(); const router=useRouter()
  const handleSubmit=async(e:React.FormEvent)=>{
    e.preventDefault(); clearError()
    try{ await login(u,p); router.push('/home') }catch{}
  }
  return (
    <div style={{minHeight:'100vh',background:'#eef2f7',display:'flex',alignItems:'center',justifyContent:'center',padding:'16px'}}>
      <div style={{width:'100%',maxWidth:'360px'}}>
        <div style={{textAlign:'center',marginBottom:'32px'}}>
          <div style={{display:'inline-flex',alignItems:'center',justifyContent:'center',width:'56px',height:'56px',borderRadius:'16px',background:'linear-gradient(135deg,#1652f0,#3b9eff)',fontSize:'24px',marginBottom:'16px'}}>🏛️</div>
          <h1 style={{fontSize:'20px',fontWeight:800,color:'#0c1e3c',letterSpacing:'-.02em'}}>AI Phường / Xã</h1>
          <p style={{fontSize:'12px',color:'#5c738a',marginTop:'4px',fontWeight:500}}>TP. Hồ Chí Minh · Hệ thống quản lý hành chính</p>
        </div>
        <div style={{background:'#fff',borderRadius:'16px',border:'1px solid #dce3ef',overflow:'hidden',boxShadow:'0 6px 24px rgba(12,30,60,.13)'}}>
          <div style={{background:'linear-gradient(to right,#0c1e3c,#1652f0)',padding:'16px 24px'}}>
            <p style={{color:'#fff',fontWeight:700,fontSize:'14px'}}>Đăng nhập hệ thống</p>
            <p style={{color:'rgba(255,255,255,.5)',fontSize:'12px',marginTop:'2px'}}>Vui lòng nhập tài khoản được cấp</p>
          </div>
          <form onSubmit={handleSubmit} style={{padding:'24px',display:'flex',flexDirection:'column',gap:'16px'}}>
            {error&&<div style={{background:'#fef2f2',border:'1px solid #fecaca',color:'#991b1b',borderRadius:'8px',padding:'10px 12px',fontSize:'12px'}}>⚠️ {error}</div>}
            <div>
              <label style={{display:'block',fontSize:'11px',fontWeight:700,color:'#2d4060',marginBottom:'6px'}}>Tên đăng nhập</label>
              <input type="text" value={u} onChange={e=>setU(e.target.value)} style={{width:'100%',padding:'10px 12px',border:'2px solid #dce3ef',borderRadius:'8px',fontSize:'13px',fontFamily:'inherit',outline:'none',background:'#f8fafc'}} placeholder="admin / canbo01 / lanhdao01" required autoFocus/>
            </div>
            <div>
              <label style={{display:'block',fontSize:'11px',fontWeight:700,color:'#2d4060',marginBottom:'6px'}}>Mật khẩu</label>
              <input type="password" value={p} onChange={e=>setP(e.target.value)} style={{width:'100%',padding:'10px 12px',border:'2px solid #dce3ef',borderRadius:'8px',fontSize:'13px',fontFamily:'inherit',outline:'none',background:'#f8fafc'}} placeholder="••••••••" required/>
            </div>
            <button type="submit" disabled={isLoading} style={{width:'100%',padding:'11px',borderRadius:'8px',fontWeight:700,fontSize:'13px',color:'#fff',background:'#1652f0',border:'none',cursor:isLoading?'not-allowed':'pointer',opacity:isLoading?.6:1,fontFamily:'inherit'}}>
              {isLoading?'⏳ Đang đăng nhập...':'🔐 Đăng nhập'}
            </button>
          </form>
        </div>
        <p style={{textAlign:'center',fontSize:'11px',color:'#8fa3bb',marginTop:'16px'}}>Phiên bản 1.0 · Sprint 9 · 2026</p>
      </div>
    </div>
  )
}
