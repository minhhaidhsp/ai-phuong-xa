"use client"
import { useState, useMemo, useEffect } from 'react'
import { formatDate, daysLeftLabel } from '@/lib/utils'
import { hoSoApi } from '@/lib/api'
import { TRANG_THAI_LABEL, TRANG_THAI_COLOR } from '@/types/ho-so'
import toast from 'react-hot-toast'

// ── Mock data (sau nối API /ho-so) ───────────────────────────
const MOCK_DATA = [
  {id:'HS-2026-0341',ten:'Đăng ký kết hôn',cd:'Trần Thị Mai Lan',tt:'DANG_XU_LY',han:'2026-03-08',cb:'Nguyễn Hùng',lv:'Hộ tịch',pr:'KHAN_CAP',nguon:'truc_tiep',cccd:'079085012345',dia_chi:'142/5 Trần Quý Khoách, P.Tân Định, Q.1',sdt:'0901234567',ngay_nop:'2026-03-05',ghi_chu:''},
  {id:'HS-2026-0340',ten:'Đăng ký khai sinh',cd:'Phạm Thị Bích',tt:'CHO_TIEP_NHAN',han:'2026-03-10',cb:'Lê Thị Hoa',lv:'Hộ tịch',pr:'TRUNG_BINH',nguon:'truc_tiep',cccd:'079012345678',dia_chi:'22 Nguyễn Trãi, P.Bến Thành, Q.1',sdt:'0912345678',ngay_nop:'2026-03-06',ghi_chu:''},
  {id:'HS-2026-0339',ten:'Đăng ký thường trú',cd:'Nguyễn Văn Bình',tt:'YEU_CAU_BO_SUNG',han:'2026-03-10',cb:'Trần Quang Tú',lv:'Cư trú',pr:'TRUNG_BINH',nguon:'buu_chinh',cccd:'079087654321',dia_chi:'55 Lê Lợi, P.Bến Nghé, Q.1',sdt:'',ngay_nop:'2026-03-04',ghi_chu:'Thiếu giấy tờ nhà ở'},
  {id:'HS-2026-0338',ten:'Cấp lại sổ hộ khẩu',cd:'Vũ Minh Tuấn',tt:'DANG_XU_LY',han:'2026-03-07',cb:'Nguyễn Hùng',lv:'Cư trú',pr:'KHAN_CAP',nguon:'truc_tiep',cccd:'079011112222',dia_chi:'88 Hai Bà Trưng, P.Đa Kao, Q.1',sdt:'0988112233',ngay_nop:'2026-03-03',ghi_chu:'Khẩn — mất sổ'},
  {id:'HS-2026-0335',ten:'Khai sinh — Nguyễn Minh Khoa',cd:'Nguyễn Thị Hoa (mẹ)',tt:'YEU_CAU_BO_SUNG',han:'2026-03-10',cb:'Lê Thị Hoa',lv:'Hộ tịch',pr:'TRUNG_BINH',nguon:'truc_tiep',cccd:'079099887766',dia_chi:'10 Đinh Tiên Hoàng, Q.1',sdt:'0933445566',ngay_nop:'2026-03-03',ghi_chu:''},
  {id:'HS-2026-0330',ten:'Đăng ký tạm trú',cd:'Đỗ Văn Long',tt:'HOAN_THANH',han:'2026-03-03',cb:'Lê Thị Hoa',lv:'Cư trú',pr:'TRUNG_BINH',nguon:'lgsp',cccd:'079055443322',dia_chi:'33 Phạm Ngũ Lão, Q.1',sdt:'0977665544',ngay_nop:'2026-02-28',ghi_chu:''},
  {id:'HS-2026-0328',ten:'Xác nhận tình trạng hôn nhân',cd:'Lê Hoàng Sơn',tt:'HOAN_THANH',han:'2026-03-05',cb:'Nguyễn Hùng',lv:'Hộ tịch',pr:'TRUNG_BINH',nguon:'truc_tiep',cccd:'079044332211',dia_chi:'5 Ngô Đức Kế, Q.1',sdt:'0966554433',ngay_nop:'2026-02-27',ghi_chu:''},
  {id:'HS-2026-0325',ten:'Cấp phép xây dựng nhà ở',cd:'Nguyễn Thanh Bình',tt:'DANG_XU_LY',han:'2026-03-15',cb:'Trần Quang Tú',lv:'Đất đai',pr:'TRUNG_BINH',nguon:'truc_tiep',cccd:'079033221100',dia_chi:'120 Đinh Tiên Hoàng, Q.Bình Thạnh',sdt:'0955443322',ngay_nop:'2026-02-25',ghi_chu:''},
  {id:'HS-2026-0320',ten:'Đăng ký hộ kinh doanh',cd:'Bùi Thị Lan',tt:'HOAN_THANH',han:'2026-03-04',cb:'Nguyễn Hùng',lv:'Kinh doanh',pr:'TRUNG_BINH',nguon:'lgsp',cccd:'079022110099',dia_chi:'77 Lý Tự Trọng, Q.1',sdt:'0944332211',ngay_nop:'2026-02-24',ghi_chu:''},
  {id:'HS-2026-0315',ten:'Xác nhận thường trú',cd:'Trần Văn Nam',tt:'HOAN_THANH',han:'2026-03-02',cb:'Lê Thị Hoa',lv:'Cư trú',pr:'TRUNG_BINH',nguon:'buu_chinh',cccd:'079011009988',dia_chi:'200 Lê Văn Sỹ, Q.3',sdt:'0933221100',ngay_nop:'2026-02-20',ghi_chu:''},
]

type HoSo = typeof MOCK_DATA[0]

const TRANG_THAI_OPTIONS = [
  {value:'', label:'Tất cả trạng thái'},
  {value:'CHO_TIEP_NHAN', label:'Chờ tiếp nhận'},
  {value:'DANG_XU_LY',    label:'Đang xử lý'},
  {value:'YEU_CAU_BO_SUNG',label:'Yêu cầu bổ sung'},
  {value:'CHO_PHE_DUYET', label:'Chờ phê duyệt'},
  {value:'HOAN_THANH',    label:'Hoàn thành'},
  {value:'TU_CHOI',       label:'Từ chối'},
]
const LINH_VUC_OPTIONS = ['','Hộ tịch','Cư trú','Đất đai','Kinh doanh','Chứng thực']


const NGUON_ICON: Record<string,string> = {
  'TRUC_TIEP': '🏢',
  'TRUC_TUYEN': '🌐', 
  'BUU_CHINH': '📮',
  'DVC_TRUC_TUYEN': '💻',
}
const LV_COLOR: Record<string,string> = {
  'Hộ tịch':    '#1652f0',
  'Cư trú':     '#0b8a7e',
  'Đất đai':    '#92400e',
  'Kinh doanh': '#6d28d9',
  'Chứng thực': '#0f7b3c',
}
const NGUON_LABEL:Record<string,string> = {truc_tiep:'Trực tiếp',buu_chinh:'Bưu chính',lgsp:'🔗 LGSP'}
const PR_LABEL:Record<string,string> = {KHAN_CAP:'⚡ Khẩn cấp',CAO:'🔴 Cao',TRUNG_BINH:'Thường',THAP:'Thấp'}
const PR_COLOR:Record<string,string> = {KHAN_CAP:'#d93025',CAO:'#e07b12',TRUNG_BINH:'#5c738a',THAP:'#8fa3bb'}

const S_SELECT = {
  padding:'8px 28px 8px 10px', border:'1.5px solid #dce3ef', borderRadius:'8px',
  fontFamily:'inherit', fontSize:'12.5px', background:'#fff', outline:'none',
  color:'#0c1e3c', appearance:'none' as React.CSSProperties['appearance'],
  backgroundImage:"url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath fill='%235c738a' d='M0 0l5 6 5-6z'/%3E%3C/svg%3E\")",
  backgroundRepeat:'no-repeat', backgroundPosition:'right 10px center',
} as React.CSSProperties

// ── Status Badge ──────────────────────────────────────────────
function StatusBadge({ tt }: { tt: string }) {
  const label = TRANG_THAI_LABEL[tt as keyof typeof TRANG_THAI_LABEL] || tt
  const color = TRANG_THAI_COLOR[tt as keyof typeof TRANG_THAI_COLOR] || '#5c738a'
  return (
    <span style={{ display:'inline-flex', alignItems:'center', gap:'4px', fontSize:'10.5px', fontWeight:700, padding:'3px 8px', borderRadius:'20px', background:color+'18', color }}>
      <span style={{ width:'5px', height:'5px', borderRadius:'50%', background:color, flexShrink:0 }}/>
      {label}
    </span>
  )
}

// ── Deadline cell ─────────────────────────────────────────────
function Deadline({ han, tt }: { han: string; tt: string }) {
  if (tt === 'HOAN_THANH') return <span style={{ fontSize:'12px', color:'#0f7b3c', fontWeight:600 }}>✓ Hoàn thành</span>
  const { label, color } = daysLeftLabel(han)
  const d = Math.ceil((new Date(han).getTime() - Date.now()) / 86400000)
  return (
    <div>
      <div style={{ fontSize:'12px', fontWeight: d <= 0 ? 800 : d <= 2 ? 700 : 500, color }}>{d <= 0 ? '⚠️ ' : ''}{formatDate(han)}</div>
      <div style={{ fontSize:'10.5px', color, fontWeight:600 }}>{label}</div>
    </div>
  )
}

// ── Modal chi tiết ────────────────────────────────────────────
function HoSoModal({ hs, onClose }: { hs: HoSo; onClose: () => void }) {
  const [tab, setTab] = useState<'info'|'lich-su'|'ai'>('info')
  const { label: deadlineLabel, color: deadlineColor } = daysLeftLabel(hs.han)

  const tabs = [{id:'info',label:'📋 Thông tin'},{id:'lich-su',label:'📅 Lịch sử'},{id:'ai',label:'🤖 AI gợi ý'}] as const

  return (
    <div style={{ position:'fixed', inset:0, background:'rgba(12,30,60,.45)', zIndex:1000, display:'flex', alignItems:'center', justifyContent:'center', padding:'20px' }} onClick={onClose}>
      <div style={{ background:'#fff', borderRadius:'16px', width:'100%', maxWidth:'580px', maxHeight:'85vh', overflow:'hidden', display:'flex', flexDirection:'column', boxShadow:'0 20px 60px rgba(12,30,60,.25)' }} onClick={e=>e.stopPropagation()}>
        {/* Modal header */}
        <div style={{ background:'linear-gradient(135deg,#0c1e3c,#1652f0)', padding:'16px 20px', display:'flex', alignItems:'flex-start', justifyContent:'space-between' }}>
          <div>
            <div style={{ fontFamily:'JetBrains Mono,monospace', fontSize:'11px', color:'rgba(255,255,255,.5)', marginBottom:'4px' }}>{hs.id}</div>
            <div style={{ fontSize:'16px', fontWeight:800, color:'#fff', lineHeight:1.2 }}>{hs.ten}</div>
            <div style={{ fontSize:'12px', color:'rgba(255,255,255,.6)', marginTop:'4px' }}>{hs.cd} · {hs.lv}</div>
          </div>
          <button onClick={onClose} style={{ background:'rgba(255,255,255,.15)', border:'none', color:'#fff', width:'28px', height:'28px', borderRadius:'8px', cursor:'pointer', fontSize:'14px', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }}>✕</button>
        </div>

        {/* Status row */}
        <div style={{ padding:'10px 20px', background:'#f8fafc', borderBottom:'1px solid #dce3ef', display:'flex', alignItems:'center', gap:'10px', flexWrap:'wrap' }}>
          <StatusBadge tt={hs.tt} />
          <span style={{ fontSize:'11.5px', color:PR_COLOR[hs.pr], fontWeight:700 }}>{PR_LABEL[hs.pr]}</span>
          <span style={{ fontSize:'11.5px', color:'#5c738a' }}>📥 {NGUON_LABEL[hs.nguon]}</span>
          <span style={{ marginLeft:'auto', fontSize:'11.5px', fontWeight:700, color:deadlineColor }}>⏰ {deadlineLabel}</span>
        </div>

        {/* Tabs */}
        <div style={{ display:'flex', gap:'2px', padding:'8px 20px 0', borderBottom:'1px solid #dce3ef', background:'#fff' }}>
          {tabs.map(t => (
            <button key={t.id} onClick={()=>setTab(t.id)} style={{ padding:'7px 14px', border:'none', background:'none', cursor:'pointer', fontFamily:'inherit', fontSize:'12px', fontWeight: tab===t.id ? 800 : 500, color: tab===t.id ? '#1652f0' : '#5c738a', borderBottom: tab===t.id ? '2px solid #1652f0' : '2px solid transparent', marginBottom:'-1px' }}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div style={{ flex:1, overflow:'y-auto', overflowY:'auto', padding:'18px 20px' }}>
          {tab === 'info' && (
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'14px' }}>
              {[
                ['Họ tên công dân', hs.cd],
                ['Số CCCD', hs.cccd],
                ['Số điện thoại', hs.sdt || '—'],
                ['Ngày nộp', formatDate(hs.ngay_nop)],
                ['Địa chỉ', hs.dia_chi],
                ['Hạn giải quyết', formatDate(hs.han)],
                ['Cán bộ xử lý', hs.cb],
                ['Ghi chú', hs.ghi_chu || '—'],
              ].map(([label, val]) => (
                <div key={label}>
                  <div style={{ fontSize:'10.5px', fontWeight:700, color:'#5c738a', textTransform:'uppercase', letterSpacing:'.05em', marginBottom:'3px' }}>{label}</div>
                  <div style={{ fontSize:'13px', color:'#0c1e3c', fontWeight:500, wordBreak:'break-word' }}>{val}</div>
                </div>
              ))}
              <div style={{ gridColumn:'1/-1', padding:'10px 14px', background:'#eff6ff', borderRadius:'8px', border:'1px solid #bfdbfe' }}>
                <div style={{ fontSize:'10.5px', fontWeight:700, color:'#1652f0', marginBottom:'4px' }}>📋 MÃ HỒ SƠ</div>
                <div style={{ fontFamily:'JetBrains Mono,monospace', fontSize:'14px', fontWeight:800, color:'#0c1e3c', letterSpacing:'.05em' }}>{hs.id}</div>
              </div>
            </div>
          )}

          {tab === 'lich-su' && (
            <div style={{ display:'flex', flexDirection:'column', gap:'0' }}>
              {[
                {time:formatDate(hs.ngay_nop)+' 08:30', icon:'📥', label:'Tiếp nhận hồ sơ', desc:`Tiếp nhận qua ${NGUON_LABEL[hs.nguon]}`, color:'#0f7b3c'},
                {time:formatDate(hs.ngay_nop)+' 08:32', icon:'🤖', label:'AI phân loại', desc:`Phân loại: ${hs.ten} · Lĩnh vực: ${hs.lv}`, color:'#1652f0'},
                {time:formatDate(hs.ngay_nop)+' 09:00', icon:'👤', label:'Phân công xử lý', desc:`Giao cho: ${hs.cb}`, color:'#6d28d9'},
                ...(hs.tt==='HOAN_THANH' ? [{time:formatDate(hs.han)+' 14:00', icon:'✅', label:'Hoàn thành', desc:'Hồ sơ đã được giải quyết xong', color:'#0f7b3c'}] : []),
                ...(hs.tt==='YEU_CAU_BO_SUNG' ? [{time:formatDate(hs.han)+' 10:00', icon:'⚠️', label:'Yêu cầu bổ sung', desc:hs.ghi_chu||'Cần bổ sung giấy tờ', color:'#e07b12'}] : []),
              ].map((ev, i, arr) => (
                <div key={i} style={{ display:'flex', gap:'12px', paddingBottom: i<arr.length-1 ? '16px' : '0', position:'relative' }}>
                  {i<arr.length-1 && <div style={{ position:'absolute', left:'17px', top:'34px', bottom:'0', width:'2px', background:'#f1f5f9' }}/>}
                  <div style={{ width:'34px', height:'34px', borderRadius:'50%', background:ev.color+'18', border:`2px solid ${ev.color}30`, display:'flex', alignItems:'center', justifyContent:'center', fontSize:'14px', flexShrink:0 }}>{ev.icon}</div>
                  <div style={{ flex:1, paddingTop:'4px' }}>
                    <div style={{ fontSize:'12.5px', fontWeight:700, color:'#0c1e3c' }}>{ev.label}</div>
                    <div style={{ fontSize:'11.5px', color:'#5c738a', marginTop:'2px' }}>{ev.desc}</div>
                    <div style={{ fontSize:'10.5px', color:'#8fa3bb', marginTop:'3px', fontFamily:'JetBrains Mono,monospace' }}>{ev.time}</div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {tab === 'ai' && (
            <div style={{ display:'flex', flexDirection:'column', gap:'10px' }}>
              <div style={{ padding:'12px 14px', background:'#f0fdf4', borderRadius:'10px', border:'1px solid #86efac' }}>
                <div style={{ fontSize:'12px', fontWeight:800, color:'#166534', marginBottom:'6px' }}>🤖 Phân tích AI</div>
                <div style={{ fontSize:'12.5px', color:'#166534', lineHeight:1.6 }}>
                  Hồ sơ <strong>{hs.ten}</strong> thuộc lĩnh vực <strong>{hs.lv}</strong>.
                  {hs.tt==='YEU_CAU_BO_SUNG' && ' Hiện đang yêu cầu bổ sung giấy tờ — cần liên hệ công dân sớm.'}
                  {hs.tt==='DANG_XU_LY' && ' Đang trong quá trình xử lý, theo dõi sát thời hạn.'}
                  {hs.tt==='HOAN_THANH' && ' Hồ sơ đã hoàn thành đúng hạn.'}
                </div>
              </div>
              <div style={{ padding:'12px 14px', background:'#eff6ff', borderRadius:'10px', border:'1px solid #bfdbfe' }}>
                <div style={{ fontSize:'12px', fontWeight:800, color:'#1652f0', marginBottom:'6px' }}>📋 Căn cứ pháp lý</div>
                <div style={{ fontSize:'12px', color:'#1e40af', lineHeight:1.7 }}>
                  {hs.lv==='Hộ tịch' && '• Luật Hộ tịch 2014\n• Nghị định 123/2015/NĐ-CP\n• Thông tư 04/2020/TT-BTP'}
                  {hs.lv==='Cư trú' && '• Luật Cư trú 2020\n• Nghị định 62/2021/NĐ-CP'}
                  {hs.lv==='Đất đai' && '• Luật Đất đai 2024\n• Nghị định 101/2024/NĐ-CP'}
                  {hs.lv==='Kinh doanh' && '• Luật Doanh nghiệp 2020\n• Nghị định 01/2021/NĐ-CP'}
                </div>
              </div>
              <div style={{ padding:'12px 14px', background:'#fefce8', borderRadius:'10px', border:'1px solid #fde68a' }}>
                <div style={{ fontSize:'12px', fontWeight:800, color:'#92400e', marginBottom:'6px' }}>⚡ Hành động gợi ý</div>
                <div style={{ fontSize:'12px', color:'#78350f', lineHeight:1.7 }}>
                  {hs.tt==='YEU_CAU_BO_SUNG' && '• Gọi điện công dân: ' + (hs.sdt||'chưa có SĐT') + '\n• Gửi thông báo bổ sung qua email\n• Gia hạn thêm 3 ngày nếu cần'}
                  {hs.tt==='DANG_XU_LY' && '• Kiểm tra tiến độ xử lý\n• Chuẩn bị văn bản kết quả\n• Thông báo ngày trả kết quả cho công dân'}
                  {hs.tt==='CHO_TIEP_NHAN' && '• Phân công cán bộ xử lý\n• Kiểm tra đầy đủ giấy tờ\n• Cập nhật trạng thái trong hệ thống'}
                  {hs.tt==='HOAN_THANH' && '• Lưu hồ sơ vào kho lưu trữ\n• Cập nhật báo cáo tháng\n• Thông báo kết quả cho công dân'}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div style={{ padding:'12px 20px', borderTop:'1px solid #dce3ef', display:'flex', gap:'8px', background:'#f8fafc' }}>
          {hs.tt !== 'HOAN_THANH' && (
            <button onClick={()=>{ toast.success('Đã cập nhật trạng thái'); onClose() }}
              style={{ padding:'8px 16px', borderRadius:'8px', fontWeight:700, fontSize:'12.5px', color:'#fff', background:'#1652f0', border:'none', cursor:'pointer', fontFamily:'inherit' }}>
              ✏️ Cập nhật trạng thái
            </button>
          )}
          <button onClick={()=>toast('Đang mở soạn thảo...')}
            style={{ padding:'8px 16px', borderRadius:'8px', fontWeight:700, fontSize:'12.5px', color:'#2d4060', background:'#fff', border:'1.5px solid #dce3ef', cursor:'pointer', fontFamily:'inherit' }}>
            ✍️ Soạn văn bản
          </button>
          <button onClick={onClose}
            style={{ padding:'8px 16px', borderRadius:'8px', fontWeight:700, fontSize:'12.5px', color:'#5c738a', background:'transparent', border:'none', cursor:'pointer', fontFamily:'inherit', marginLeft:'auto' }}>
            Đóng
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Grid layout (shared between header and rows) ──────────────
const GRID = '140px 1fr 110px 140px 160px 90px 140px 88px'
// cols:        MãHS  TT/CD  LV     TrangThai Han    Ngay  CB    TT

// ── Main Page ─────────────────────────────────────────────────
export default function TheodoiPage() {
  const [data, setData] = useState(MOCK_DATA)
  const [loading, setLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [filterTT, setFilterTT] = useState('')
  const [filterLV, setFilterLV] = useState('')
  const [selectedHS, setSelectedHS] = useState<HoSo | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [sortCol, setSortCol] = useState<string>('han')
  const [sortDir, setSortDir] = useState<'asc'|'desc'>('asc')

  useEffect(() => {
    setLoading(true)
    hoSoApi.list({ size: 100 })
      .then(res => {
        const items = res.data?.items || res.data
        if (items?.length) {
          setData(items.map((d: Record<string,unknown>) => {
            return {
              id:       String(d.ma_ho_so || d.id || ''),
              ten:      String(d.thu_tuc_ten || ''),
              cd:       String(d.cong_dan_ho_ten || ''),
              tt:       String(d.trang_thai || ''),
              han:      String(d.han_giai_quyet || '').slice(0, 10),
              cb:       String(d.can_bo_ten || '—'),
              lv:       String(d.linh_vuc || ''),
              pr:       'TRUNG_BINH',
              nguon:    String(d.nguon_tiep_nhan || ''),
              cccd:     String(d.cong_dan_cccd || ''),
              dia_chi:  String(d.cong_dan_dia_chi || ''),
              sdt:      String(d.cong_dan_sdt || ''),
              ngay_nop: String(d.ngay_tiep_nhan || '').slice(0, 10),
              ghi_chu:  String(d.ghi_chu_noi_bo || ''),
            }
          }))
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    const q = search.toLowerCase()
    return data.filter((d: typeof MOCK_DATA[0]) =>
      (!q || d.id.toLowerCase().includes(q) || d.ten.toLowerCase().includes(q) || d.cd.toLowerCase().includes(q)) &&
      (!filterTT || d.tt === filterTT) &&
      (!filterLV || d.lv === filterLV)
    )
  }, [data, search, filterTT, filterLV])


  // Sort
  const sorted = useMemo(() => {
    return [...filtered].sort((a, b) => {
      const va = (a as Record<string,unknown>)[sortCol] ?? ''
      const vb = (b as Record<string,unknown>)[sortCol] ?? ''
      const cmp = String(va).localeCompare(String(vb), 'vi')
      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [filtered, sortCol, sortDir])

  const toggleSort = (col: string) => {
    if (sortCol === col) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortCol(col); setSortDir('asc') }
    setPage(1)
  }

  const SortIcon = ({ col }: { col: string }) => (
    <span style={{ marginLeft:'4px', opacity: sortCol===col ? 1 : 0.3, fontSize:'9px' }}>
      {sortCol===col ? (sortDir==='asc' ? '▲' : '▼') : '⬍'}
    </span>
  )

  // Phân trang
  const totalPages = Math.ceil(sorted.length / pageSize)
  const paginated = sorted.slice((page - 1) * pageSize, page * pageSize)

  // Summary counts
  const counts = useMemo(() => ({
    total:   data.length,
    dang:    data.filter((d:typeof MOCK_DATA[0])=>d.tt==='DANG_XU_LY').length,
    cho:     data.filter((d:typeof MOCK_DATA[0])=>d.tt==='CHO_TIEP_NHAN').length,
    bosung:  data.filter((d:typeof MOCK_DATA[0])=>d.tt==='YEU_CAU_BO_SUNG').length,
    xong:    data.filter((d:typeof MOCK_DATA[0])=>d.tt==='HOAN_THANH').length,
    quahan:  data.filter((d:typeof MOCK_DATA[0])=>d.tt!=='HOAN_THANH' && new Date(d.han)<new Date()).length,
  }), [])

  const summaryCards = [
    {label:'Tổng hồ sơ',  value:counts.total,  color:'#1652f0', bg:'#eff6ff'},
    {label:'Đang xử lý',  value:counts.dang,   color:'#e07b12', bg:'#fffbeb'},
    {label:'Chờ bổ sung', value:counts.bosung, color:'#d97706', bg:'#fef3c7'},
    {label:'Quá hạn',     value:counts.quahan, color:'#d93025', bg:'#fef2f2'},
    {label:'Hoàn thành',  value:counts.xong,   color:'#0f7b3c', bg:'#f0fdf4'},
  ]

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom:'16px' }}>
        <h1 style={{ fontSize:'22px', fontWeight:800, color:'#0c1e3c', letterSpacing:'-.02em' }}>📋 Theo dõi xử lý</h1>
        <p style={{ fontSize:'12px', color:'#5c738a', marginTop:'4px' }}>Danh sách hồ sơ đang xử lý, lọc theo trạng thái và lĩnh vực.</p>
      </div>

      {/* Summary cards */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:'10px', marginBottom:'16px' }}>
        {summaryCards.map(c => (
          <div key={c.label} style={{ background:'#fff', border:'1px solid #dce3ef', borderRadius:'10px', padding:'12px 14px', boxShadow:'0 1px 3px rgba(12,30,60,.06)' }}>
            <div style={{ fontSize:'22px', fontWeight:800, color:c.color }}>{c.value}</div>
            <div style={{ fontSize:'11px', color:'#5c738a', fontWeight:600, marginTop:'2px' }}>{c.label}</div>
            <div style={{ marginTop:'6px', height:'3px', borderRadius:'2px', background:c.bg }}>
              <div style={{ height:'100%', width:`${(c.value/counts.total)*100}%`, background:c.color, borderRadius:'2px', transition:'width .4s' }}/>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display:'flex', gap:'8px', marginBottom:'12px', alignItems:'center', flexWrap:'wrap', background:'#fff', border:'1px solid #dce3ef', borderRadius:'10px', padding:'10px 14px', boxShadow:'0 1px 3px rgba(12,30,60,.06)' }}>
        <div style={{ position:'relative', flex:'0 0 240px' }}>
          <span style={{ position:'absolute', left:'10px', top:'50%', transform:'translateY(-50%)', fontSize:'13px', color:'#8fa3bb' }}>🔍</span>
          <input
            value={search} onChange={e=>setSearch(e.target.value)}
            placeholder="Mã HS, tên công dân, thủ tục..."
            style={{ width:'100%', padding:'8px 10px 8px 32px', border:'1.5px solid #dce3ef', borderRadius:'8px', fontFamily:'inherit', fontSize:'12.5px', outline:'none', background:'#f8fafc' }}
          />
        </div>
        <select value={filterTT} onChange={e=>setFilterTT(e.target.value)} style={S_SELECT}>
          {TRANG_THAI_OPTIONS.map(o=><option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <select value={filterLV} onChange={e=>setFilterLV(e.target.value)} style={S_SELECT}>
          {LINH_VUC_OPTIONS.map(lv=><option key={lv} value={lv}>{lv||'Tất cả lĩnh vực'}</option>)}
        </select>
        <span style={{ fontSize:'11px', fontWeight:600, color:'#0b8a7e', background:'#f0fdfa', border:'1px solid #99f6e4', padding:'5px 10px', borderRadius:'7px', cursor:'pointer' }}>🔗 Đồng bộ LGSP</span>
        <select value={pageSize} onChange={e=>{setPageSize(Number(e.target.value));setPage(1)}} style={{padding:'6px 24px 6px 10px',border:'1.5px solid #dce3ef',borderRadius:'8px',fontFamily:'inherit',fontSize:'12.5px',background:'#fff',outline:'none',color:'#0c1e3c',appearance:'none',backgroundImage:"url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath fill='%235c738a' d='M0 0l5 6 5-6z'/%3E%3C/svg%3E\")",backgroundRepeat:'no-repeat',backgroundPosition:'right 8px center'}}>
          {[10,20,50].map(n=><option key={n} value={n}>{n} hàng/trang</option>)}
        </select>
        <span style={{ fontSize:'11.5px', color:'#5c738a', marginLeft:'4px' }}>
          Hiển thị <strong style={{ color:'#0c1e3c' }}>{Math.min(page*pageSize, filtered.length)}</strong>/{filtered.length} hồ sơ
        </span>
        <button style={{ marginLeft:'auto', padding:'8px 16px', borderRadius:'8px', fontWeight:700, fontSize:'12.5px', color:'#fff', background:'#1652f0', border:'none', cursor:'pointer', fontFamily:'inherit' }}>
          + Hồ sơ mới
        </button>
      </div>

      {loading && <div style={{textAlign:'center',padding:'20px',color:'#5c738a',fontSize:'13px'}}>⏳ Đang tải dữ liệu...</div>}
      {/* Table */}
      <div style={{ background:'#fff', borderRadius:'10px', border:'1px solid #dce3ef', overflow:'hidden', boxShadow:'0 1px 3px rgba(12,30,60,.06)' }}>
        {/* Header */}
        <div style={{ display:'grid', gridTemplateColumns:GRID, gap:'0', background:'#f8fafc', borderBottom:'1px solid #dce3ef', padding:'9px 14px', fontSize:'10.5px', fontWeight:800, color:'#5c738a', textTransform:'uppercase', letterSpacing:'.06em' }}>
          <div onClick={()=>toggleSort('id')} style={{cursor:'pointer',userSelect:'none'}}>Mã hồ sơ<SortIcon col="id"/></div>
          <div onClick={()=>toggleSort('ten')} style={{cursor:'pointer',userSelect:'none'}}>Thủ tục / Công dân<SortIcon col="ten"/></div>
          <div onClick={()=>toggleSort('lv')} style={{cursor:'pointer',userSelect:'none'}}>Lĩnh vực<SortIcon col="lv"/></div>
          <div onClick={()=>toggleSort('tt')} style={{cursor:'pointer',userSelect:'none'}}>Trạng thái<SortIcon col="tt"/></div>
          <div onClick={()=>toggleSort('han')} style={{cursor:'pointer',userSelect:'none'}}>Hạn xử lý<SortIcon col="han"/></div>
          <div onClick={()=>toggleSort('ngay_nop')} style={{cursor:'pointer',userSelect:'none'}}>Ngày nộp<SortIcon col="ngay_nop"/></div>
          <div onClick={()=>toggleSort('cb')} style={{cursor:'pointer',userSelect:'none'}}>Cán bộ<SortIcon col="cb"/></div>
          <div>Thao tác</div>
        </div>

        {/* Rows */}
        {filtered.length === 0 ? (
          <div style={{ padding:'40px', textAlign:'center', color:'#8fa3bb', fontSize:'13px' }}>
            <div style={{ fontSize:'32px', marginBottom:'8px' }}>📭</div>
            Không tìm thấy hồ sơ phù hợp
          </div>
        ) : paginated.map((hs, i) => (
          <div key={hs.id}
            onClick={() => setSelectedHS(hs)}
            style={{ display:'grid', gridTemplateColumns:GRID, padding:'10px 14px', borderBottom: i<paginated.length-1 ? '1px solid #f1f5f9' : 'none', cursor:'pointer', transition:'background .12s', alignItems:'center' }}
            onMouseEnter={e=>(e.currentTarget.style.background='#f8fafc')}
            onMouseLeave={e=>(e.currentTarget.style.background='#fff')}
          >
            <div>
              <div style={{ fontFamily:'JetBrains Mono,monospace', fontSize:'11.5px', fontWeight:700, color:'#1652f0' }}>{hs.id}</div>
              {hs.pr==='KHAN_CAP' && <span style={{ fontSize:'9px', fontWeight:800, color:'#d93025', background:'#fef2f2', padding:'1px 5px', borderRadius:'4px' }}>⚡ KHẨN</span>}
            </div>
            <div>
              <div style={{ display:'flex', alignItems:'center', gap:'6px' }}>
                <span style={{ fontSize:'12.5px', fontWeight:700, color:'#0c1e3c' }}>{hs.ten}</span>

              </div>
              <div style={{ fontSize:'11.5px', color:'#5c738a', marginTop:'2px', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' }}>{hs.cd}</div>
            </div>
            {/* Lĩnh vực */}
            <div style={{ display:'flex', alignItems:'center' }}>
              {hs.lv && <span style={{ fontSize:'11px', fontWeight:700, padding:'3px 9px', borderRadius:'20px', background:(LV_COLOR[hs.lv]||'#5c738a')+'18', color:LV_COLOR[hs.lv]||'#5c738a', border:`1px solid ${(LV_COLOR[hs.lv]||'#5c738a')}35`, whiteSpace:'nowrap' }}>{hs.lv}</span>}
            </div>
            <div><StatusBadge tt={hs.tt} /></div>
            <div><Deadline han={hs.han} tt={hs.tt} /></div>
            <div style={{ fontSize:'11.5px', color:'#334155' }}>
              {hs.ngay_nop ? new Date(hs.ngay_nop).toLocaleDateString('vi-VN',{day:'2-digit',month:'2-digit',year:'2-digit'}) : '—'}
            </div>
            <div>
              <div style={{ fontSize:'12px', color:'#2d4060', fontWeight:500 }}>{hs.cb}</div>
              <div style={{ fontSize:'10.5px', color:'#94a3b8', marginTop:'2px' }}>
                {hs.nguon==='TRUC_TIEP'?'🏢 Trực tiếp':hs.nguon==='TRUC_TUYEN'?'🌐 Trực tuyến':hs.nguon==='BUU_CHINH'?'📮 Bưu chính':hs.nguon||''}
              </div>
            </div>
            <div>
              <button
                onClick={e=>{ e.stopPropagation(); setSelectedHS(hs) }}
                style={{ padding:'5px 12px', borderRadius:'7px', fontWeight:700, fontSize:'11.5px', color:'#1652f0', background:'#eff6ff', border:'1px solid #bfdbfe', cursor:'pointer', fontFamily:'inherit' }}
              >
                Chi tiết
              </button>
            </div>
          </div>
        ))}
      </div>


      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginTop:'12px', padding:'10px 14px', background:'#fff', borderRadius:'10px', border:'1px solid #dce3ef' }}>
          <div style={{ fontSize:'12px', color:'#5c738a' }}>
            Trang <strong style={{color:'#0c1e3c'}}>{page}</strong> / {totalPages}
            {' · '}{filtered.length} hồ sơ · {pageSize} hàng/trang
          </div>
          <div style={{ display:'flex', gap:'4px' }}>
            <button
              onClick={()=>setPage(1)} disabled={page===1}
              style={{ padding:'5px 10px', borderRadius:'6px', border:'1px solid #dce3ef', background: page===1?'#f8fafc':'#fff', color: page===1?'#c4d0de':'#2d4060', cursor: page===1?'not-allowed':'pointer', fontSize:'12px', fontWeight:600, fontFamily:'inherit' }}>
              «
            </button>
            <button
              onClick={()=>setPage(p=>Math.max(1,p-1))} disabled={page===1}
              style={{ padding:'5px 12px', borderRadius:'6px', border:'1px solid #dce3ef', background: page===1?'#f8fafc':'#fff', color: page===1?'#c4d0de':'#2d4060', cursor: page===1?'not-allowed':'pointer', fontSize:'12px', fontWeight:600, fontFamily:'inherit' }}>
              ‹ Trước
            </button>
            {Array.from({length: Math.min(5, totalPages)}, (_, i) => {
              const start = Math.max(1, Math.min(page-2, totalPages-4))
              const p = start + i
              if (p > totalPages) return null
              return (
                <button key={p} onClick={()=>setPage(p)}
                  style={{ padding:'5px 10px', borderRadius:'6px', border:'1px solid', borderColor: p===page?'#1652f0':'#dce3ef', background: p===page?'#1652f0':'#fff', color: p===page?'#fff':'#2d4060', cursor:'pointer', fontSize:'12px', fontWeight: p===page?800:500, fontFamily:'inherit', minWidth:'32px' }}>
                  {p}
                </button>
              )
            })}
            <button
              onClick={()=>setPage(p=>Math.min(totalPages,p+1))} disabled={page===totalPages}
              style={{ padding:'5px 12px', borderRadius:'6px', border:'1px solid #dce3ef', background: page===totalPages?'#f8fafc':'#fff', color: page===totalPages?'#c4d0de':'#2d4060', cursor: page===totalPages?'not-allowed':'pointer', fontSize:'12px', fontWeight:600, fontFamily:'inherit' }}>
              Sau ›
            </button>
            <button
              onClick={()=>setPage(totalPages)} disabled={page===totalPages}
              style={{ padding:'5px 10px', borderRadius:'6px', border:'1px solid #dce3ef', background: page===totalPages?'#f8fafc':'#fff', color: page===totalPages?'#c4d0de':'#2d4060', cursor: page===totalPages?'not-allowed':'pointer', fontSize:'12px', fontWeight:600, fontFamily:'inherit' }}>
              »
            </button>
          </div>
        </div>
      )}

      {/* Modal */}
      {selectedHS && <HoSoModal hs={selectedHS} onClose={()=>setSelectedHS(null)} />}
    </div>
  )
}
