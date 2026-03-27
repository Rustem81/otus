import { api } from "boot/axios";
import type { AxiosRequestConfig } from "axios";

export const customMutator = async <T>(
  config: AxiosRequestConfig,
): Promise<T> => {
  const response = await api.request<T>(config);
  return response.data;
};
