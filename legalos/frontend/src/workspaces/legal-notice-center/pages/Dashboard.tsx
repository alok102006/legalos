import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  UploadCloud, 
  FileText, 
  AlertCircle, 
  Calendar, 
  ChevronRight, 
  Loader2,
  Plus,
  RefreshCw
} from 'lucide-react';
import { Card } from '@/design-system/components/Card';
import { Button } from '@/design-system/components/Button';
import { Badge } from '@/design-system/components/Badge';
import { Skeleton } from '@/design-system/components/Skeleton';
import { analyzeNoticeFile, analyzeNoticeText, listNotices } from '../api';
import { NoticeSummary } from '@/api/types';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [notices, setNotices] = useState<NoticeSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // File Upload State
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Paste Text State
  const [showPasteForm, setShowPasteForm] = useState(false);
  const [pasteTitle, setPasteTitle] = useState('');
  const [pasteText, setPasteText] = useState('');
  const [pasteSubmitting, setPasteSubmitting] = useState(false);

  const fetchNoticesList = async (showSkeleton = false) => {
    if (showSkeleton) setLoading(true);
    try {
      const data = await listNotices();
      setNotices(data);
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || 'Failed to retrieve notices.');
    } finally {
      if (showSkeleton) setLoading(false);
    }
  };

  useEffect(() => {
    fetchNoticesList(true);
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    const file = files[0];
    setUploading(true);
    setError(null);

    try {
      const result = await analyzeNoticeFile(file);
      // Immediately navigate to detail page where it shows loading/parsed state
      navigate(`/notices/${result.id}`);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || 'Failed to upload and analyze notice.');
      setUploading(false);
    }
  };

  const handlePasteSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pasteTitle.trim() || !pasteText.trim()) return;

    setPasteSubmitting(true);
    setError(null);

    try {
      const result = await analyzeNoticeText(pasteTitle.trim(), pasteText.trim());
      navigate(`/notices/${result.id}`);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || 'Failed to submit pasted notice.');
      setPasteSubmitting(false);
    }
  };

  // Badge rendering helpers
  const getUrgencyBadge = (urgency: string | null) => {
    const cleanUrgency = (urgency || 'low').toLowerCase();
    const map = {
      critical: { text: 'Critical', variant: 'danger' },
      high: { text: 'High', variant: 'warning' },
      medium: { text: 'Medium', variant: 'secondary' },
      low: { text: 'Low', variant: 'neutral' },
    } as any;
    const config = map[cleanUrgency] || { text: 'Pending', variant: 'neutral' };
    return <Badge variant={config.variant}>{config.text}</Badge>;
  };

  const getNoticeTypeBadge = (noticeType: string | null) => {
    const cleanType = (noticeType || 'other').toLowerCase();
    const map = {
      demand: { text: 'Demand Notice', variant: 'primary' },
      show_cause: { text: 'Show Cause', variant: 'secondary' },
      summons: { text: 'Court Summons', variant: 'danger' },
      other: { text: 'Other Notice', variant: 'neutral' },
    } as any;
    const config = map[cleanType] || { text: 'Analyzing', variant: 'neutral' };
    return <Badge variant={config.variant}>{config.text}</Badge>;
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Upload/Creation Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          {!showPasteForm ? (
            <Card title="Ingest New Legal Notice" subtitle="Upload notice document to run semantic extraction, categorization, and generate reply letter.">
              <div 
                className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center hover:border-blue-500 hover:bg-slate-50/50 transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  className="hidden"
                  accept=".pdf,.docx,.txt,.md"
                  onChange={handleFileUpload}
                  disabled={uploading}
                />
                
                {uploading ? (
                  <div className="flex flex-col items-center py-4">
                    <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-3" />
                    <span className="text-sm font-semibold text-slate-700">Uploading and parsing notice...</span>
                    <span className="text-xs text-slate-400 mt-1">Extracting text and chunking paragraphs</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center py-4">
                    <UploadCloud className="w-12 h-12 text-slate-400 mb-3" />
                    <span className="text-sm font-semibold text-slate-700">
                      Click to upload legal notice file
                    </span>
                    <span className="text-xs text-slate-400 mt-1">
                      Supports PDF, DOCX, TXT or MD (Max 10MB)
                    </span>
                  </div>
                )}
              </div>
              
              <div className="mt-4 flex items-center justify-between">
                <span className="text-xs text-slate-400 font-medium">Or choose manual input:</span>
                <Button variant="outline" size="sm" onClick={() => setShowPasteForm(true)}>
                  <Plus className="w-4 h-4 mr-1.5" /> Paste Notice Text
                </Button>
              </div>
            </Card>
          ) : (
            <Card title="Paste Notice Text" subtitle="Submit notice content manually for AI classification.">
              <form onSubmit={handlePasteSubmit} className="space-y-4">
                <div>
                  <label htmlFor="title" className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                    Notice Subject / Title
                  </label>
                  <input
                    type="text"
                    id="title"
                    className="block w-full border border-slate-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g., Injunction Demand Letter"
                    value={pasteTitle}
                    onChange={(e) => setPasteTitle(e.target.value)}
                    required
                    disabled={pasteSubmitting}
                  />
                </div>

                <div>
                  <label htmlFor="text" className="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                    Notice Content
                  </label>
                  <textarea
                    id="text"
                    rows={8}
                    className="block w-full border border-slate-300 rounded px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Paste the full legal notice text here..."
                    value={pasteText}
                    onChange={(e) => setPasteText(e.target.value)}
                    required
                    disabled={pasteSubmitting}
                  />
                </div>

                <div className="flex gap-3 justify-end">
                  <Button type="button" variant="outline" onClick={() => setShowPasteForm(false)} disabled={pasteSubmitting}>
                    Cancel
                  </Button>
                  <Button type="submit" isLoading={pasteSubmitting}>
                    Analyze Notice
                  </Button>
                </div>
              </form>
            </Card>
          )}
        </div>

        <div>
          <Card title="Legal Notice Guidelines" className="h-full">
            <div className="text-xs text-slate-600 space-y-4 leading-relaxed font-medium">
              <p>
                <strong>Indian Legal Notice Protocol:</strong> A legal notice is a formal notification served by an advocate representing their client, stating grievances and legal intention.
              </p>
              <p>
                <strong>System Features:</strong>
              </p>
              <ul className="list-disc pl-4 space-y-2">
                <li>Automatic classification of notice types (Summons, Demand, Show Cause).</li>
                <li>Priority sorting using urgency criteria (Critical notices highlighted).</li>
                <li>RAG-enhanced automated drafting of contextually fitting reply letters.</li>
              </ul>
            </div>
          </Card>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-red-800">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          <span className="text-sm font-medium">{error}</span>
        </div>
      )}

      {/* Notices Audits List */}
      <Card 
        title="Notice History & Registry"
        footer={
          <Button variant="outline" size="sm" onClick={() => fetchNoticesList(false)}>
            <RefreshCw className="w-4 h-4 mr-1.5" /> Refresh List
          </Button>
        }
      >
        {loading ? (
          <div className="space-y-3">
            <Skeleton className="h-12" />
            <Skeleton className="h-12" />
            <Skeleton className="h-12" />
          </div>
        ) : notices.length === 0 ? (
          <div className="text-center py-12 text-slate-500 flex flex-col items-center justify-center">
            <FileText className="w-12 h-12 text-slate-300 mb-2" />
            <p className="text-sm font-medium">No legal notices ingested yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            {/* Desktop Table View */}
            <table className="hidden md:table min-w-full divide-y divide-slate-200">
              <thead>
                <tr className="bg-slate-50">
                  <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Notice Name</th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Urgency</th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Ingested At</th>
                  <th className="px-6 py-3 text-right text-xs font-bold text-slate-500 uppercase tracking-wider">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {notices.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-slate-800 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-slate-400" />
                      {item.original_filename}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getNoticeTypeBadge(item.notice_type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getUrgencyBadge(item.urgency)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 font-medium">
                      <span className="inline-flex items-center gap-1.5">
                        <Calendar className="w-4 h-4 text-slate-400" />
                        {new Date(item.created_at).toLocaleString()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <Button variant="ghost" size="sm" onClick={() => navigate(`/notices/${item.id}`)}>
                        View Notice <ChevronRight className="w-4 h-4 ml-1" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Mobile Stacked Card View */}
            <div className="md:hidden space-y-4">
              {notices.map((item) => (
                <div key={item.id} className="p-4 border border-slate-200 rounded-lg space-y-3 bg-white shadow-sm">
                  <div className="flex justify-between items-start">
                    <h4 className="text-sm font-bold text-slate-800 flex items-center gap-1.5">
                      <FileText className="w-4 h-4 text-slate-400" />
                      {item.original_filename}
                    </h4>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {getNoticeTypeBadge(item.notice_type)}
                    {getUrgencyBadge(item.urgency)}
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-slate-100 text-xs text-slate-500 font-medium">
                    <span>{new Date(item.created_at).toLocaleDateString()}</span>
                    <Button variant="ghost" size="sm" onClick={() => navigate(`/notices/${item.id}`)} className="p-0">
                      Open notice
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};
export default Dashboard;
