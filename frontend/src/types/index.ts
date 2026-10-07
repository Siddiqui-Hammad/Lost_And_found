export type UserRole = 'STUDENT' | 'ADMIN';

export interface User {
  user_id: string;
  name: string;
  email: string;
  role: UserRole;
  student_id?: string;
  department?: string;
  semester?: string;
  phone?: string;
}

export type ItemStatus = 'LOST' | 'FOUND' | 'MATCHED' | 'CLAIM_PENDING' | 'VERIFIED' | 'RETURNED' | 'REJECTED' | 'RESOLVED';

export interface LostItem {
  item_id: string;
  user_id: string;
  user_name: string;
  user_email: string;
  student_id?: string;
  item_name: string;
  category: string;
  brand?: string;
  color: string;
  description: string;
  location: string;
  lost_at: string;
  image_url?: string;
  status: ItemStatus;
  created_at: string;
}

export interface FoundItem {
  item_id: string;
  rfid_id?: string;
  box_id?: string;
  item_name: string;
  category: string;
  brand?: string;
  color: string;
  description: string;
  location: string;
  found_at: string;
  image_url?: string;
  source: 'MANUAL' | 'IOT';
  reported_by_name?: string;
  status: ItemStatus;
  created_at: string;
}

export interface MatchBreakdown {
  text_score: number;
  category_score: number;
  color_score: number;
  brand_score: number;
  location_score: number;
  time_score: number;
  image_score?: number | null;
  final_score: number;
  match_level: 'HIGH PROBABILITY' | 'POSSIBLE MATCH' | 'LOW PROBABILITY';
}

export interface MatchRecord {
  match_id: string;
  lost_item_id: string;
  found_item_id: string;
  text_score: number;
  category_score: number;
  color_score: number;
  brand_score: number;
  location_score: number;
  time_score: number;
  image_score?: number | null;
  final_match_score: number;
  match_level: string;
  lost_item: LostItem;
  found_item: FoundItem;
  created_at: string;
}

export interface Claim {
  claim_id: string;
  user_id: string;
  student_name: string;
  student_email: string;
  student_id?: string;
  lost_item_id: string;
  found_item_id: string;
  item_name: string;
  answers: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  admin_notes?: string;
  created_at: string;
  reviewed_at?: string;
}

export interface IoTBox {
  box_id: string;
  name: string;
  location: string;
  status: 'ONLINE' | 'OFFLINE' | 'MAINTENANCE';
  last_seen: string;
  items_registered: number;
}

export interface Notification {
  notification_id: string;
  user_id: string;
  user_email: string;
  title: string;
  message: string;
  match_id?: string;
  match_score?: number;
  link?: string;
  is_read: boolean;
  created_at: string;
}
