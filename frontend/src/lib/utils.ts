export function cn(...classes: (string|undefined|false|null)[]): string {
  return classes.filter(Boolean).join(' ')
}
export function formatDate(date:string|Date, fmt='dd/MM/yyyy'): string {
  if (!date) return '—'
  const d = typeof date === 'string' ? new Date(date) : date
  const dd = String(d.getDate()).padStart(2,'0')
  const mm = String(d.getMonth()+1).padStart(2,'0')
  const yyyy = d.getFullYear()
  return fmt.replace('dd',dd).replace('MM',mm).replace('yyyy',String(yyyy))
}
export function daysLeft(deadline:string): number {
  return Math.floor((new Date(deadline).getTime() - Date.now()) / 86400000)
}
export function daysLeftLabel(deadline:string): {label:string;color:string} {
  const d = daysLeft(deadline)
  if (d < 0)  return { label:`Qua han ${Math.abs(d)} ngay`, color:'#d93025' }
  if (d === 0) return { label:'Hom nay', color:'#e07b12' }
  if (d <= 2)  return { label:`Con ${d} ngay`, color:'#e07b12' }
  return { label:`Con ${d} ngay`, color:'#0f7b3c' }
}
export function getInitials(name:string): string {
  return name.split(' ').map((w:string)=>w[0]).slice(-2).join('').toUpperCase()
}
export function downloadBlob(blob:Blob, filename:string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href=url; a.download=filename; a.click()
  URL.revokeObjectURL(url)
}
