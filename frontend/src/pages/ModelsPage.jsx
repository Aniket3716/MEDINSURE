import { useEffect, useState } from 'react'
import { getModelMetrics, retrainModels } from '../services/predictionService'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar, Cell } from 'recharts'
import { BarChart3, RefreshCw, Award, Cpu, Database, Clock, Loader2, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import { format } from 'date-fns'

const MODEL_COLORS = { 'Xgboost': '#2563EB', 'Random Forest': '#7C3AED', 'Decision Tree': '#059669' }

function MetricCard({ label, value, unit = '', description }) {
  return (
    <div className="bg-slate-50 rounded-xl p-4">
      <p className="text-xs text-slate-500 font-medium">{label}</p>
      <p className="text-2xl font-display font-semibold text-slate-800 mt-1">
        {value}<span className="text-sm text-slate-400 font-normal ml-1">{unit}</span>
      </p>
      {description && <p className="text-xs text-slate-400 mt-1">{description}</p>}
    </div>
  )
}

export default function ModelsPage() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [retraining, setRetraining] = useState(false)

  const fetchMetrics = async () => {
    setLoading(true)
    try {
      const res = await getModelMetrics()
      setData(res.data)
    } catch {
      toast.error('Failed to load model metrics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchMetrics() }, [])

  const handleRetrain = async () => {
    if (!confirm('Retrain all models? This may take a minute.')) return
    setRetraining(true)
    try {
      await retrainModels()
      toast.success('Models retrained successfully!')
      await fetchMetrics()
    } catch {
      toast.error('Retraining failed')
    } finally {
      setRetraining(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    )
  }

  const models = data?.models || []
  const chartData = data?.comparison_chart_data || []

  const rmseData = models.map(m => ({ model: m.model_name, RMSE: Math.round(m.rmse), fill: MODEL_COLORS[m.model_name] || '#94A3B8' }))
  const r2Data = models.map(m => ({ model: m.model_name, R2: parseFloat((m.r2_score * 100).toFixed(1)), fill: MODEL_COLORS[m.model_name] || '#94A3B8' }))
  const maeData = models.map(m => ({ model: m.model_name, MAE: Math.round(m.mae), fill: MODEL_COLORS[m.model_name] || '#94A3B8' }))

  const bestModel = models.find(m => m.model_name === data?.best_model) || models[0]

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between animate-in">
        <div>
          <h1 className="font-display text-3xl font-medium text-slate-900">ML Model Performance</h1>
          <p className="text-slate-500 mt-1">Compare XGBoost, Random Forest, and Decision Tree</p>
        </div>
        <button
          onClick={handleRetrain}
          disabled={retraining}
          className="btn-secondary flex items-center gap-2"
        >
          {retraining ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
          {retraining ? 'Retraining...' : 'Retrain Models'}
        </button>
      </div>

      {/* Best Model Banner */}
      {bestModel && (
        <div className="card p-5 border-l-4 border-l-primary-600 animate-in">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
              <Award className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-medium">Best Performing Model</p>
              <p className="font-semibold text-slate-800">{bestModel.model_name}</p>
            </div>
            <div className="flex gap-6 ml-auto text-sm">
              <div>
                <p className="text-xs text-slate-400">R² Score</p>
                <p className="font-semibold text-emerald-600">{(bestModel.r2_score * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">RMSE</p>
                <p className="font-semibold text-slate-700">${bestModel.rmse.toLocaleString('en-US', { maximumFractionDigits: 0 })}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">MAE</p>
                <p className="font-semibold text-slate-700">${bestModel.mae.toLocaleString('en-US', { maximumFractionDigits: 0 })}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400">Training Samples</p>
                <p className="font-semibold text-slate-700">{bestModel.training_samples.toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Individual Model Cards */}
      <div className="grid grid-cols-3 gap-4 animate-in">
        {models.map((model) => {
          const isBest = model.model_name === data?.best_model
          return (
            <div key={model.model_name} className={clsx('card p-5 space-y-4', isBest && 'ring-2 ring-primary-500')}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ background: MODEL_COLORS[model.model_name] || '#94A3B8' }}
                  />
                  <p className="font-semibold text-slate-800 text-sm">{model.model_name}</p>
                </div>
                {isBest && (
                  <span className="flex items-center gap-1 text-xs text-primary-600 font-medium bg-primary-50 px-2 py-0.5 rounded-full">
                    <CheckCircle className="w-3 h-3" /> Best
                  </span>
                )}
              </div>
              <div className="grid grid-cols-2 gap-2">
                <MetricCard label="R² Score" value={(model.r2_score * 100).toFixed(1)} unit="%" description="Higher is better" />
                <MetricCard label="MAE" value={`$${(model.mae / 1000).toFixed(1)}k`} description="Mean abs. error" />
                <MetricCard label="RMSE" value={`$${(model.rmse / 1000).toFixed(1)}k`} description="Root mean sq. error" />
                <MetricCard label="MSE" value={`$${(model.mse / 1000000).toFixed(1)}M`} description="Mean sq. error" />
              </div>
              <div className="text-xs text-slate-400 flex items-center gap-1">
                <Database className="w-3 h-3" />
                {model.training_samples.toLocaleString()} training samples
              </div>
            </div>
          )
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6 animate-in">
        <div className="card p-5">
          <h3 className="font-semibold text-slate-800 mb-4">R² Score Comparison</h3>
          <p className="text-xs text-slate-400 mb-3">Higher R² = better fit (max 100%)</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={r2Data} barSize={50}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="model" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tickFormatter={v => `${v}%`} tick={{ fontSize: 10 }} />
              <Tooltip formatter={v => [`${v}%`, 'R² Score']} />
              <Bar dataKey="R2" radius={[6, 6, 0, 0]}>
                {r2Data.map((e, i) => <Cell key={i} fill={e.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card p-5">
          <h3 className="font-semibold text-slate-800 mb-4">RMSE Comparison</h3>
          <p className="text-xs text-slate-400 mb-3">Lower RMSE = more accurate predictions</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={rmseData} barSize={50}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
              <XAxis dataKey="model" tick={{ fontSize: 11 }} />
              <YAxis tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{ fontSize: 10 }} />
              <Tooltip formatter={v => [`$${v.toLocaleString()}`, 'RMSE']} />
              <Bar dataKey="RMSE" radius={[6, 6, 0, 0]}>
                {rmseData.map((e, i) => <Cell key={i} fill={e.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Feature Importance */}
      {models[0]?.feature_names?.length > 0 && (
        <div className="card p-5 animate-in">
          <h3 className="font-semibold text-slate-800 mb-1">Model Features</h3>
          <p className="text-xs text-slate-400 mb-4">Input variables used for prediction</p>
          <div className="flex flex-wrap gap-2">
            {models[0].feature_names.map(f => (
              <span key={f} className="px-3 py-1.5 bg-primary-50 text-primary-700 text-xs font-medium rounded-lg border border-primary-100">
                {f.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Training Info */}
      {models[0]?.last_trained && (
        <div className="flex items-center gap-2 text-xs text-slate-400 animate-in">
          <Clock className="w-3.5 h-3.5" />
          Last trained: {format(new Date(models[0].last_trained), 'MMMM d, yyyy at h:mm a')}
        </div>
      )}
    </div>
  )
}
