"use client"
import { useState, useEffect } from 'react'
import { hoSoApi, agentsApi } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import toast from 'react-hot-toast'

// ── Static data (sẽ load từ API /thu-tuc sau) ─────────────────
const THU_TUC_LIST = [
  { id:'00000000-0000-0000-0000-000000000001', ma:'HT-001', ten:'Đăng ký kết hôn', linh_vuc:'Hộ tịch', thoi_han:5,
    giay_to:['CCCD/Hộ chiếu 2 người','Giấy xác nhận tình trạng hôn nhân','Tờ khai đăng ký kết hôn (Mẫu TP/HT-2015)','Ảnh 3×4 (2 tấm/người)','Sổ hộ khẩu (nếu có)'] },
  { id:'c2f3c071-8f94-4cf0-9b9b-a3077607512b', ma:'HT-002', ten:'Đăng ký khai sinh', linh_vuc:'Hộ tịch', thoi_han:3,
    giay_to:['CCCD bố/mẹ','Giấy chứng sinh','Giấy đăng ký kết hôn của cha mẹ','Sổ hộ khẩu'] },
  { id:'7170cf4d-07b7-47f5-ae91-6cea54df067a', ma:'CT-001', ten:'Đăng ký thường trú', linh_vuc:'Cư trú', thoi_han:7,
    giay_to:['CCCD','Giấy tờ nhà','Phiếu báo thay đổi hộ khẩu (HK01)','Sổ hộ khẩu (nếu có)'] },
]

const LINH_VUC = ['Tất cả','Hộ tịch','Cư trú','Đất đai']
const NGUON = [
  {value:'truc_tiep', label:'Trực tiếp'},
  {value:'buu_chinh', label:'Bưu chính'},
  {value:'lgsp',      label:'LGSP (Online)'},
]

// ── Styles ────────────────────────────────────────────────────
const s = {
  wrap:     { display:'grid', gridTemplateColumns:'1fr 300px', gap:'14px' } as React.CSSProperties,
  card:     { background:'#fff', borderRadius:'12px', border:'1px solid #dce3ef', padding:'18px 20px', boxShadow:'0 1px 4px rgba(12,30,60,.07)' } as React.CSSProperties,
  label:    { display:'block', fontSize:'11px', fontWeight:700, color:'#2d4060', marginBottom:'5px' } as React.CSSProperties,
  input:    { width:'100%', padding:'9px 11px', border:'1.5px solid #dce3ef', borderRadius:'8px', fontFamily:'inherit', fontSize:'13px', background:'#fff', outline:'none', color:'#0c1e3c' } as React.CSSProperties,
  grid2:    { display:'grid', gridTemplateColumns:'1fr 1fr', gap:'10px', marginBottom:'10px' } as React.CSSProperties,
  grid3:    { display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:'10px', marginBottom:'10px' } as React.CSSProperties,
  ff:       { marginBottom:'10px' } as React.CSSProperties,
  btnPri:   { padding:'9px 18px', borderRadius:'8px', fontWeight:700, fontSize:'12.5px', color:'#fff', background:'#1652f0', border:'none', cursor:'pointer', fontFamily:'inherit', display:'inline-flex', alignItems:'center', gap:'5px' } as React.CSSProperties,
  btnSec:   { padding:'9px 18px', borderRadius:'8px', fontWeight:700, fontSize:'12.5px', color:'#2d4060', background:'#fff', border:'1.5px solid #dce3ef', cursor:'pointer', fontFamily:'inherit', display:'inline-flex', alignItems:'center', gap:'5px' } as React.CSSProperties,
  sectionT: { fontSize:'12.5px', fontWeight:800, marginBottom:'13px', display:'flex', alignItems:'center', gap:'6px' } as React.CSSProperties,
}

type ThuTuc = typeof THU_TUC_LIST[0]

// ── Step indicator ─────────────────────────────────────────────
function StepBar({ step }: { step: number }) {
  const steps = ['① Thông tin hồ sơ', '② Xác nhận & Lưu']
  return (
    <div style={{ display:'flex', gap:'2px', background:'#f1f5f9', border:'1px solid #dce3ef', borderRadius:'10px', padding:'3px', marginBottom:'16px' }}>
      {steps.map((s, i) => (
        <button key={i} style={{ flex:1, padding:'7px 14px', borderRadius:'8px', border:'none', fontFamily:'inherit', fontSize:'12px', fontWeight: step===i ? 800 : 600, color: step===i ? '#0c1e3c' : '#5c738a', background: step===i ? '#fff' : 'transparent', cursor:'pointer', boxShadow: step===i ? '0 1px 4px rgba(0,0,0,.08)' : 'none' }}>
          {s}
        </button>
      ))}
    </div>
  )
}

// ── AI Checker banner ──────────────────────────────────────────
function AIChecker({ thuTuc, loading }: { thuTuc: ThuTuc | null; loading: boolean }) {
  if (loading) return (
    <div style={{ display:'flex', alignItems:'center', gap:'9px', padding:'9px 13px', borderRadius:'8px', marginBottom:'14px', background:'#f0fdf4', border:'1px solid #86efac', fontSize:'12.5px', color:'#166534' }}>
      <span style={{ animation:'spin 1s linear infinite', display:'inline-block' }}>⏳</span>
      <span>AI đang phân tích thủ tục...</span>
    </div>
  )
  if (!thuTuc) return null
  return (
    <div style={{ display:'flex', alignItems:'flex-start', gap:'9px', padding:'9px 13px', borderRadius:'8px', marginBottom:'14px', background:'#f0fdf4', border:'1px solid #86efac', fontSize:'12.5px', color:'#166534' }}>
      <span>🤖</span>
      <span>
        <strong>AI phát hiện:</strong> "{thuTuc.ten}" cần <strong>{thuTuc.giay_to.length} loại giấy tờ</strong>
        {' · '}Thời hạn: <strong>{thuTuc.thoi_han} ngày làm việc</strong>
        {' · '}Lĩnh vực: <strong>{thuTuc.linh_vuc}</strong>
      </span>
    </div>
  )
}

// ── Right panel ────────────────────────────────────────────────
function RightPanel({ thuTuc, ngayNop }: { thuTuc: ThuTuc | null; ngayNop: string }) {
  const hanGQ = thuTuc && ngayNop ? (() => {
    const d = new Date(ngayNop)
    d.setDate(d.getDate() + thuTuc.thoi_han)
    return d
  })() : null

  const conLai = hanGQ ? Math.ceil((hanGQ.getTime() - Date.now()) / 86400000) : null

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'12px' }}>
      {/* Giấy tờ cần nộp */}
      <div style={s.card}>
        <div style={s.sectionT}>
          <span style={{ width:'3px', height:'13px', background:'#1652f0', borderRadius:'2px', flexShrink:0 }}/>
          🤖 Giấy tờ cần nộp
        </div>
        {thuTuc ? (
          <div style={{ display:'flex', flexDirection:'column', gap:'5px' }}>
            {thuTuc.giay_to.map((gt, i) => (
              <div key={i} style={{ display:'flex', alignItems:'flex-start', gap:'7px', fontSize:'12px', padding:'5px 0', borderBottom: i<thuTuc.giay_to.length-1 ? '1px solid #f1f5f9' : 'none' }}>
                <span style={{ color:'#0f7b3c', fontWeight:800, flexShrink:0, marginTop:'1px' }}>✓</span>
                <span style={{ color:'#2d4060' }}>{gt}</span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ fontSize:'12px', color:'#8fa3bb', textAlign:'center', padding:'12px 0' }}>Chọn thủ tục để xem danh sách</div>
        )}
      </div>

      {/* Thời hạn xử lý */}
      <div style={s.card}>
        <div style={s.sectionT}>
          <span style={{ width:'3px', height:'13px', background:'#e07b12', borderRadius:'2px', flexShrink:0 }}/>
          📅 Thời hạn xử lý
        </div>
        <div style={{ display:'flex', flexDirection:'column', gap:'7px', fontSize:'12.5px' }}>
          <div style={{ display:'flex', justifyContent:'space-between' }}>
            <span style={{ color:'#5c738a' }}>Ngày nộp</span>
            <b>{ngayNop ? formatDate(ngayNop) : formatDate(new Date().toISOString())}</b>
          </div>
          <div style={{ display:'flex', justifyContent:'space-between' }}>
            <span style={{ color:'#5c738a' }}>Hạn giải quyết</span>
            <b style={{ color:'#e07b12' }}>{hanGQ ? formatDate(hanGQ.toISOString()) : '—'}</b>
          </div>
          <div style={{ display:'flex', justifyContent:'space-between' }}>
            <span style={{ color:'#5c738a' }}>Còn lại</span>
            <b style={{ color: conLai !== null ? (conLai <= 1 ? '#d93025' : conLai <= 3 ? '#e07b12' : '#0f7b3c') : '#8fa3bb' }}>
              {conLai !== null ? `${conLai} ngày làm việc` : '—'}
            </b>
          </div>
          {thuTuc && (
            <div style={{ marginTop:'4px', padding:'6px 10px', background:'#eff6ff', borderRadius:'7px', fontSize:'11px', color:'#1652f0', fontWeight:600 }}>
              📋 Thủ tục: {thuTuc.ma} · {thuTuc.linh_vuc}
            </div>
          )}
        </div>
      </div>

      {/* Nguồn tiếp nhận */}
      <div style={s.card}>
        <div style={s.sectionT}>
          <span style={{ width:'3px', height:'13px', background:'#0b8a7e', borderRadius:'2px', flexShrink:0 }}/>
          🔗 Nguồn tiếp nhận
        </div>
        <div style={{ fontSize:'11.5px', color:'#5c738a', lineHeight:1.7 }}>
          <div>• <strong style={{color:'#0c1e3c'}}>Trực tiếp</strong>: công dân đến quầy</div>
          <div>• <strong style={{color:'#0c1e3c'}}>Bưu chính</strong>: nhận qua bưu điện</div>
          <div>• <strong style={{color:'#0c1e3c'}}>LGSP</strong>: cổng dịch vụ công online</div>
        </div>
      </div>
    </div>
  )
}

// ── Confirm step ───────────────────────────────────────────────
function ConfirmStep({ form, thuTuc, onBack, onSubmit, loading }: {
  form: Record<string, string>; thuTuc: ThuTuc | null
  onBack: () => void; onSubmit: () => void; loading: boolean
}) {
  const rows = [
    ['Thủ tục', thuTuc?.ten || '—'],
    ['Lĩnh vực', thuTuc?.linh_vuc || '—'],
    ['Họ tên công dân', form.ho_ten],
    ['Số CCCD', form.cccd],
    ['Số điện thoại', form.sdt || '—'],
    ['Địa chỉ', form.dia_chi],
    ['Nguồn tiếp nhận', NGUON.find(n=>n.value===form.nguon)?.label || '—'],
    ['Ghi chú', form.ghi_chu || '—'],
  ]
  return (
    <div style={s.card}>
      <div style={{ display:'flex', alignItems:'center', gap:'8px', padding:'10px 14px', background:'#f0fdf4', borderRadius:'8px', marginBottom:'18px', border:'1px solid #86efac' }}>
        <span>✅</span>
        <span style={{ fontSize:'12.5px', color:'#166534', fontWeight:600 }}>Vui lòng kiểm tra thông tin trước khi lưu hồ sơ</span>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'10px 24px', marginBottom:'18px' }}>
        {rows.map(([label, val]) => (
          <div key={label}>
            <div style={{ fontSize:'10.5px', fontWeight:700, color:'#5c738a', textTransform:'uppercase', letterSpacing:'.05em', marginBottom:'2px' }}>{label}</div>
            <div style={{ fontSize:'13px', fontWeight:600, color:'#0c1e3c' }}>{val}</div>
          </div>
        ))}
      </div>
      {thuTuc && (
        <div style={{ marginBottom:'18px' }}>
          <div style={{ fontSize:'10.5px', fontWeight:700, color:'#5c738a', textTransform:'uppercase', letterSpacing:'.05em', marginBottom:'8px' }}>Giấy tờ cần nộp ({thuTuc.giay_to.length})</div>
          <div style={{ display:'flex', flexDirection:'column', gap:'4px' }}>
            {thuTuc.giay_to.map((gt, i) => (
              <div key={i} style={{ fontSize:'12px', color:'#2d4060', display:'flex', gap:'7px' }}>
                <span style={{ color:'#0f7b3c', fontWeight:800 }}>✓</span>{gt}
              </div>
            ))}
          </div>
        </div>
      )}
      <div style={{ display:'flex', gap:'8px' }}>
        <button onClick={onBack} style={s.btnSec}>← Quay lại</button>
        <button onClick={onSubmit} disabled={loading} style={{ ...s.btnPri, opacity: loading ? .6 : 1 }}>
          {loading ? '⏳ Đang lưu...' : '💾 Lưu hồ sơ'}
        </button>
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────
export default function TiepNhanPage() {
  const [step, setStep] = useState(0)
  const [aiLoading, setAiLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [selectedThuTuc, setSelectedThuTuc] = useState<ThuTuc>(THU_TUC_LIST[0])
  const [linhVucFilter, setLinhVucFilter] = useState('Tất cả')

  const [form, setForm] = useState({
    thu_tuc_id: THU_TUC_LIST[0].id,
    ho_ten: '', cccd: '', sdt: '', dia_chi: '', ghi_chu: '',
    nguon: 'truc_tiep',
    ngay_nop: new Date().toISOString().slice(0,10),
  })

  const thuTucFiltered = linhVucFilter === 'Tất cả'
    ? THU_TUC_LIST
    : THU_TUC_LIST.filter(t => t.linh_vuc === linhVucFilter)

  const set1 = (k: string, v: string) => setForm(f => ({...f, [k]: v}))

  const handleThuTucChange = (id: string) => {
    const tt = THU_TUC_LIST.find(t => t.id === id)
    if (!tt) return
    setAiLoading(true)
    set1('thu_tuc_id', id)
    setSelectedThuTuc(tt)
    setTimeout(() => setAiLoading(false), 800)
  }

  const handleNext = () => {
    if (!form.ho_ten.trim()) { toast.error('Vui lòng nhập họ tên công dân'); return }
    if (!form.cccd.trim())   { toast.error('Vui lòng nhập số CCCD'); return }
    if (!form.dia_chi.trim()){ toast.error('Vui lòng nhập địa chỉ thường trú'); return }
    setStep(1)
    window.scrollTo(0,0)
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      await hoSoApi.tiepNhan({
        thu_tuc_id:        selectedThuTuc.id,
        thu_tuc_ten:       selectedThuTuc.ten,
        linh_vuc:          selectedThuTuc.linh_vuc,
        thoi_han_ngay:     selectedThuTuc.thoi_han,
        cong_dan_ho_ten: form.ho_ten,
        cong_dan_cccd:   form.cccd,
        cong_dan_dia_chi:form.dia_chi,
        cong_dan_sdt:    form.sdt,
        cong_dan_email:    '',
        cong_dan_ngay_sinh:'',
        ghi_chu_noi_bo:    form.ghi_chu,
      })
      toast.success('✅ Lưu hồ sơ thành công!')
      // Reset form
      setForm({ thu_tuc_id:THU_TUC_LIST[0].id, ho_ten:'', cccd:'', sdt:'', dia_chi:'', ghi_chu:'', nguon:'truc_tiep', ngay_nop:new Date().toISOString().slice(0,10) })
      setSelectedThuTuc(THU_TUC_LIST[0])
      setStep(0)
    } catch (err: unknown) {
      const msg = (err as {response?:{data?:{detail?:string}}}).response?.data?.detail || 'Lỗi khi lưu hồ sơ'
      toast.error(msg)
    } finally {
      setSubmitting(false)
    }
  }

  const inp = (k: string) => ({
    value: form[k as keyof typeof form],
    onChange: (e: React.ChangeEvent<HTMLInputElement|HTMLSelectElement|HTMLTextAreaElement>) => set1(k, e.target.value),
    style: s.input,
  })

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom:'16px' }}>
        <h1 style={{ fontSize:'22px', fontWeight:800, color:'#0c1e3c', letterSpacing:'-.02em' }}>📥 Tiếp nhận hồ sơ</h1>
        <p style={{ fontSize:'12px', color:'#5c738a', marginTop:'4px' }}>Nhập thông tin công dân — AI tự động kiểm tra danh mục giấy tờ theo thủ tục đã chọn.</p>
      </div>

      <div style={s.wrap}>
        {/* Left: Form */}
        <div>
          <StepBar step={step} />

          {step === 0 ? (
            <div style={s.card}>
              {/* Thủ tục + Lĩnh vực */}
              <div style={s.grid2}>
                <div>
                  <label style={s.label}>Lĩnh vực</label>
                  <select value={linhVucFilter} onChange={e=>setLinhVucFilter(e.target.value)}
                    style={{...s.input, backgroundImage:"url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath fill='%235c738a' d='M0 0l5 6 5-6z'/%3E%3C/svg%3E\")", backgroundRepeat:'no-repeat', backgroundPosition:'right 11px center', paddingRight:'28px', appearance:'none' as React.CSSProperties['appearance']}}>
                    {LINH_VUC.map(lv => <option key={lv}>{lv}</option>)}
                  </select>
                </div>
                <div>
                  <label style={s.label}>Loại thủ tục <span style={{color:'#d93025'}}>*</span></label>
                  <select value={form.thu_tuc_id} onChange={e=>handleThuTucChange(e.target.value)}
                    style={{...s.input, backgroundImage:"url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath fill='%235c738a' d='M0 0l5 6 5-6z'/%3E%3C/svg%3E\")", backgroundRepeat:'no-repeat', backgroundPosition:'right 11px center', paddingRight:'28px', appearance:'none' as React.CSSProperties['appearance']}}>
                    {thuTucFiltered.map(tt => <option key={tt.id} value={tt.id}>{tt.ten}</option>)}
                  </select>
                </div>
              </div>

              {/* AI Checker */}
              <AIChecker thuTuc={selectedThuTuc} loading={aiLoading} />

              {/* Thông tin công dân */}
              <div style={{ fontSize:'11px', fontWeight:800, color:'#5c738a', textTransform:'uppercase', letterSpacing:'.08em', marginBottom:'10px', marginTop:'4px' }}>
                👤 Thông tin công dân
              </div>

              <div style={s.grid2}>
                <div>
                  <label style={s.label}>Họ và tên <span style={{color:'#d93025'}}>*</span></label>
                  <input {...inp('ho_ten')} placeholder="Nguyễn Thị Mai Lan" />
                </div>
                <div>
                  <label style={s.label}>Số CCCD <span style={{color:'#d93025'}}>*</span></label>
                  <input {...inp('cccd')} placeholder="079085012345" maxLength={12} />
                </div>
              </div>

              <div style={s.grid2}>
                <div>
                  <label style={s.label}>Số điện thoại</label>
                  <input {...inp('sdt')} placeholder="0901 234 567" />
                </div>
                <div>
                  <label style={s.label}>Nguồn tiếp nhận</label>
                  <select value={form.nguon} onChange={e=>set1('nguon',e.target.value)}
                    style={{...s.input, backgroundImage:"url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath fill='%235c738a' d='M0 0l5 6 5-6z'/%3E%3C/svg%3E\")", backgroundRepeat:'no-repeat', backgroundPosition:'right 11px center', paddingRight:'28px', appearance:'none' as React.CSSProperties['appearance']}}>
                    {NGUON.map(n => <option key={n.value} value={n.value}>{n.label}</option>)}
                  </select>
                </div>
              </div>

              <div style={s.ff}>
                <label style={s.label}>Địa chỉ thường trú <span style={{color:'#d93025'}}>*</span></label>
                <input {...inp('dia_chi')} placeholder="142/5 Trần Quý Khoách, P.Tân Định, Q.1" />
              </div>

              <div style={s.ff}>
                <label style={s.label}>Ghi chú</label>
                <textarea value={form.ghi_chu} onChange={e=>set1('ghi_chu',e.target.value)}
                  rows={2} placeholder="Thông tin bổ sung nếu có..."
                  style={{...s.input, resize:'vertical', lineHeight:1.5}} />
              </div>

              <div style={{ display:'flex', gap:'8px', marginTop:'4px' }}>
                <button onClick={handleNext} style={s.btnPri}>Tiếp theo →</button>
                <button onClick={()=>setForm({thu_tuc_id:THU_TUC_LIST[0].id,ho_ten:'',cccd:'',sdt:'',dia_chi:'',ghi_chu:'',nguon:'truc_tiep',ngay_nop:new Date().toISOString().slice(0,10)})} style={s.btnSec}>🗑 Xóa</button>
              </div>
            </div>
          ) : (
            <ConfirmStep form={form} thuTuc={selectedThuTuc} onBack={()=>setStep(0)} onSubmit={handleSubmit} loading={submitting} />
          )}
        </div>

        {/* Right panel */}
        <RightPanel thuTuc={selectedThuTuc} ngayNop={form.ngay_nop} />
      </div>
    </div>
  )
}

