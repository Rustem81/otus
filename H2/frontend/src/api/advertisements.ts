import { api } from "boot/axios";

export interface Advertisement {
  id: string;
  merchant_id: string;
  merchant_name: string;
  price: number;
  available_amount: number;
  min_amount: number;
  max_amount: number;
  currency: string;
  direction: string;
  payment_methods: string[];
  risk_score: number;
  risk_category: "low" | "medium" | "high";
  profitability: number;
  is_active: boolean;
  fetched_at: string;
}

export interface AdvertisementsResponse {
  items: Advertisement[];
  total: number;
  page: number;
  page_size: number;
}

export interface AdvertisementsFilters {
  payment_methods?: string[];
  min_rating?: number;
  min_trades?: number;
  min_amount?: number;
  max_amount?: number;
  page?: number;
  page_size?: number;
}

export async function getAdvertisements(
  filters?: AdvertisementsFilters,
): Promise<AdvertisementsResponse> {
  const params: Record<string, string | number> = {};

  if (filters?.payment_methods?.length) {
    params.payment_methods = filters.payment_methods.join(",");
  }
  if (filters?.min_rating) params.min_rating = filters.min_rating;
  if (filters?.min_trades) params.min_trades = filters.min_trades;
  if (filters?.min_amount) params.min_amount = filters.min_amount;
  if (filters?.max_amount) params.max_amount = filters.max_amount;
  if (filters?.page) params.page = filters.page;
  if (filters?.page_size) params.page_size = filters.page_size;

  const response = await api.get<AdvertisementsResponse>("/advertisements", {
    params,
  });
  return response.data;
}

export async function getAdvertisement(id: string): Promise<Advertisement> {
  const response = await api.get<Advertisement>(`/advertisements/${id}`);
  return response.data;
}
