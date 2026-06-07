import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getPrediction, downloadReport } from '../services/predictionService'
import { ArrowLeft, FileDown, Loader2, Shield, TrendingUp, BarChart3, CheckCircle } from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import clsx from 'clsx'

const RISK_CLASSES = {
  low: 'risk-low', medium: 'risk-medium', high: 'risk-high', very_high: 'risk-very_high'
}

export default function PredictionDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [pred, setPred] = useState(null)
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await getPrediction(id)
        setPred(res.data)
      } catch {
        toast.error('Prediction not found')
        navigate('/history')
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [id])

  const handleDownload = async () => {
    setDownloading(true)
    try {
      await downloadReport(id)
      toast.success('PDF downloaded!')
    } catch {
      toast.error('Download failed')
    } finally {
      setDownloading(false)
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center min-h-[400px]">
      <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
    </div>
  )

  if (!pred) return null

  const input = pred.input_data

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between animate-in">
        <div className="flex items-center gap-3">
          <Link to="/history" className="p-2 hover:bg-slate-100 rounded-xl transition-colors">
            <ArrowLeft className="w-5 h-5 text-slate-500" />
          </Link>
          <div>
            <h1 className="font-display text-2xl font-medium text-slate-900">Prediction #{pred.prediction_id}</h1>
            <p className="text-slate-400 text-sm">
              {format(new Date(pred.created_at), 'MMMM d, yyyy at h:mm a')} · {pred.processing_time_ms}ms
            </p>
          </div>
        </div>
        <button onClick={handleDownload} disabled={downloading} className="btn-primary flex items-center gap-2">
          {downloading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileDown className="w-4 h-4" />}
          Download PDF
        </button>
      </div>

      {/* Best Prediction */}
      <div className="card p-6 bg-gradient-to-r from-primary-800 to-primary-700 text-white animate-in">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white/60 text-sm">Predicted Annual Premium</p>
            <p className="font-display text-5xl font-semibold mt-1">
              ${pred.best_prediction.toLocaleString('en-US', { maximumFractionDigits: 0 })}
            </p>
            <p className="text-white/60 text-sm mt-1">Best model: {pred.best_model.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</p>
          </div>
          <div className="text-right">
            <p className="text-white/60 text-xs">Risk Score</p>
            <p className="font-display text-4xl font-semibold">{pred.risk_score.toFixed(0)}/100</p>
            <span className={clsx('text-xs font-semibold px-3 py-1 rounded-full capitalize mt-1 inline-block',
              `risk-${pred.risk_category}`)}>
              {pred.risk_category.replace('_', ' ')} risk
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Input Profile */}
        <div className="card p-5 animate-in">
          <h3 className="font-semibold text-slate-800 mb-4">Your Profile</h3>
          <dl className="space-y-2.5">
            {[
              ['Age', `${input.age} years`],
              ['Sex', input.sex.charAt(0).toUpperCase() + input.sex.slice(1)],
              ['BMI', input.bmi.toFixed(1)],
              ['Children', input.children],
              ['Smoker', input.smoker.charAt(0).toUpperCase() + input.smoker.slice(1)],
              ['Region', input.region.charAt(0).toUpperCase() + input.region.slice(1)],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <dt className="text-sm text-slate-500">{k}</dt>
                <dd className="text-sm font-medium text-slate-800">{v}</dd>
              </div>
            ))}
          </dl>
        </div>

        {/* Model Results */}
        <div className="card p-5 animate-in">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-primary-600" /> All Model Results
          </h3>
          <div className="space-y-3">
            {pred.model_predictions.map((mp) => {
              const isBest = mp.model_name === pred.best_model
              return (
                <div key={mp.model_name} className={clsx(
                  'flex items-center justify-between p-3 rounded-xl border',
                  isBest ? 'border-primary-200 bg-primary-50' : 'border-slate-100 bg-slate-50'
                )}>
                  <div className="flex items-center gap-2">
                    {isBest && <CheckCircle className="w-3.5 h-3.5 text-primary-600" />}
                    <span className="text-sm font-medium text-slate-700">
                      {mp.model_name.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                    </span>
                  </div>
                  <span className={clsx('text-sm font-semibold', isBest ? 'text-primary-800' : 'text-slate-600')}>
                    ${mp.predicted_premium.toLocaleString('en-US', { maximumFractionDigits: 0 })}/yr
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* SHAP */}
      {pred.shap_explanations?.length > 0 && (
        <div className="card p-5 animate-in">
          <h3 className="font-semibold text-slate-800 mb-1 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-primary-600" /> Feature Impact (SHAP)
          </h3>
          <p className="text-xs text-slate-400 mb-4">Positive values increase your premium; negative values decrease it.</p>
          <div className="space-y-3">
            {pred.shap_explanations.map((s) => {
              const maxVal = Math.max(...pred.shap_explanations.map(x => Math.abs(x.shap_value)))
              const pct = (Math.abs(s.shap_value) / maxVal) * 100
              return (
                <div key={s.feature_name}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="font-medium text-slate-600">
                      {s.feature_name.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                      <span className="text-slate-400 ml-1">(={s.feature_value})</span>
                    </span>
                    <span className={clsx('font-semibold', s.impact === 'positive' ? 'text-red-500' : 'text-emerald-600')}>
                      {s.impact === 'positive' ? '+' : '-'}${Math.abs(s.shap_value).toLocaleString('en-US', { maximumFractionDigits: 0 })}
                    </span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={clsx('h-full rounded-full', s.impact === 'positive' ? 'bg-red-400' : 'bg-emerald-400')}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Recommended Plans */}
      {pred.recommended_plans?.length > 0 && (
        <div className="card p-5 animate-in">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            <Shield className="w-4 h-4 text-primary-600" /> Recommended Plans
          </h3>
          <div className="space-y-3">
            {pred.recommended_plans.map((plan, i) => (
              <div key={plan.plan_id} className={clsx('rounded-xl border p-4', i === 0 ? 'border-primary-200 bg-primary-50' : 'border-slate-100')}>
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center gap-2">
                      {i === 0 && <CheckCircle className="w-4 h-4 text-primary-600" />}
                      <p className="font-semibold text-slate-800 text-sm">{plan.plan_name}</p>
                      <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full">{plan.plan_type}</span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">{plan.provider}</p>
                    <div className="flex gap-4 mt-2 text-xs text-slate-500">
                      <span>Deductible: <b>${plan.deductible.toLocaleString()}</b></span>
                      <span>Coverage: <b>${(plan.coverage_limit/1000000).toFixed(1)}M</b></span>
                      <span>Match: <b className="text-primary-600">{plan.match_score.toFixed(0)}%</b></span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-display text-xl font-semibold text-primary-800">
                      ${plan.monthly_premium.toLocaleString('en-US', { maximumFractionDigits: 0 })}/mo
                    </p>
                    <p className="text-xs text-slate-400">${plan.annual_premium.toLocaleString('en-US', { maximumFractionDigits: 0 })}/yr</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
