export type TrangThaiNhiemVu = 'CHUA_BAT_DAU'|'DANG_THUC_HIEN'|'HOAN_THANH'|'QUA_HAN'|'DA_HUY'
export type UuTien = 'THAP'|'TRUNG_BINH'|'CAO'|'KHAN_CAP'
export type XepLoaiKPI = 'XUAT_SAC'|'TOT'|'KHA'|'TRUNG_BINH'|'YEU'
export interface NhiemVu {
  id:string; tieu_de:string; mo_ta?:string
  nguoi_giao_id:string; nguoi_nhan_id:string
  nguoi_giao?:{ho_ten:string}; nguoi_nhan?:{ho_ten:string}
  ngay_giao:string; han_hoan_thanh:string; ngay_hoan_thanh_thuc_te?:string
  trang_thai:TrangThaiNhiemVu; muc_do_uu_tien:UuTien; ho_so_id?:string; ket_qua?:string; created_at:string
}
export interface KPIData {
  user_id:string; ho_ten:string; vai_tro:string; ky_danh_gia:string
  tong_ho_so:number; ho_so_dung_han:number; ty_le_dung_han:number
  tong_nhiem_vu:number; nhiem_vu_dung_han:number
  diem_ho_so:number; diem_nhiem_vu:number; diem_tong:number; xep_loai:XepLoaiKPI
}
