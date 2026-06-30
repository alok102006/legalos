import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  UploadCloud, 
  FileText, 
  Search, 
  Calendar, 
  Building2, 
  ChevronRight, 
  AlertCircle, 
  CheckCircle2, 
  Loader2 
} from 'lucide-react';
import { uploadContract, listContracts } from '../api';
import { ContractSummary } from '@/api/types';
import Button from '@/design-system/components/Button';
import Card from '@/design-system/components/Card';
import Skeleton from '@/design-system/components/Skeleton';
import Badge from '@/design-system/components/Badge';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [contracts, setContracts] = useState<ContractSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Upload State
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Search/Filter State
  const [searchQuery, setSearchQuery] = useState('');

  const fetchContractsList = async (showSkeleton = false) => {
    if (showSkeleton) setLoading(true);
    try {
      const data = await listContracts();
      setContracts(data);
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || 'Failed to retrieve contracts.');
    } finally {
      if (showSkeleton) setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchContractsList(true);
  }, []);

  // Polling for processing items
  useEffect(() => {
    const hasProcessing = contracts.some(c => c.status === 'processing');
    if (!hasProcessing) return;

    const interval = setInterval(() => {
      fetchContractsList(false);
    }, 3000);

    return () => clearInterval(interval);
  }, [contracts]);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    
    // File validation guards (mirrors backend constraints)
    const MAX_SIZE = 10 * 1024 * 1024; // 10MB
    if (file.size > MAX_SIZE) {
      setUploadError('File size exceeds the 10MB limit.');
      return;
    }

    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !['pdf', 'docx', 'txt', 'md'].includes(ext)) {
      setUploadError('Invalid format. Please upload PDF, DOCX, TXT, or MD.');
      return;
    }

    setUploading(true);
    setUploadError(null);
    try {
      const stub = await uploadContract(file);
      // Insert stub at front of list immediately
      setContracts(prev => [stub, ...prev]);
      
      // Reset input
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err: any) {
      console.error(err);
      setUploadError(err?.response?.data?.detail || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const selectFile = () => {
    fileInputRef.current?.click();
  };

  // Filtered list
  const filteredContracts = contracts.filter(c => {
    const titleMatch = c.title?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false;
    const partnerMatch = c.counterparty_name?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false;
    return titleMatch || partnerMatch;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'processing':
        return (
          <Badge variant="warning" className="flex gap-1 items-center">
            <Loader2 className="w-3 h-3 animate-spin" /> In Analysis
          </Badge>
        );
      case 'analyzed':
        return (
          <Badge variant="success" className="flex gap-1 items-center">
            <CheckCircle2 className="w-3 h-3" /> Analyzed
          </Badge>
        );
      case 'failed':
        return (
          <Badge variant="danger" className="flex gap-1 items-center">
            <AlertCircle className="w-3 h-3" /> Analysis Failed
          </Badge>
        );
      default:
        return <Badge variant="neutral">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Overview Banner */}
      <div className="bg-slate-900 text-white rounded-xl p-6 md:p-8 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-md">
        <div className="space-y-2">
          <h2 className="text-2xl font-bold tracking-tight">Contract Risk & Compliance Auditor</h2>
          <p className="text-slate-400 text-sm max-w-xl">
            Upload commercial vendor agreements, lease terms, or NDA drafts. Our localized intelligence platform parses clauses, scores compliance risks, and generates negotiation playbooks.
          </p>
        </div>
        <div className="flex-shrink-0">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            accept=".pdf,.docx,.txt,.md"
          />
          <Button 
            onClick={selectFile}
            isLoading={uploading}
            className="shadow-lg font-semibold bg-blue-500 hover:bg-blue-600 border-none px-6 py-3 rounded-lg text-white"
          >
            {!uploading && <UploadCloud className="w-5 h-5 mr-2" />}
            Upload Contract Document
          </Button>
          {uploadError && (
            <p className="mt-2 text-xs text-red-400 flex items-center gap-1 font-medium">
              <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
              {uploadError}
            </p>
          )}
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Left Column: Search & Quick Help */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm space-y-4">
            <h3 className="font-semibold text-slate-800 text-sm tracking-wide uppercase">Find Contract</h3>
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search name or vendor..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 pr-4 py-2 w-full text-sm rounded-lg border border-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all"
              />
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm space-y-4">
            <h3 className="font-semibold text-slate-800 text-sm tracking-wide uppercase">Audit Indicators</h3>
            <div className="space-y-3 text-xs text-slate-600">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <span>Maximum File Size</span>
                <span className="font-bold text-slate-800">10 MB</span>
              </div>
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <span>Supported Formats</span>
                <span className="font-bold text-slate-800">PDF, DOCX, TXT</span>
              </div>
              <div className="flex items-center justify-between">
                <span>RAG Dimensions</span>
                <span className="font-bold text-slate-800">384 (Cosine)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Contracts List */}
        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-800 text-lg">Documents Registry</h3>
            <span className="text-xs font-semibold text-slate-500">Showing {filteredContracts.length} items</span>
          </div>

          {loading ? (
            <div className="space-y-4">
              <Skeleton variant="table" count={3} />
            </div>
          ) : error ? (
            <Card className="text-center py-8">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h4 className="text-base font-bold text-slate-800 mb-2">Failed to load registry</h4>
              <p className="text-sm text-slate-500 mb-4">{error}</p>
              <Button onClick={() => fetchContractsList(true)} variant="outline">
                Try Again
              </Button>
            </Card>
          ) : filteredContracts.length === 0 ? (
            <Card className="text-center py-16 flex flex-col items-center">
              <FileText className="w-16 h-16 text-slate-300 mb-4" />
              <h4 className="text-lg font-bold text-slate-800 mb-2">No documents found</h4>
              <p className="text-sm text-slate-500 max-w-sm mb-6">
                {searchQuery 
                  ? "No results matching your keyword. Clear the search and try again." 
                  : "Get started by uploading your first commercial agreement or compliance document above."}
              </p>
              {!searchQuery && (
                <Button onClick={selectFile} variant="primary">
                  Upload Contract
                </Button>
              )}
            </Card>
          ) : (
            <div className="bg-white border border-slate-200 rounded-lg overflow-hidden shadow-sm divide-y divide-slate-100">
              {filteredContracts.map((contract) => (
                <div 
                  key={contract.id}
                  onClick={() => {
                    if (contract.status === 'analyzed') {
                      navigate(`/contracts/${contract.id}`);
                    }
                  }}
                  className={`
                    p-5 flex items-center justify-between transition-colors
                    ${contract.status === 'analyzed' ? 'hover:bg-slate-50 cursor-pointer' : 'opacity-85'}
                  `}
                >
                  <div className="flex gap-4 items-start min-w-0 flex-1 pr-4">
                    <div className="bg-blue-50 p-2.5 rounded-lg text-blue-600 flex-shrink-0">
                      <FileText className="w-6 h-6" />
                    </div>
                    <div className="min-w-0 space-y-1">
                      <h4 className="font-semibold text-slate-800 truncate text-sm md:text-base">
                        {contract.title || "Processing details..."}
                      </h4>
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Building2 className="w-3.5 h-3.5" />
                          {contract.counterparty_name || "Extracting..."}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5" />
                          {new Date(contract.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 flex-shrink-0">
                    <div className="text-right hidden sm:block">
                      {getStatusBadge(contract.status)}
                      {contract.status === 'analyzed' && (
                        <div className="mt-1 text-[10px] font-semibold text-slate-500">
                          {contract.risk_clause_count > 0 ? (
                            <span className="text-red-600">{contract.risk_clause_count} Risk Clause(s)</span>
                          ) : (
                            <span className="text-emerald-600">Clean Audit</span>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="sm:hidden">
                      {getStatusBadge(contract.status)}
                    </div>
                    {contract.status === 'analyzed' && (
                      <ChevronRight className="w-5 h-5 text-slate-400" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default Dashboard;
