"use client"
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuthStore } from '@/stores/authStore'

const NAV=[
  {href:'/home',      icon:'🏠', label:'Trang chủ'},
  {href:'/tiep-nhan', icon:'📥', label:'Tiếp nhận hồ sơ',    badge:'3',   bc:'#d93025'},
  {href:'/theo-doi',  icon:'📋', label:'Theo dõi xử lý',     badge:'7',   bc:'#e07b12'},
  {href:'/phan-loai', icon:'🗂️', label:'Phân loại hồ sơ AI', badge:'AI',  bc:'#1652f0'},
  {href:'/hoi-dap',   icon:'🤖', label:'Hỏi đáp AI'},
  {href:'/tra-cuu',   icon:'🔍', label:'Tra cứu pháp luật'},
  {href:'/soan-thao', icon:'✍️', label:'Soạn thảo văn bản'},
]
const NAV2=[
  {href:'/bao-cao',   icon:'📊', label:'Tổng hợp báo cáo',   badge:'Mới', bc:'#0f7b3c'},
  {href:'/nhiem-vu',  icon:'✅', label:'Nhiệm vụ & KPI',     badge:'2',   bc:'#d93025'},
  {href:'/dashboard', icon:'📈', label:'Dashboard lãnh đạo', roles:['admin','lanh_dao']},
]
const NAV3=[
  {href:'/kpi',   icon:'🎯', label:'KPI & Hiệu quả'},
  {href:'/lgsp',  icon:'🔗', label:'Tích hợp LGSP',    roles:['admin']},
  {href:'/ragas', icon:'🔬', label:'RAGAS Evaluation', roles:['admin']},
]

type NavItem={href:string;icon:string;label:string;badge?:string;bc?:string;roles?:string[]}

function Item({item,role}:{item:NavItem;role:string}){
  const path=usePathname(); const on=path===item.href
  if(item.roles&&!item.roles.includes(role)) return null
  return (
    <Link href={item.href} style={{display:'flex',alignItems:'center',gap:'9px',padding:'7px 14px',margin:'1px 6px',borderRadius:'8px',fontSize:'12.5px',fontWeight:on?700:500,color:on?'#fff':'rgba(255,255,255,.5)',background:on?'rgba(22,82,240,.3)':'transparent',textDecoration:'none',position:'relative',transition:'all .15s'}}>
      {on&&<span style={{position:'absolute',left:'-6px',top:'50%',transform:'translateY(-50%)',width:'3px',height:'18px',background:'#3b9eff',borderRadius:'0 3px 3px 0'}}/>}
      <span style={{fontSize:'14px',width:'18px',textAlign:'center',flexShrink:0}}>{item.icon}</span>
      <span style={{flex:1}}>{item.label}</span>
      {item.badge&&<span style={{fontSize:'9.5px',fontWeight:800,padding:'1px 7px',borderRadius:'20px',background:item.bc||'#1652f0',color:'#fff'}}>{item.badge}</span>}
    </Link>
  )
}

function Sec({label,items,role}:{label:string;items:NavItem[];role:string}){
  return <div style={{marginBottom:'4px'}}>
    <div style={{padding:'14px 14px 3px',fontSize:'9px',fontWeight:800,letterSpacing:'.12em',textTransform:'uppercase',color:'rgba(255,255,255,.25)'}}>{label}</div>
    {items.map(i=><Item key={i.href} item={i} role={role}/>)}
  </div>
}

export default function Sidebar(){
  const {user,logout}=useAuthStore()
  const role=user?.vai_tro||'can_bo'
  const init=user?.ho_ten?.split(' ').map((w:string)=>w[0]).slice(-2).join('').toUpperCase()||'?'
  const rl:Record<string,string>={admin:'Quản trị viên',lanh_dao:'Lãnh đạo',can_bo:'Cán bộ'}
  return (
    <nav style={{width:'230px',background:'#0c1e3c',display:'flex',flexDirection:'column',flexShrink:0,overflowY:'auto'}}>
      <div style={{height:'54px',padding:'0 16px',display:'flex',alignItems:'center',gap:'10px',borderBottom:'1px solid rgba(255,255,255,.07)',flexShrink:0}}>
        <div style={{width:'30px',height:'30px',borderRadius:'8px',background:'linear-gradient(135deg,#1652f0,#3b9eff)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'15px',flexShrink:0}}>🏛️</div>
        <div>
          <strong style={{display:'block',fontSize:'12px',fontWeight:800,color:'#fff'}}>AI Phường/Xã</strong>
          <span style={{fontSize:'10px',color:'rgba(255,255,255,.35)'}}>TP. Hồ Chí Minh</span>
        </div>
      </div>
      <div style={{flex:1,paddingTop:'8px'}}>
        <Sec label="Nghiệp vụ" items={NAV} role={role}/>
        <div style={{height:'1px',background:'rgba(255,255,255,.07)',margin:'5px 14px'}}/>
        <Sec label="Quản lý" items={NAV2} role={role}/>
        <div style={{height:'1px',background:'rgba(255,255,255,.07)',margin:'5px 14px'}}/>
        <Sec label="Hệ thống" items={NAV3} role={role}/>
      </div>
      <div style={{padding:'10px',borderTop:'1px solid rgba(255,255,255,.07)'}}>
        <div style={{display:'flex',alignItems:'center',gap:'9px',padding:'8px 10px',borderRadius:'8px',background:'rgba(255,255,255,.06)'}}>
          <div style={{width:'28px',height:'28px',borderRadius:'8px',flexShrink:0,background:'linear-gradient(135deg,#1652f0,#0b8a7e)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:'11px',fontWeight:800,color:'#fff'}}>{init}</div>
          <div style={{flex:1,minWidth:0}}>
            <span style={{display:'block',fontSize:'11.5px',fontWeight:700,color:'#fff',overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{user?.ho_ten||'—'}</span>
            <span style={{fontSize:'10px',color:'rgba(255,255,255,.35)'}}>{rl[role]}</span>
          </div>
          <button onClick={logout} style={{background:'none',border:'none',color:'rgba(255,255,255,.35)',cursor:'pointer',fontSize:'14px'}} title="Đăng xuất">⏏</button>
        </div>
      </div>
    </nav>
  )
}
