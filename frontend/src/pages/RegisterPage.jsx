import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { Shield, Mail, Lock, User, Loader2 } from 'lucide-react'
import useAuthStore from '../store/authStore'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const { register: registerUser, isLoading } = useAuthStore()
  const navigate = useNavigate()
  const { register, handleSubmit, watch, formState: { errors } } = useForm()

  const onSubmit = async (data) => {
    const { confirmPassword, ...payload } = data
    const result = await registerUser(payload)
    if (result.success) {
      toast.success('Account created! Please sign in.')
      navigate('/login')
    } else {
      toast.error(result.error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-900 via-primary-800 to-slate-900 flex items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 right-1/3 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md animate-in">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-white/10 backdrop-blur rounded-2xl mb-4">
            <Shield className="w-7 h-7 text-white" />
          </div>
          <h1 className="font-display text-3xl font-medium text-white">Create Account</h1>
          <p className="text-white/50 text-sm mt-1">Start predicting your insurance premiums</p>
        </div>

        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-8 shadow-2xl">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label text-white/80">Username</label>
                <div className="relative">
                  <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                  <input
                    {...register('username', {
                      required: 'Required',
                      minLength: { value: 3, message: 'Min 3 chars' },
                    })}
                    placeholder="johndoe"
                    className="input-field pl-10 bg-white/10 border-white/20 text-white placeholder-white/30 focus:border-white/50"
                  />
                </div>
                {errors.username && <p className="text-red-300 text-xs mt-1">{errors.username.message}</p>}
              </div>

              <div>
                <label className="label text-white/80">Full Name</label>
                <input
                  {...register('full_name')}
                  placeholder="John Doe"
                  className="input-field bg-white/10 border-white/20 text-white placeholder-white/30 focus:border-white/50"
                />
              </div>
            </div>

            <div>
              <label className="label text-white/80">Email</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  {...register('email', {
                    required: 'Email is required',
                    pattern: { value: /\S+@\S+\.\S+/, message: 'Invalid email' },
                  })}
                  type="email"
                  placeholder="you@example.com"
                  className="input-field pl-10 bg-white/10 border-white/20 text-white placeholder-white/30 focus:border-white/50"
                />
              </div>
              {errors.email && <p className="text-red-300 text-xs mt-1">{errors.email.message}</p>}
            </div>

            <div>
              <label className="label text-white/80">Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  {...register('password', {
                    required: 'Password is required',
                    minLength: { value: 8, message: 'Min 8 characters' },
                  })}
                  type="password"
                  placeholder="Min 8 characters"
                  className="input-field pl-10 bg-white/10 border-white/20 text-white placeholder-white/30 focus:border-white/50"
                />
              </div>
              {errors.password && <p className="text-red-300 text-xs mt-1">{errors.password.message}</p>}
            </div>

            <div>
              <label className="label text-white/80">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  {...register('confirmPassword', {
                    required: 'Please confirm password',
                    validate: (v) => v === watch('password') || 'Passwords do not match',
                  })}
                  type="password"
                  placeholder="Repeat password"
                  className="input-field pl-10 bg-white/10 border-white/20 text-white placeholder-white/30 focus:border-white/50"
                />
              </div>
              {errors.confirmPassword && <p className="text-red-300 text-xs mt-1">{errors.confirmPassword.message}</p>}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 bg-white text-primary-800
                         hover:bg-white/90 font-semibold px-5 py-3 rounded-xl transition-all mt-2
                         disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? <><Loader2 className="w-4 h-4 animate-spin" /> Creating...</> : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-white/50 text-sm mt-6">
            Already have an account?{' '}
            <Link to="/login" className="text-white font-medium hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
