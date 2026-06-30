import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Building2, 
  Calendar, 
  Sparkles, 
  ShieldAlert,
  Loader2,
  FileText,
  AlertCircle
} from 'lucide-react';
import { getContract, generateSuggestion } from '../api';
import { ContractDetail as ContractDetailType, Clause } from '@/api/types';
import Button from '@/design-system/components/Button';
import Card from '@/design-system/components/Card';
import RiskBadge from '@/design-system/components/RiskBadge';
import Skeleton from '@/design-system/components/Skeleton';
import Badge from '@/design-system/components/Badge';

export const ContractDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [contract, setContract] = useState<ContractDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Selected Clause details
  const [selectedClause, setSelectedClause] = useState<Clause | null>(null);
  const [generatingSuggest, setGeneratingSuggest] = useState(false);

  // Filters
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [searchText, setSearchText] = useState('');

  const fetchContractDetails = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await getContract(id);
      setContract(data);
      // Auto-select first high-risk clause if available
      const highRisk = data.clauses.find(c => c.risk_score >= 70);
      if (highRisk) {
        setSelectedClause(highRisk);
      } else if (data.clauses.length > 0) {
        setSelectedClause(data.clauses[0]);
      }
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || 'Failed to retrieve contract analysis.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContractDetails();
  }, [id]);

  const handleGenerateSuggestion = async () => {
    if (!contract || !selectedClause) return;
    setGeneratingSuggest(true);
    try {
      const suggestion = await generateSuggestion(contract.id, selectedClause.id);
      
      // Update local state dynamically
      const updatedClauses = contract.clauses.map(c => {
        if (c.id === selectedClause.id) {
          const updated = {
            ...c,
            suggestions: [suggestion, ...c.suggestions]
          };
          // Keep inspector select updated
          setSelectedClause(updated);
          return updated;
        }
        return c;
      });

      setContract({
        ...contract,
        clauses: updatedClauses
      });
    } catch (err) {
      console.error(err);
    } finally {
      setGeneratingSuggest(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Skeleton variant="line" count={2} className="w-1/3" />
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Skeleton variant="table" count={5} />
          </div>
          <div className="lg:col-span-1">
            <Skeleton variant="card" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !contract) {
    return (
      <Card className="text-center py-16">
        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h4 className="text-lg font-bold text-slate-800 mb-2">Error Loading Audit</h4>
        <p className="text-sm text-slate-500 mb-6">{error || 'Agreement file not found.'}</p>
        <Button onClick={() => navigate('/')} variant="outline">
          <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
        </Button>
      </Card>
    );
  }

  // Filter logic
  const filteredClauses = contract.clauses.filter(c => {
    const textMatch = c.raw_text.toLowerCase().includes(searchText.toLowerCase()) || 
                      (c.summary?.toLowerCase().includes(searchText.toLowerCase()) ?? false);
    const filterMatch = riskFilter === 'all' || 
                        (riskFilter === 'risk' && c.risk_type !== 'none') || 
                        c.risk_type === riskFilter;
    return textMatch && filterMatch;
  });

  return (
    <div className="space-y-6 pb-20">
      {/* Header breadcrumb */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <button 
          onClick={() => navigate('/')}
          className="inline-flex items-center text-xs font-semibold text-slate-500 hover:text-slate-800 uppercase tracking-wider transition-colors outline-none"
        >
          <ArrowLeft className="w-4 h-4 mr-1.5" /> Back to Dashboard
        </button>
        <div className="flex gap-2">
          {contract.status === 'failed' ? (
            <Badge variant="danger">Audit Failed</Badge>
          ) : (
            <Badge variant="success">Audit Complete</Badge>
          )}
        </div>
      </div>

      {/* Title block */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-slate-400">
            <FileText className="w-5 h-5 text-blue-500" />
            <span className="text-xs font-semibold tracking-wider uppercase">Document Profile</span>
          </div>
          <h2 className="text-xl md:text-2xl font-bold text-slate-800">{contract.title}</h2>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Building2 className="w-3.5 h-3.5" />
              Counterparty: <strong>{contract.counterparty_name}</strong>
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              Audited: <strong>{new Date(contract.created_at).toLocaleDateString()}</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Main Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left column: Clause List */}
        <div className="lg:col-span-2 space-y-4">
          <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm flex flex-col sm:flex-row gap-4 items-center justify-between">
            {/* Filter tags */}
            <div className="flex flex-wrap gap-1.5 w-full sm:w-auto">
              {[
                { label: 'All Clauses', val: 'all' },
                { label: 'Risk Flags', val: 'risk' },
                { label: 'Penalty', val: 'penalty' },
                { label: 'Indemnity', val: 'indemnity' },
                { label: 'Termination', val: 'termination' },
                { label: 'Lock-in', val: 'lock_in' },
              ].map(f => (
                <button
                  key={f.val}
                  onClick={() => setRiskFilter(f.val)}
                  className={`
                    px-3 py-1 rounded text-xs font-semibold border transition-colors outline-none
                    ${riskFilter === f.val 
                      ? 'bg-blue-600 border-blue-600 text-white shadow-sm' 
                      : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'}
                  `}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {/* Local search */}
            <input
              type="text"
              placeholder="Search clause text..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              className="px-3 py-1.5 w-full sm:w-60 text-xs rounded border border-slate-200 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </div>

          {/* List display */}
          <div className="space-y-3">
            {filteredClauses.length === 0 ? (
              <Card className="text-center py-12">
                <FileText className="w-12 h-12 text-slate-300 mx-auto mb-2" />
                <p className="text-sm text-slate-500 font-medium">No matching clauses found with active filters.</p>
              </Card>
            ) : (
              filteredClauses.map((clause) => {
                const isSelected = selectedClause?.id === clause.id;
                return (
                  <div
                    key={clause.id}
                    onClick={() => setSelectedClause(clause)}
                    className={`
                      p-4 rounded-lg border transition-all cursor-pointer flex flex-col gap-3
                      ${isSelected 
                        ? 'bg-blue-50/50 border-blue-400 shadow-sm ring-1 ring-blue-400' 
                        : 'bg-white border-slate-200 hover:border-slate-300'}
                    `}
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                        Clause #{clause.clause_index + 1}
                      </span>
                      <div className="flex gap-2">
                        {clause.risk_type && clause.risk_type !== 'none' && (
                          <Badge variant="secondary" className="uppercase text-[9px]">{clause.risk_type}</Badge>
                        )}
                        <RiskBadge score={clause.risk_score} riskType={clause.risk_type} />
                      </div>
                    </div>

                    <p className="text-slate-800 text-sm font-medium line-clamp-3 leading-relaxed">
                      {clause.raw_text}
                    </p>

                    {clause.summary && (
                      <p className="text-xs text-slate-500 border-l-2 border-slate-200 pl-2 italic">
                        Summary: {clause.summary}
                      </p>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right column: Inspector Panel */}
        <div className="lg:col-span-1">
          {selectedClause ? (
            <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm sticky top-6 space-y-6 flex flex-col h-[calc(100vh-140px)] max-h-[800px] overflow-y-auto">
              
              {/* Heading */}
              <div className="border-b border-slate-100 pb-4 space-y-2 flex-shrink-0">
                <div className="flex justify-between items-center">
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    Clause Inspector
                  </span>
                  <RiskBadge score={selectedClause.risk_score} riskType={selectedClause.risk_type} />
                </div>
                <h3 className="text-base font-bold text-slate-800">
                  Clause #{selectedClause.clause_index + 1} Analysis
                </h3>
              </div>

              {/* Raw segment */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Source Content</h4>
                <div className="bg-slate-50 p-4 rounded text-xs font-medium text-slate-700 leading-relaxed border border-slate-100 max-h-40 overflow-y-auto">
                  {selectedClause.raw_text}
                </div>
              </div>

              {/* AI summary */}
              {selectedClause.summary && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">AI Executive Summary</h4>
                  <p className="text-sm text-slate-600 leading-relaxed font-medium">
                    {selectedClause.summary}
                  </p>
                </div>
              )}

              {/* Suggestions Panel */}
              <div className="space-y-4 pt-4 border-t border-slate-100 flex-1 flex flex-col min-h-0">
                <div className="flex justify-between items-center flex-shrink-0">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5 text-blue-500" />
                    Negotiation Recommendation
                  </h4>
                  {selectedClause.suggestions.length > 0 && (
                    <Badge variant="success">Suggested</Badge>
                  )}
                </div>

                <div className="flex-1 overflow-y-auto pr-1">
                  {selectedClause.suggestions.length > 0 ? (
                    <div className="space-y-3">
                      {selectedClause.suggestions.map((s) => (
                        <div key={s.id} className="bg-blue-50/30 border border-blue-100 rounded-lg p-4 text-xs font-medium text-slate-700 leading-relaxed space-y-2">
                          <p className="whitespace-pre-wrap">{s.suggestion_text}</p>
                          <span className="text-[9px] text-slate-400 block pt-1 border-t border-slate-100">
                            Generated on {new Date(s.created_at).toLocaleString()}
                          </span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-6 border-2 border-dashed border-slate-200 rounded-lg flex flex-col items-center justify-center p-4">
                      <Sparkles className="w-8 h-8 text-slate-300 mb-2" />
                      <p className="text-xs text-slate-400 font-medium mb-4">
                        Request specialized negotiation counter-terms incorporating local compliance guidance.
                      </p>
                      <Button
                        onClick={handleGenerateSuggestion}
                        isLoading={generatingSuggest}
                        size="sm"
                        className="bg-blue-600 hover:bg-blue-700 text-white rounded shadow-sm text-xs"
                      >
                        {!generatingSuggest && <Sparkles className="w-3.5 h-3.5 mr-1" />}
                        Generate Suggestion
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-lg p-8 text-center flex flex-col items-center justify-center h-[200px]">
              <FileText className="w-8 h-8 text-slate-300 mb-2" />
              <p className="text-xs text-slate-400 font-medium">Select any clause to audit details and generate negotiations.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
export default ContractDetail;
