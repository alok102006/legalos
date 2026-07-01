import apiClient from '@/api/client';
import { ContractSummary, ContractDetail, NegotiationSuggestion } from '@/api/types';

export const uploadContract = async (file: File): Promise<ContractSummary> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post<ContractSummary>('/api/v1/contracts/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const listContracts = async (): Promise<ContractSummary[]> => {
  const response = await apiClient.get<ContractSummary[]>('/api/v1/contracts/');
  return response.data;
};

export const getContract = async (id: string): Promise<ContractDetail> => {
  const response = await apiClient.get<ContractDetail>(`/api/v1/contracts/${id}`);
  return response.data;
};

export const generateSuggestion = async (
  contractId: string,
  clauseId: string
): Promise<NegotiationSuggestion> => {
  const response = await apiClient.post<NegotiationSuggestion>(
    `/api/v1/contracts/${contractId}/clauses/${clauseId}/suggest`
  );
  return response.data;
};

export const deleteContract = async (id: string): Promise<void> => {
  await apiClient.delete(`/api/v1/contracts/${id}`);
};

