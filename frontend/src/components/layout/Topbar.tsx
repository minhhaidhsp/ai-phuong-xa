"use client"
import { usePathname } from 'next/navigation'
const META:Record<string,{title:string;crumb:string}>={
  '/home':      {title:'Trang chủ',            crumb:'Tổng quan'},
  '/tiep-nhan': {title:'Tiếp nhận hồ sơ',      crumb:'Nghiệp vụ'},
  '/theo-doi':  {title:'Theo dõi xử lý',       crumb:'Nghiệp vụ'},
  '/phan-loai': {title:'Phân loại hồ sơ AI',   crumb:'Nghiệp vụ · AI'},
  '/hoi-dap':   {title:'Hỏi đáp AI',           crumb:'Nghiệp vụ · AI'},
  '/tra-cuu':   {title:'Tra cứu pháp luật',    crumb:'Nghiệp vụ'},
  '/soan-thao': {title:'Soạn thảo văn bản',    crumb:'Nghiệp vụ · AI'},
  '/bao-cao':   {title:'Tổng hợp báo cáo',     crumb:'Quản lý'},
  '/nhiem-vu':  {title:'Nhiệm vụ & KPI',       crumb:'Quản lý'},
  '/dashboard': {title:'Dashboard lãnh đạo',   crumb:'Quản lý'},
  '/kpi':       {title:'KPI & Hiệu quả',       crumb:'Hệ thống'},
  '/lgsp':      {title:'Tích hợp LGSP',        crumb:'Hệ thống'},
  '/ragas':     {title:'RAGAS Evaluation',     crumb:'Hệ thống · Admin'},
}
export default function Topbar(){
  const path=usePathname(); const m=META[path]||{title:path,crumb:'Hệ thống'}
  const today=new Date().toLocaleDateString('vi-VN',{weekday:'short',day:'2-digit',month:'2-digit',year:'numeric'})
  return (
    <header style={{height:'54px',background:'#fff',borderBottom:'1px solid #dce3ef',display:'flex',alignItems:'center',padding:'0 22px',gap:'12px',flexShrink:0}}>
      <div>
        <div style={{fontSize:'10.5px',color:'#8fa3bb',marginBottom:'1px'}}>{m.crumb}</div>
        <div style={{fontSize:'15px',fontWeight:800,color:'#0c1e3c',letterSpacing:'-.02em',lineHeight:'1'}}>{m.title}</div>
      </div>
      <div style={{marginLeft:'auto',display:'flex',alignItems:'center',gap:'8px'}}>
        <div style={{fontFamily:'JetBrains Mono,monospace',fontSize:'11px',color:'#5c738a',background:'#f8fafc',border:'1px solid #dce3ef',padding:'5px 11px',borderRadius:'7px'}}>{today}</div>
        <div style={{width:'32px',height:'32px',borderRadius:'7px',border:'1px solid #dce3ef',background:'#fff',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'15px',cursor:'pointer',position:'relative'}}>
          🔔<span style={{position:'absolute',top:'4px',right:'4px',width:'6px',height:'6px',borderRadius:'50%',background:'#d93025',border:'1.5px solid #fff'}}/>
        </div>
      </div>
    </header>
  )
}
