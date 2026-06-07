import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  History, ChevronRight, ChevronLeft, Trash2, Eye,
  AlertTriangle, CheckCircle, Activity, Loader2, Search
} from 'lucide-react'
import { getPredictionHistory, deletePrediction } from '../services/predictionService'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import clsx from 'clsx'

const RISK_CONFIG = {
  low: { label: 'Low', color: 'risk-low', icon: CheckCircle },
  medium: { label: 'Medium', color: 'risk-medium', icon: Activity },
  high: { label: 'High', color: 'risk-high', icon: AlertTriangle },
  very_high: { label: 'Very High', color: 'risk-very_high', icon: AlertTriangle },
}

export default function HistoryPage() {
  const [predictions, setPredictions] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)
  const PAGE_SIZE = 10

  const fetchData = async (p = page) => {
    setLoading(true)
    try {
      const res = await getPredictionHistory(p, PAGE_SIZE)
      setPredictions(res.data.items || [])
      setTotal(res.data.total || 0)
    } catch {
      toast.error('Failed to load history')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchData() }, [page])

  const handleDelete = async (id) => {
    if (!confirm('Delete this prediction?')) return
    setDeleting(id)
    try {
      await deletePrediction(id)
      toast.success('Prediction deleted')
      fetchData()
    } catch {
      toast.error('Failed to delete')
    } finally {
      setDeleting(null)
    }
  }

  const totalPages = Math.ceil(total / PAGE_SIZE)

  return (
    <div className="space-y-6">
      <div className="animate-in">
        <h1 className="font-display text-3xl font-medium text-slate-900">Prediction History</h1>
        <p className="text-slate-500 mt-1">{total} total predictions</p>
      </div>

      <div className="card animate-in overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        ) : predictions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <History className="w-10 h-10 text-slate-300 mb-3" />
            <p className="text-slate-500 font-medium">No predictions yet</p>
            <Link to="/predict" className="btn-primary mt-4">Make your first prediction</Link>
          </div>
        ) : (
          <>
            {/* Table Header */}
            <div className="grid grid-cols-[1fr,80px,80px,100px,120px,100px,80px] gap-4 px-5 py-3 bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wide">
              <span>Profile</span>
              <span>Age</span>
              <span>BMI</span>
              <span>Smoker</span>
              <span>Premium</span>
              <span>Risk</span>
              <span>Actions</span>
            </div>

            {/* Rows */}
            {predictions.map((pred) => {
              const risk = RISK_CONFIG[pred.risk_category] || RISK_CONFIG.medium
              const RiskIcon = risk.icon
              return (
                <div
                  key={pred.id}
                  className="grid grid-cols-[1fr,80px,80px,100px,120px,100px,80px] gap-4 px-5 py-4 border-b border-slate-50 hover:bg-slate-50/70 transition-colors items-center"
                >
                  <div>
                    <p className="text-sm font-medium text-slate-800">
                      Prediction #{pred.id}
                    </p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {format(new Date(pred.created_at), 'MMM d, yyyy')}
                    </p>
                  </div>
                  <span className="text-sm text-slate-600">{pred.age}</span>
                  <span className="text-sm text-slate-600">{pred.bmi.toFixed(1)}</span>
                  <span className={clsx('text-xs font-medium', pred.smoker === 'yes' ? 'text-red-600' : 'text-emerald-600')}>
                    {pred.smoker === 'yes' ? 'Smoker' : 'Non-smoker'}
                  </span>
                  <span className="text-sm font-semibold text-slate-800">
                    ${pred.best_prediction.toLocaleString('en-US', { maximumFractionDigits: 0 })}/yr
                  </span>
                  <span className={clsx('text-xs font-medium px-2 py-1 rounded-full border inline-flex items-center gap-1 w-fit', `risk-${pred.risk_category}`)}>
                    <RiskIcon className="w-3 h-3" /> {risk.label}
                  </span>
                  <div className="flex items-center gap-1">
                    <Link
                      to={`/history/${pred.id}`}
                      className="p-1.5 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    >
                      <Eye className="w-4 h-4" />
                    </Link>
                    <button
                      onClick={() => handleDelete(pred.id)}
                      disabled={deleting === pred.id}
                      className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-40"
                    >
                      {deleting === pred.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>
              )
            })}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-5 py-4">
                <p className="text-sm text-slate-500">
                  Page {page} of {totalPages} · {total} records
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="btn-secondary !px-3 !py-2 disabled:opacity-40"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const p = Math.max(1, Math.min(page - 2, totalPages - 4)) + i
                    return (
                      <button
                        key={p}
                        onClick={() => setPage(p)}
                        className={clsx(
                          'w-9 h-9 rounded-xl text-sm font-medium transition-all',
                          p === page ? 'bg-primary-800 text-white' : 'text-slate-600 hover:bg-slate-100'
                        )}
                      >
                        {p}
                      </button>
                    )
                  })}
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="btn-secondary !px-3 !py-2 disabled:opacity-40"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
