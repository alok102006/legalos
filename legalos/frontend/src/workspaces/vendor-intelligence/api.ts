import apiClient from '@/api/client';
import { VendorCheck } from '@/api/types';

export const verifyVendor = async (gstin: string): Promise<VendorCheck> => {
  const response = await apiClient.post<VendorCheck>('/api/v1/vendors/verify', { gstin });
  return response.data;
};

export const listVendorAudits = async (): Promise<VendorCheck[]> => {
  const response = await apiClient.get<VendorCheck[]>('/api/v1/vendors/');
  return response.data;
};
