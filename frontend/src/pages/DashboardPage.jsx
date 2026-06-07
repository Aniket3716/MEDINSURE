import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Calculator, TrendingUp, BarChart3, History, ArrowRight, Activity, Shield, AlertTriangle, CheckCircle } from 'lucide-react'
import { getPredictionStats, getPredictionHistory } from '../services/predictionService'
import useAuthStore from '../store/authStore'
import { format } from 'date-fns'
import clsx from 'clsx'

const RISK_CONFIG = {
  low: { label: 'Low Risk', icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-50' },
  medium: { label: 'Medium Risk', icon: Activity, color: 'text-amber-600', bg: 'bg-amber-50' },
  high: { label: 'High Risk', icon: AlertTriangle, color: 'text-orange-600', bg: 'bg-orange-50' },
  very_high: { label: 'Very High Risk', icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-50' },
}

function StatCard({ icon: Icon, label, value, sub, color = 'text-primary-800' }) {
  return (
    <div className="card p-6 animate-in">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-500 font-medium">{label}</p>
          <p className={clsx('text-3xl font-display font-semibold mt-1', color)}>{value}</p>
          {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
        </div>
        <div className="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center">
          <Icon className="w-5 h-5 text-slate-500" />
        </div>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState(null)
  const [recentPredictions, setRecentPredictions] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, histRes] = await Promise.all([
          getPredictionStats(),
          getPredictionHistory(1, 5),
        ])
        setStats(statsRes.data)
        setRecentPredictions(histRes.data.items || [])
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const greeting = () => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 17) return 'Good afternoon'
    return 'Good evening'
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="animate-in">
        <h1 className="font-display text-3xl font-medium text-slate-900">
          {greeting()}, {user?.full_name?.split(' ')[0] || user?.username} 👋
        </h1>
        <p className="text-slate-500 mt-1">Here's your insurance prediction overview.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={BarChart3}
          label="Total Predictions"
          value={loading ? '—' : stats?.total_predictions ?? 0}
          sub="All time"
        />
        <StatCard
          icon={TrendingUp}
          label="Avg. Annual Premium"
          value={loading ? '—' : `$${(stats?.avg_premium ?? 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`}
          sub="Across all predictions"
          color="text-blue-700"
        />
        <StatCard
          icon={Shield}
          label="Lowest Premium"
          value={loading ? '—' : `$${(stats?.min_premium ?? 0).toLocaleString('en-US', { maximumFractionDigits: 0 })}`}
          sub="Best case"
          color="text-emerald-700"
        />
        <StatCard
          icon={Activity}
          label="Avg. Risk Score"
          value={loading ? '—' : `${(stats?.avg_risk_score ?? 0).toFixed(1)}/100`}
          sub="Your risk profile"
          color="text-amber-700"
        />
      </div>

      {/* Quick Action */}
      <div className="card p-6 bg-gradient-to-r from-primary-800 to-primary-700 text-white animate-in">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/60 text-sm font-medium">Ready to predict?</p>
            <h2 className="font-display text-2xl font-medium mt-0.5">
              Get your insurance premium estimate
            </h2>
            <p className="text-white/60 text-sm mt-1">
              Our AI uses 3 ML models for the most accurate predictions.
            </p>
          </div>
          <Link
            to="/predict"
            className="flex items-center gap-2 bg-white text-primary-800 font-semibold
                       px-5 py-3 rounded-xl hover:bg-white/90 transition-all flex-shrink-0"
          >
            <Calculator className="w-4 h-4" />
            Predict Now
          </Link>
        </div>
      </div>

      {/* Recent Predictions */}
      <div className="animate-in">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display text-xl font-medium text-slate-900">Recent Predictions</h2>
          <Link to="/history" className="text-sm text-primary-700 hover:text-primary-800 flex items-center gap-1">
            View all <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loading ? (
          <div className="card p-12 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-primary-300 border-t-primary-700 rounded-full animate-spin" />
          </div>
        ) : recentPredictions.length === 0 ? (
          <div className="card p-12 text-center">
            <Calculator className="w-10 h-10 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500 font-medium">No predictions yet</p>
            <p className="text-slate-400 text-sm mt-1">Make your first prediction to see results here.</p>
            <Link to="/predict" className="btn-primary inline-flex mt-4">
              Make a Prediction
            </Link>
          </div>
        ) : (
          <div className="card divide-y divide-slate-100">
            {recentPredictions.map((pred) => {
              const risk = RISK_CONFIG[pred.risk_category] || RISK_CONFIG.medium
              const RiskIcon = risk.icon
              return (
                <Link
                  key={pred.id}
                  to={`/history/${pred.id}`}
                  className="flex items-center gap-4 p-4 hover:bg-slate-50 transition-colors"
                >
                  <div className={clsx('w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0', risk.bg)}>
                    <RiskIcon className={clsx('w-4.5 h-4.5', risk.color)} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900">
                      Age {pred.age} · BMI {pred.bmi.toFixed(1)} · {pred.smoker === 'yes' ? 'Smoker' : 'Non-smoker'}
                    </p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {format(new Date(pred.created_at), 'MMM d, yyyy • h:mm a')}
                    </p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-sm font-semibold text-slate-900">
                      ${pred.best_prediction.toLocaleString('en-US', { maximumFractionDigits: 0 })}/yr
                    </p>
                    <span className={clsx('text-xs font-medium px-2 py-0.5 rounded-full border', `risk-${pred.risk_category}`)}>
                      {risk.label}
                    </span>
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
