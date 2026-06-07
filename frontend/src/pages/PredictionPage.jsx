import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import {
  Calculator, Loader2, User, Activity, Users,
  MapPin, Cigarette, ChevronRight, BarChart3,
  TrendingUp, Shield, FileDown, CheckCircle
} from 'lucide-react'
import { predictPremium, downloadReport } from '../services/predictionService'
import toast from 'react-hot-toast'
import clsx from 'clsx'
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Cell
} from 'recharts'

const RISK_COLORS = {
  low: '#10B981', medium: '#F59E0B', high: '#F97316', very_high: '#EF4444'
}

const MODEL_COLORS = ['#2563EB', '#7C3AED', '#059669']

function FormSection({ title, icon: Icon, children }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 pb-2 border-b border-slate-100">
        <Icon className="w-4 h-4 text-primary-600" />
        <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">{title}</h3>
      </div>
      {children}
    </div>
  )
}

function SelectField({ label, name, options, register, error }) {
  return (
    <div>
      <label className="label">{label}</label>
      <select {...register(name, { required: `${label} is required` })} className="input-field">
        <option value="">Select...</option>
        {options.map(({ value, label }) => (
          <option key={value} value={value}>{label}</option>
        ))}
      </select>
      {error && <p className="text-red-500 text-xs mt-1">{error.message}</p>}
    </div>
  )
}

function PremiumCard({ label, value, isTop, color }) {
  return (
    <div className={clsx('rounded-xl border p-4 text-center', isTop ? 'border-primary-200 bg-primary-50' : 'border-slate-100 bg-slate-50')}>
      <p className="text-xs font-medium text-slate-500 mb-1">{label}</p>
      <p className={clsx('text-xl font-display font-semibold', isTop ? 'text-primary-800' : 'text-slate-700')}>
        ${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}
      </p>
      <p className="text-xs text-slate-400">per year</p>
      {isTop && <span className="text-xs text-primary-600 font-medium mt-1 inline-block">★ Best Model</span>}
    </div>
  )
}

export default function PredictionPage() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [downloadingPdf, setDownloadingPdf] = useState(false)
  const navigate = useNavigate()

  const { register, handleSubmit, formState: { errors } } = useForm()

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      const payload = {
        ...data,
        age: parseInt(data.age),
        bmi: parseFloat(data.bmi),
        children: parseInt(data.children),
      }
      const res = await predictPremium(payload)
      setResult(res.data)
      toast.success('Prediction complete!')
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Prediction failed')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadPdf = async () => {
    if (!result) return
    setDownloadingPdf(true)
    try {
      await downloadReport(result.prediction_id)
      toast.success('PDF downloaded!')
    } catch {
      toast.error('Failed to download report')
    } finally {
      setDownloadingPdf(false)
    }
  }

  // Chart data
  const modelChartData = result?.model_predictions?.map((mp, i) => ({
    model: mp.model_name.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
    premium: Math.round(mp.predicted_premium),
    fill: MODEL_COLORS[i],
  })) || []

  const shapData = result?.shap_explanations?.slice(0, 6).map(s => ({
    feature: s.feature_name.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
    value: Math.abs(s.shap_value),
    impact: s.impact,
  })) || []

  const riskScore = result?.risk_score || 0
  const riskColor = RISK_COLORS[result?.risk_category] || '#F59E0B'

  return (
    <div className="space-y-8 max-w-5xl">
      <div className="animate-in">
        <h1 className="font-display text-3xl font-medium text-slate-900">Premium Prediction</h1>
        <p className="text-slate-500 mt-1">Enter your details to get an AI-powered insurance estimate.</p>
      </div>

      <div className="grid lg:grid-cols-[420px,1fr] gap-8">
        {/* ── Form ─────────────────────────────────────────────────────── */}
        <div className="card p-6 space-y-6 animate-in h-fit">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <FormSection title="Personal Info" icon={User}>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Age</label>
                  <input
                    {...register('age', { required: 'Required', min: { value: 18, message: 'Min 18' }, max: { value: 100, message: 'Max 100' } })}
                    type="number" placeholder="35"
                    className="input-field"
                  />
                  {errors.age && <p className="text-red-500 text-xs mt-1">{errors.age.message}</p>}
                </div>
                <SelectField
                  label="Sex" name="sex" register={register} error={errors.sex}
                  options={[{ value: 'male', label: 'Male' }, { value: 'female', label: 'Female' }]}
                />
              </div>
            </FormSection>

            <FormSection title="Health Profile" icon={Activity}>
              <div>
                <label className="label">BMI (Body Mass Index)</label>
                <input
                  {...register('bmi', { required: 'Required', min: { value: 10, message: 'Min 10' }, max: { value: 60, message: 'Max 60' } })}
                  type="number" step="0.1" placeholder="27.5"
                  className="input-field"
                />
                {errors.bmi && <p className="text-red-500 text-xs mt-1">{errors.bmi.message}</p>}
                <p className="text-xs text-slate-400 mt-1">Normal: 18.5–24.9 | Overweight: 25–29.9 | Obese: ≥30</p>
              </div>
              <SelectField
                label="Smoker" name="smoker" register={register} error={errors.smoker}
                options={[{ value: 'no', label: 'No' }, { value: 'yes', label: 'Yes' }]}
              />
            </FormSection>

            <FormSection title="Family & Location" icon={Users}>
              <SelectField
                label="Number of Children" name="children" register={register} error={errors.children}
                options={[0,1,2,3,4,5].map(n => ({ value: String(n), label: `${n} ${n === 1 ? 'child' : 'children'}` }))}
              />
              <SelectField
                label="Region" name="region" register={register} error={errors.region}
                options={[
                  { value: 'northeast', label: 'Northeast' },
                  { value: 'northwest', label: 'Northwest' },
                  { value: 'southeast', label: 'Southeast' },
                  { value: 'southwest', label: 'Southwest' },
                ]}
              />
            </FormSection>

            <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
              {loading ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</>
              ) : (
                <><Calculator className="w-4 h-4" /> Predict Premium</>
              )}
            </button>
          </form>
        </div>

        {/* ── Results ──────────────────────────────────────────────────── */}
        <div className="space-y-4">
          {!result ? (
            <div className="card p-12 flex flex-col items-center justify-center text-center h-full min-h-[400px]">
              <div className="w-16 h-16 bg-slate-100 rounded-2xl flex items-center justify-center mb-4">
                <BarChart3 className="w-8 h-8 text-slate-300" />
              </div>
              <p className="text-slate-500 font-medium">Results will appear here</p>
              <p className="text-slate-400 text-sm mt-1">Fill in the form and click Predict Premium</p>
            </div>
          ) : (
            <>
              {/* Best Prediction Hero */}
              <div className="card p-6 bg-gradient-to-r from-primary-800 to-primary-700 text-white animate-in">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-white/60 text-sm">Best Estimate · {result.best_model.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}</p>
                    <p className="font-display text-5xl font-semibold mt-1">
                      ${result.best_prediction.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                    </p>
                    <p className="text-white/60 text-sm mt-1">estimated annual premium</p>
                  </div>
                  <div className="text-right">
                    <p className="text-white/60 text-xs mb-1">Risk Score</p>
                    <p className="font-display text-3xl font-semibold">{riskScore.toFixed(0)}</p>
                    <span className={clsx(
                      'text-xs font-semibold px-2 py-1 rounded-full capitalize',
                      result.risk_category === 'low' ? 'bg-emerald-400/30 text-emerald-100' :
                      result.risk_category === 'medium' ? 'bg-amber-400/30 text-amber-100' :
                      result.risk_category === 'high' ? 'bg-orange-400/30 text-orange-100' :
                      'bg-red-400/30 text-red-100'
                    )}>
                      {result.risk_category.replace('_', ' ')} risk
                    </span>
                  </div>
                </div>
                <button
                  onClick={handleDownloadPdf}
                  disabled={downloadingPdf}
                  className="mt-4 flex items-center gap-2 bg-white/15 hover:bg-white/25 text-white
                             text-sm font-medium px-4 py-2 rounded-xl transition-all"
                >
                  {downloadingPdf ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileDown className="w-4 h-4" />}
                  Download PDF Report
                </button>
              </div>

              {/* Model Comparison */}
              <div className="card p-6 animate-in">
                <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-primary-600" /> Model Comparison
                </h3>
                <div className="grid grid-cols-3 gap-3 mb-4">
                  {result.model_predictions.map((mp, i) => (
                    <PremiumCard
                      key={mp.model_name}
                      label={mp.model_name.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())}
                      value={mp.predicted_premium}
                      isTop={mp.model_name === result.best_model}
                      color={MODEL_COLORS[i]}
                    />
                  ))}
                </div>
                <ResponsiveContainer width="100%" height={160}>
                  <BarChart data={modelChartData} barSize={40}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                    <XAxis dataKey="model" tick={{ fontSize: 11 }} />
                    <YAxis tickFormatter={v => `$${(v/1000).toFixed(0)}k`} tick={{ fontSize: 10 }} />
                    <Tooltip formatter={v => [`$${v.toLocaleString()}`, 'Annual Premium']} />
                    <Bar dataKey="premium" radius={[6, 6, 0, 0]}>
                      {modelChartData.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* SHAP Feature Importance */}
              {shapData.length > 0 && (
                <div className="card p-6 animate-in">
                  <h3 className="font-semibold text-slate-800 mb-1 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-primary-600" /> Feature Impact (SHAP)
                  </h3>
                  <p className="text-xs text-slate-400 mb-4">How each factor influences your premium</p>
                  <div className="space-y-3">
                    {shapData.map((item) => {
                      const maxVal = Math.max(...shapData.map(d => d.value))
                      const pct = (item.value / maxVal) * 100
                      return (
                        <div key={item.feature}>
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="font-medium text-slate-600">{item.feature}</span>
                            <span className={clsx('font-semibold', item.impact === 'positive' ? 'text-red-500' : 'text-emerald-600')}>
                              {item.impact === 'positive' ? '+' : '-'}${item.value.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                            </span>
                          </div>
                          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className={clsx('h-full rounded-full transition-all duration-700',
                                item.impact === 'positive' ? 'bg-red-400' : 'bg-emerald-400')}
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
              {result.recommended_plans?.length > 0 && (
                <div className="card p-6 animate-in">
                  <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
                    <Shield className="w-4 h-4 text-primary-600" /> Recommended Plans
                  </h3>
                  <div className="space-y-3">
                    {result.recommended_plans.map((plan, i) => (
                      <div key={plan.plan_id} className={clsx(
                        'rounded-xl border p-4',
                        i === 0 ? 'border-primary-200 bg-primary-50' : 'border-slate-100'
                      )}>
                        <div className="flex items-start justify-between">
                          <div>
                            <div className="flex items-center gap-2">
                              {i === 0 && <CheckCircle className="w-4 h-4 text-primary-600" />}
                              <p className="font-semibold text-slate-800 text-sm">{plan.plan_name}</p>
                              <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full">{plan.plan_type}</span>
                            </div>
                            <p className="text-xs text-slate-500 mt-0.5">{plan.provider}</p>
                            <div className="flex gap-3 mt-2 text-xs text-slate-500">
                              <span>Deductible: <b className="text-slate-700">${plan.deductible.toLocaleString()}</b></span>
                              <span>Coverage: <b className="text-slate-700">${(plan.coverage_limit/1000000).toFixed(1)}M</b></span>
                            </div>
                          </div>
                          <div className="text-right ml-4">
                            <p className="font-display text-lg font-semibold text-primary-800">
                              ${plan.monthly_premium.toLocaleString('en-US', { maximumFractionDigits: 0 })}/mo
                            </p>
                            <p className="text-xs text-slate-400">${plan.annual_premium.toLocaleString('en-US', { maximumFractionDigits: 0 })}/yr</p>
                            <p className="text-xs font-medium text-primary-600 mt-1">{plan.match_score.toFixed(0)}% match</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
