import React, { useState, useEffect } from 'react';
import { 
  Search, 
  AlertOctagon, 
  CheckCircle, 
  Clock, 
  ShieldAlert, 
  History,
  Building,
  Calendar,
  AlertTriangle
} from 'lucide-react';
import { Card } from '@/design-system/components/Card';
import { Button } from '@/design-system/components/Button';
import { Badge } from '@/design-system/components/Badge';
import { Skeleton } from '@/design-system/components/Skeleton';
import { verifyVendor, listVendorAudits } from '../api';
import { VendorCheck } from '@/api/types';

export const Dashboard: React.FC = () => {
  const [gstin, setGstin] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VendorCheck | null>(null);
  const [history, setHistory] = useState<VendorCheck[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const fetchHistory = async () => {
    try {
      const data = await listVendorAudits();
      setHistory(data);
    } catch (err: any) {
      console.error('Failed to load audit history:', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (gstin.trim().length !== 15) {
      setError('GSTIN must be exactly 15 characters.');
      return;
    }
    setError(null);
    setLoading(true);
    setResult(null);

    try {
      const data = await verifyVendor(gstin.trim());
      setResult(data);
      await fetchHistory(); // Refresh history list
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.detail || 'Failed to verify GSTIN. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Helper for rendering trust score status
  const getTrustScoreColor = (check: VendorCheck) => {
    if (check.fraud_flagged) return 'text-red-600 bg-red-50 border-red-200';
    const score = check.trust_score || 0;
    if (score >= 70) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score >= 40) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Form Section */}
      <Card 
        title="GSTIN Compliance Audit" 
        subtitle="Verify Indian vendor GSTIN registration details and screen for compliance or fraud risk."
      >
        <form onSubmit={handleVerify} className="space-y-4 max-w-xl">
          <div>
            <label htmlFor="gstin" className="block text-sm font-semibold text-slate-700 mb-2">
              Enter 15-character GSTIN Number
            </label>
            <div className="relative rounded-md shadow-sm">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Search className="w-5 h-5" />
              </div>
              <input
                type="text"
                name="gstin"
                id="gstin"
                className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm uppercase tracking-wider placeholder:normal-case placeholder:tracking-normal"
                placeholder="e.g. 27AAAAA1111A1Z1"
                value={gstin}
                onChange={(e) => setGstin(e.target.value.toUpperCase())}
                maxLength={15}
                disabled={loading}
              />
            </div>
            {error && <p className="mt-2 text-sm text-red-600 font-medium">{error}</p>}
          </div>

          <div className="flex gap-3">
            <Button type="submit" isLoading={loading} disabled={gstin.length !== 15}>
              Verify Compliance
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setGstin('27AAAAA1111A1Z1');
                setError(null);
              }}
              disabled={loading}
            >
              Load Demo Fraud GSTIN
            </Button>
          </div>
        </form>
      </Card>

      {/* Results Display */}
      {loading && (
        <Card title="Performing Verification Audit...">
          <div className="space-y-4">
            <Skeleton className="h-6 w-1/4" />
            <Skeleton className="h-24 w-full" />
            <div className="grid grid-cols-2 gap-4">
              <Skeleton className="h-10" />
              <Skeleton className="h-10" />
            </div>
          </div>
        </Card>
      )}

      {result && (
        <Card className={`border-2 ${result.fraud_flagged ? 'border-red-300 bg-red-50/20' : 'border-slate-200'}`}>
          <div className="md:flex md:items-start md:justify-between gap-6">
            <div className="space-y-4 flex-1">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                  Verification Result for {result.gstin}
                </span>
                <h3 className="text-2xl font-bold text-slate-900 mt-1 flex items-center gap-2">
                  <Building className="w-6 h-6 text-slate-500" />
                  {result.company_name}
                </h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                <div className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg">
                  <Calendar className="w-5 h-5 text-slate-400" />
                  <div>
                    <span className="text-xs text-slate-400 block font-medium">Registration Date</span>
                    <span className="text-sm font-semibold text-slate-700">
                      {result.registration_date ? new Date(result.registration_date).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg">
                  {result.is_valid ? (
                    <CheckCircle className="w-5 h-5 text-emerald-500" />
                  ) : (
                    <AlertOctagon className="w-5 h-5 text-red-500" />
                  )}
                  <div>
                    <span className="text-xs text-slate-400 block font-medium">Status</span>
                    <span className={`text-sm font-bold ${result.is_valid ? 'text-emerald-700' : 'text-red-700'}`}>
                      {result.is_valid ? 'Active GSTIN' : 'Inactive / Suspended'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Warnings details */}
              {result.fraud_flagged && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex gap-3 text-red-800">
                  <ShieldAlert className="w-6 h-6 text-red-600 flex-shrink-0" />
                  <div>
                    <h4 className="font-bold text-sm">Critical Risk Flagged</h4>
                    <p className="text-xs mt-1 text-red-700 leading-relaxed font-medium">
                      {result.raw_mock_response?.reason || 'Compliance team blacklisted this vendor profile.'}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Trust Score circular-ish display */}
            <div className={`mt-6 md:mt-0 p-6 rounded-xl border flex flex-col items-center justify-center text-center w-full md:w-48 ${getTrustScoreColor(result)}`}>
              <span className="text-xs font-bold uppercase tracking-wide opacity-80">Trust Score</span>
              <span className="text-5xl font-extrabold my-2">{result.trust_score}</span>
              <span className="text-[10px] font-bold tracking-wider uppercase opacity-90 px-2 py-0.5 rounded-full bg-white border">
                {result.fraud_flagged ? 'Critical Risk' : (result.trust_score || 0) >= 70 ? 'Verified / Safe' : 'Caution'}
              </span>
            </div>
          </div>
        </Card>
      )}

      {/* History List */}
      <Card title="Compliance Audit Log" subtitle="Previous GSTIN verification audits.">
        {historyLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-10" />
            <Skeleton className="h-10" />
            <Skeleton className="h-10" />
          </div>
        ) : history.length === 0 ? (
          <div className="text-center py-8 text-slate-500 flex flex-col items-center justify-center">
            <History className="w-12 h-12 text-slate-300 mb-2" />
            <p className="text-sm">No verification history available.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            {/* Desktop Table View */}
            <table className="hidden md:table min-w-full divide-y divide-slate-200">
              <thead>
                <tr className="bg-slate-50">
                  <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">GSTIN</th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Company Name</th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-center text-xs font-bold text-slate-500 uppercase tracking-wider">Trust Score</th>
                  <th className="px-6 py-3 text-left text-xs font-bold text-slate-500 uppercase tracking-wider">Audit Date</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {history.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-blue-600 tracking-wider">
                      {item.gstin}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-slate-800">
                      {item.company_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {item.fraud_flagged ? (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-bold bg-red-100 text-red-800">
                          <ShieldAlert className="w-3.5 h-3.5 text-red-600" />
                          Fraud Flagged
                        </span>
                      ) : item.is_valid ? (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-bold bg-emerald-100 text-emerald-800">
                          <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                          Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-800">
                          Suspended
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-bold">
                      <span className={`px-2.5 py-1 rounded-full text-xs border ${
                        item.fraud_flagged ? 'text-red-700 bg-red-50 border-red-200' :
                        (item.trust_score || 0) >= 70 ? 'text-emerald-700 bg-emerald-50 border-emerald-200' :
                        (item.trust_score || 0) >= 40 ? 'text-amber-700 bg-amber-50 border-amber-200' :
                        'text-red-700 bg-red-50 border-red-200'
                      }`}>
                        {item.trust_score}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 font-medium">
                      <span className="inline-flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-slate-400" />
                        {new Date(item.checked_at).toLocaleString()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Mobile Stacked Card View */}
            <div className="md:hidden space-y-4">
              {history.map((item) => (
                <div key={item.id} className="p-4 border border-slate-200 rounded-lg space-y-2.5 bg-white shadow-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-bold text-blue-600 tracking-wider">{item.gstin}</span>
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-extrabold border ${
                      item.fraud_flagged ? 'text-red-700 bg-red-50 border-red-200' :
                      (item.trust_score || 0) >= 70 ? 'text-emerald-700 bg-emerald-50 border-emerald-200' :
                      (item.trust_score || 0) >= 40 ? 'text-amber-700 bg-amber-50 border-amber-200' :
                      'text-red-700 bg-red-50 border-red-200'
                    }`}>
                      Score: {item.trust_score}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-slate-800">{item.company_name}</h4>
                  <div className="flex justify-between items-center pt-2 border-t border-slate-100 text-xs text-slate-500 font-medium">
                    <span>
                      {item.fraud_flagged ? (
                        <span className="text-red-700 font-extrabold flex items-center gap-1">
                          <ShieldAlert className="w-3.5 h-3.5" /> Fraud Flagged
                        </span>
                      ) : (
                        <span className="text-emerald-700 font-extrabold flex items-center gap-1">
                          <CheckCircle className="w-3.5 h-3.5" /> Active
                        </span>
                      )}
                    </span>
                    <span>{new Date(item.checked_at).toLocaleDateString()}</span>
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
