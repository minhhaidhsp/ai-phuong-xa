export type TrangThaiHoSo = 'CHO_TIEP_NHAN'|'DANG_XU_LY'|'YEU_CAU_BO_SUNG'|'CHO_PHE_DUYET'|'TU_CHOI'|'HOAN_THANH'
export type NguonTiepNhan = 'truc_tiep'|'buu_chinh'|'lgsp'
export interface ThuTuc { id:string; ten_thu_tuc:string; ma_thu_tuc:string; linh_vuc:string; thoi_han_ngay:number; phi?:number }
export interface HoSo {
  id:string; ma_ho_so:string; thu_tuc_id:string; thu_tuc?:ThuTuc; trang_thai:TrangThaiHoSo
  nguon_tiep_nhan:NguonTiepNhan; can_bo_xu_ly_id?:string
  cong_dan_ho_ten:string; cong_dan_cccd:string; cong_dan_dia_chi:string; cong_dan_sdt?:string
  ngay_tiep_nhan:string; han_giai_quyet:string; ngay_hoan_thanh?:string; ghi_chu?:string
  created_at:string; updated_at:string
}
export const TRANG_THAI_LABEL:Record<TrangThaiHoSo,string> = {
  CHO_TIEP_NHAN:'Cho tiep nhan', DANG_XU_LY:'Dang xu ly',
  YEU_CAU_BO_SUNG:'Yeu cau bo sung', CHO_PHE_DUYET:'Cho phe duyet',
  TU_CHOI:'Tu choi', HOAN_THANH:'Hoan thanh'
}
export const TRANG_THAI_COLOR:Record<TrangThaiHoSo,string> = {
  CHO_TIEP_NHAN:'#1652f0', DANG_XU_LY:'#e07b12', YEU_CAU_BO_SUNG:'#d97706',
  CHO_PHE_DUYET:'#6d28d9', TU_CHOI:'#d93025', HOAN_THANH:'#0f7b3c'
}
