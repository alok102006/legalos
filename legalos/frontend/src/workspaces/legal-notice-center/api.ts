import apiClient from '@/api/client';
import { NoticeSummary, NoticeDetail, DraftReply } from '@/api/types';

export const analyzeNoticeFile = async (file: File): Promise<NoticeSummary> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await apiClient.post<NoticeSummary>('/api/v1/notices/analyze/file', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const analyzeNoticeText = async (title: string, text: string): Promise<NoticeSummary> => {
  const response = await apiClient.post<NoticeSummary>('/api/v1/notices/analyze/text', { title, text });
  return response.data;
};

export const listNotices = async (): Promise<NoticeSummary[]> => {
  const response = await apiClient.get<NoticeSummary[]>('/api/v1/notices/');
  return response.data;
};

export const getNotice = async (id: string): Promise<NoticeDetail> => {
  const response = await apiClient.get<NoticeDetail>(`/api/v1/notices/${id}`);
  return response.data;
};

export const regenerateReply = async (id: string): Promise<DraftReply> => {
  const response = await apiClient.post<DraftReply>(`/api/v1/notices/${id}/regenerate`);
  return response.data;
};
