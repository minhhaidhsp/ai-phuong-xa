export type Role = 'admin' | 'lanh_dao' | 'can_bo'
export interface User {
  id:string; ho_ten:string; ten_dang_nhap:string; email:string
  vai_tro:Role; phong_ban?:string; chuc_vu?:string; is_active:boolean
}
