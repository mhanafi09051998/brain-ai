'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import {
  Wallet, ArrowDownRight, ArrowUpRight, PlusCircle, Download,
  Trash2, Edit3, Search, Calendar as CalendarIcon, CreditCard, Banknote, Smartphone,
  LogOut, User, PieChart, X, Check, Sun, Moon, AlertTriangle, CheckCircle2,
  Info, ChevronLeft, ChevronRight, Eye, EyeOff
} from 'lucide-react';

interface Transaction {
  id: number;
  type: 'income' | 'expense';
  amount: number;
  category: string;
  wallet: string;
  date: string;
  description: string;
  created_at: string;
}

interface WalletData {
  name: string;
  icon: string;
  balance: number;
  income: number;
  expense: number;
}

interface CategoryStat {
  category: string;
  total: number;
}

interface Toast {
  id: number;
  type: 'success' | 'error' | 'info';
  message: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<{ name: string; email: string } | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [summary, setSummary] = useState({ totalIncome: 0, totalExpense: 0, netBalance: 0 });
  const [wallets, setWallets] = useState<WalletData[]>([]);
  const [categoryStats, setCategoryStats] = useState<CategoryStat[]>([]);
  const [loading, setLoading] = useState(true);

  // Theme State
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  // In-App Toast System
  const [toasts, setToasts] = useState<Toast[]>([]);

  // Filters & Selected Date
  const [filterType, setFilterType] = useState('all');
  const [filterWallet, setFilterWallet] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCalendarDate, setSelectedCalendarDate] = useState<string | null>(null);

  // Calendar View Month Navigation
  const [calendarDate, setCalendarDate] = useState(new Date());

  // Pagination State (Max 10 rows per page)
  const [currentPage, setCurrentPage] = useState(1);
  const PAGE_SIZE = 10;

  // Add Modal State
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [formType, setFormType] = useState<'income' | 'expense'>('expense');
  const [formAmount, setFormAmount] = useState('');
  const [formCategory, setFormCategory] = useState('Makanan & Minuman');
  const [formWallet, setFormWallet] = useState('Kas Tunai');
  const [formDate, setFormDate] = useState(new Date().toISOString().split('T')[0]);
  const [formDesc, setFormDesc] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Edit Modal State
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingTx, setEditingTx] = useState<Transaction | null>(null);

  // Delete Confirmation Modal State
  const [deleteCandidate, setDeleteCandidate] = useState<Transaction | null>(null);
  const [deleting, setDeleting] = useState(false);

  const categories = {
    expense: ['Makanan & Minuman', 'Transportasi', 'Belanja', 'Tagihan & Utilitas', 'Hiburan', 'Kesehatan', 'Pendidikan', 'Lainnya'],
    income: ['Gaji / Pendapatan', 'Bisnis / Penjualan', 'Bonus / THR', 'Investasi / Dividen', 'Hadiah', 'Lainnya']
  };

  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    const id = Date.now();
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  useEffect(() => {
    const saved = localStorage.getItem('zolu_theme') as 'dark' | 'light';
    if (saved) {
      setTheme(saved);
      document.documentElement.classList.toggle('dark', saved === 'dark');
    } else {
      document.documentElement.classList.add('dark');
    }
  }, []);

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    localStorage.setItem('zolu_theme', next);
    document.documentElement.classList.toggle('dark', next === 'dark');
    showToast(`Beralih ke mode ${next === 'dark' ? 'gelap' : 'terang'}`, 'info');
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const meRes = await fetch('/api/auth/me');
      if (!meRes.ok) {
        router.push('/login');
        return;
      }
      const meData = await meRes.json();
      setUser(meData.user);

      const res = await fetch('/api/transactions');
      const data = await res.json();
      if (res.ok) {
        setTransactions(data.transactions || []);
        setSummary(data.summary || { totalIncome: 0, totalExpense: 0, netBalance: 0 });
        setWallets(data.wallets || []);
        setCategoryStats(data.categoryStats || []);
      }
    } catch (err) {
      console.error(err);
      showToast('Gagal memuat data kas', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    router.push('/login');
  };

  const handleAddTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formAmount || parseFloat(formAmount) <= 0) {
      showToast('Nominal transaksi harus lebih besar dari 0', 'error');
      return;
    }

    try {
      setSubmitting(true);
      const res = await fetch('/api/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: formType,
          amount: parseFloat(formAmount),
          category: formCategory,
          wallet: formWallet,
          date: formDate,
          description: formDesc
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Gagal menyimpan');

      showToast('Transaksi berhasil ditambahkan!', 'success');
      setIsAddModalOpen(false);
      setFormAmount('');
      setFormDesc('');
      fetchDashboardData();
    } catch (err: any) {
      showToast(err.message, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const openEditModal = (tx: Transaction) => {
    setEditingTx(tx);
    setIsEditModalOpen(true);
  };

  const handleUpdateTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTx) return;

    try {
      setSubmitting(true);
      const res = await fetch(`/api/transactions/${editingTx.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: editingTx.type,
          amount: editingTx.amount,
          category: editingTx.category,
          wallet: editingTx.wallet,
          date: editingTx.date,
          description: editingTx.description
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Gagal memperbarui');

      showToast('Transaksi berhasil diperbarui!', 'success');
      setIsEditModalOpen(false);
      setEditingTx(null);
      fetchDashboardData();
    } catch (err: any) {
      showToast(err.message, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteConfirmed = async () => {
    if (!deleteCandidate) return;

    try {
      setDeleting(true);
      const res = await fetch(`/api/transactions/${deleteCandidate.id}`, {
        method: 'DELETE'
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Gagal menghapus');

      showToast('Transaksi berhasil dihapus!', 'success');
      setDeleteCandidate(null);
      fetchDashboardData();
    } catch (err: any) {
      showToast(err.message, 'error');
    } finally {
      setDeleting(false);
    }
  };

  // Reset page to 1 whenever filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filterType, filterWallet, searchQuery, selectedCalendarDate]);

  // Calendar Daily Aggregations Map
  const dailyStatsMap = useMemo(() => {
    const map: Record<string, { income: number; expense: number; count: number }> = {};
    transactions.forEach((tx) => {
      if (!map[tx.date]) {
        map[tx.date] = { income: 0, expense: 0, count: 0 };
      }
      map[tx.date].count += 1;
      if (tx.type === 'income') map[tx.date].income += tx.amount;
      else map[tx.date].expense += tx.amount;
    });
    return map;
  }, [transactions]);

  // Filtered transactions
  const filteredTransactions = useMemo(() => {
    return transactions.filter(t => {
      if (selectedCalendarDate && t.date !== selectedCalendarDate) return false;
      if (filterType !== 'all' && t.type !== filterType) return false;
      if (filterWallet !== 'all' && t.wallet !== filterWallet) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        return (t.description?.toLowerCase().includes(q) || t.category.toLowerCase().includes(q));
      }
      return true;
    });
  }, [transactions, selectedCalendarDate, filterType, filterWallet, searchQuery]);

  // Pagination calculation
  const totalPages = Math.max(1, Math.ceil(filteredTransactions.length / PAGE_SIZE));
  const paginatedTransactions = useMemo(() => {
    const start = (currentPage - 1) * PAGE_SIZE;
    return filteredTransactions.slice(start, start + PAGE_SIZE);
  }, [filteredTransactions, currentPage]);

  const formatIDR = (val: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0
    }).format(val);
  };

  const formatCompactIDR = (val: number) => {
    if (!val || val === 0) return '0';
    const abs = Math.abs(val);
    if (abs >= 1_000_000_000) {
      return (val / 1_000_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
    }
    if (abs >= 1_000_000) {
      return (val / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'jt';
    }
    if (abs >= 1_000) {
      return (val / 1_000).toFixed(0) + 'k';
    }
    return val.toLocaleString('id-ID');
  };

  // Calendar Generation Helpers
  const year = calendarDate.getFullYear();
  const month = calendarDate.getMonth();
  const monthNames = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
  ];

  const firstDayOfMonth = new Date(year, month, 1).getDay(); // 0 is Sunday
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  const prevMonth = () => {
    setCalendarDate(new Date(year, month - 1, 1));
  };
  const nextMonth = () => {
    setCalendarDate(new Date(year, month + 1, 1));
  };

  const calendarDays = useMemo(() => {
    const days: { dayNumber: number | null; dateStr: string | null }[] = [];
    // Leading empty days
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push({ dayNumber: null, dateStr: null });
    }
    // Days in current month
    for (let d = 1; d <= daysInMonth; d++) {
      const mm = String(month + 1).padStart(2, '0');
      const dd = String(d).padStart(2, '0');
      days.push({ dayNumber: d, dateStr: `${year}-${mm}-${dd}` });
    }
    return days;
  }, [year, month, firstDayOfMonth, daysInMonth]);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#07080c] text-slate-900 dark:text-slate-100 pb-20 transition-colors duration-300">
      
      {/* Floating Toast */}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 max-w-sm pointer-events-none">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-2xl shadow-xl backdrop-blur-md border text-sm font-medium animate-in slide-in-from-bottom-5 duration-300 ${
              t.type === 'success'
                ? 'bg-emerald-500/90 text-white border-emerald-400/30'
                : t.type === 'error'
                ? 'bg-rose-500/90 text-white border-rose-400/30'
                : 'bg-slate-900/90 dark:bg-white/90 text-white dark:text-slate-900 border-white/20'
            }`}
          >
            {t.type === 'success' && <CheckCircle2 className="w-4 h-4 flex-shrink-0" />}
            {t.type === 'error' && <AlertTriangle className="w-4 h-4 flex-shrink-0" />}
            {t.type === 'info' && <Info className="w-4 h-4 flex-shrink-0" />}
            <span>{t.message}</span>
          </div>
        ))}
      </div>

      {/* Top Navbar */}
      <header className="sticky top-0 z-40 bg-white/80 dark:bg-[#0c0e17]/80 backdrop-blur-xl border-b border-slate-200 dark:border-white/5 px-4 sm:px-8 py-3.5 transition-colors duration-300">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 p-[1px] shadow-lg shadow-emerald-500/20">
              <div className="w-full h-full bg-white dark:bg-[#090a0f] rounded-[11px] flex items-center justify-center">
                <Wallet className="w-5 h-5 text-emerald-500 dark:text-emerald-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-slate-900 dark:text-white font-mono">
                  KAS<span className="text-emerald-500 dark:text-emerald-400">.ZOLU</span>
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={toggleTheme}
              title={theme === 'dark' ? 'Ganti ke Mode Terang' : 'Ganti ke Mode Gelap'}
              className="p-2.5 rounded-xl bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 transition-all hover:scale-105 active:scale-95"
            >
              {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-600" />}
            </button>

            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-white/[0.03] border border-slate-200 dark:border-white/5 text-xs">
              <User className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />
              <span className="font-medium text-slate-700 dark:text-slate-300">{user?.name || 'Admin Zolu'}</span>
            </div>

            <button
              onClick={() => setIsAddModalOpen(true)}
              className="px-3.5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-white dark:text-black font-bold text-xs flex items-center gap-1.5 shadow-lg shadow-emerald-500/20 transition-all active:scale-95"
            >
              <PlusCircle className="w-4 h-4" />
              <span className="hidden sm:inline">Tambah Transaksi</span>
              <span className="sm:hidden">Tambah</span>
            </button>

            <button
              onClick={handleLogout}
              title="Logout"
              className="p-2 rounded-xl bg-slate-100 dark:bg-white/5 hover:bg-rose-500/10 hover:text-rose-500 text-slate-500 dark:text-slate-400 transition-all"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-8 pt-8 space-y-8">
        
        {/* SUMMARY CARDS */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          <div className="p-6 rounded-3xl bg-white dark:bg-gradient-to-br dark:from-emerald-950/40 dark:via-[#0e121e] dark:to-[#0c0e17] border border-emerald-500/30 shadow-lg dark:shadow-xl relative overflow-hidden transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">Total Saldo Kas</span>
              <div className="p-2.5 rounded-2xl bg-emerald-500/15 text-emerald-600 dark:text-emerald-400">
                <Wallet className="w-5 h-5" />
              </div>
            </div>
            <div className="text-3xl font-extrabold font-mono text-slate-900 dark:text-white mb-2 tracking-tight">
              {formatIDR(summary.netBalance)}
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
              <span className="text-emerald-600 dark:text-emerald-400 font-mono font-semibold">Arus Kas Bersih</span>
              <span>• Semua Dompet</span>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-white dark:bg-[#0e111a] border border-slate-200 dark:border-white/5 shadow-lg dark:shadow-xl transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-cyan-600 dark:text-cyan-400">Total Pemasukan</span>
              <div className="p-2.5 rounded-2xl bg-cyan-500/10 text-cyan-600 dark:text-cyan-400">
                <ArrowDownRight className="w-5 h-5" />
              </div>
            </div>
            <div className="text-3xl font-extrabold font-mono text-cyan-700 dark:text-cyan-300 mb-2 tracking-tight">
              {formatIDR(summary.totalIncome)}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400">
              Total dana masuk tercatat
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-white dark:bg-[#0e111a] border border-slate-200 dark:border-white/5 shadow-lg dark:shadow-xl transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono font-semibold uppercase tracking-wider text-rose-600 dark:text-rose-400">Total Pengeluaran</span>
              <div className="p-2.5 rounded-2xl bg-rose-500/10 text-rose-600 dark:text-rose-400">
                <ArrowUpRight className="w-5 h-5" />
              </div>
            </div>
            <div className="text-3xl font-extrabold font-mono text-rose-700 dark:text-rose-300 mb-2 tracking-tight">
              {formatIDR(summary.totalExpense)}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400">
              Total belanja & beban tercatat
            </div>
          </div>
        </div>

        {/* KALENDER ARUS KAS HARIAN (RESPONSIVE) */}
        <div className="p-3.5 sm:p-6 rounded-2xl sm:rounded-3xl bg-white dark:bg-[#0e111a] border border-slate-200 dark:border-white/5 shadow-xl">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-3.5 sm:mb-6">
            <div className="flex items-center gap-2.5 sm:gap-3">
              <div className="p-2 sm:p-2.5 bg-emerald-500/10 text-emerald-500 rounded-xl sm:rounded-2xl">
                <CalendarIcon className="w-4 h-4 sm:w-5 sm:h-5" />
              </div>
              <div>
                <h3 className="font-bold text-sm sm:text-base text-slate-900 dark:text-white tracking-tight">
                  Kalender Pemasukan & Pengeluaran Harian
                </h3>
                <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 font-mono">
                  Pantau total masuk dan keluar per hari secara visual. Klik tanggal untuk memfilter riwayat.
                </p>
              </div>
            </div>

            {/* Month selector controls */}
            <div className="flex items-center gap-1.5 sm:gap-2 w-full sm:w-auto justify-between sm:justify-end">
              {selectedCalendarDate && (
                <button
                  onClick={() => setSelectedCalendarDate(null)}
                  className="px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-lg sm:rounded-xl bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 text-[10px] sm:text-xs font-mono text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-white/10 flex items-center gap-1"
                >
                  <X className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
                  <span>Reset: <span className="font-bold">{selectedCalendarDate}</span></span>
                </button>
              )}
              <div className="flex items-center bg-slate-100 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 rounded-xl sm:rounded-2xl p-0.5 sm:p-1 ml-auto sm:ml-0">
                <button
                  onClick={prevMonth}
                  className="p-1 sm:p-1.5 rounded-lg sm:rounded-xl hover:bg-white dark:hover:bg-white/10 text-slate-700 dark:text-slate-300"
                  title="Bulan Sebelumnya"
                >
                  <ChevronLeft className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                </button>
                <span className="px-2 sm:px-3 text-[11px] sm:text-xs font-bold font-mono text-slate-900 dark:text-white min-w-[100px] sm:min-w-[130px] text-center">
                  {monthNames[month]} {year}
                </span>
                <button
                  onClick={nextMonth}
                  className="p-1 sm:p-1.5 rounded-lg sm:rounded-xl hover:bg-white dark:hover:bg-white/10 text-slate-700 dark:text-slate-300"
                  title="Bulan Berikutnya"
                >
                  <ChevronRight className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-1 sm:gap-2 text-center text-xs">
            {['Min', 'Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab'].map((d) => (
              <div key={d} className="py-1 sm:py-2 font-bold font-mono text-slate-400 uppercase text-[9px] sm:text-[11px]">
                {d}
              </div>
            ))}

            {calendarDays.map((item, idx) => {
              if (!item.dayNumber || !item.dateStr) {
                return <div key={`empty-${idx}`} className="min-h-[56px] sm:min-h-[85px] rounded-xl sm:rounded-2xl bg-transparent" />;
              }

              const stats = dailyStatsMap[item.dateStr];
              const isSelected = selectedCalendarDate === item.dateStr;
              const isToday = new Date().toISOString().split('T')[0] === item.dateStr;

              return (
                <button
                  type="button"
                  key={item.dateStr}
                  onClick={() => {
                    if (isSelected) setSelectedCalendarDate(null);
                    else setSelectedCalendarDate(item.dateStr);
                  }}
                  className={`min-h-[56px] sm:min-h-[85px] p-1 sm:p-2 rounded-xl sm:rounded-2xl border text-left flex flex-col justify-between transition-all relative ${
                    isSelected
                      ? 'bg-emerald-500/15 border-emerald-500 shadow-md ring-2 ring-emerald-500/30'
                      : isToday
                      ? 'bg-slate-100/80 dark:bg-white/[0.05] border-emerald-500/50'
                      : stats && stats.count > 0
                      ? 'bg-white dark:bg-[#121624] border-slate-200 dark:border-white/10 hover:border-emerald-500/40 hover:bg-slate-50 dark:hover:bg-[#161c2e]'
                      : 'bg-slate-50/50 dark:bg-white/[0.01] border-slate-200/60 dark:border-white/5 opacity-60 hover:opacity-100'
                  }`}
                >
                  <div className="flex items-center justify-between w-full">
                    <span
                      className={`text-[10px] sm:text-xs font-bold font-mono px-1 sm:px-1.5 py-0.5 rounded-md sm:rounded-lg ${
                        isToday
                          ? 'bg-emerald-500 text-white dark:text-black font-extrabold'
                          : isSelected
                          ? 'bg-emerald-500/30 text-emerald-600 dark:text-emerald-400'
                          : 'text-slate-700 dark:text-slate-300'
                      }`}
                    >
                      {item.dayNumber}
                    </span>
                    {stats && stats.count > 0 && (
                      <span className="hidden sm:inline text-[10px] font-mono text-slate-400">
                        {stats.count} tx
                      </span>
                    )}
                  </div>

                  {/* Mobile View: Visible Nominal Numbers */}
                  <div className="flex sm:hidden flex-col gap-0.5 mt-1 w-full overflow-hidden text-[8px] leading-[10px] font-mono font-bold">
                    {stats && stats.income > 0 ? (
                      <div className="text-emerald-600 dark:text-emerald-400 truncate" title={`Masuk: ${formatIDR(stats.income)}`}>
                        +{formatCompactIDR(stats.income)}
                      </div>
                    ) : null}
                    {stats && stats.expense > 0 ? (
                      <div className="text-rose-600 dark:text-rose-400 truncate" title={`Keluar: ${formatIDR(stats.expense)}`}>
                        -{formatCompactIDR(stats.expense)}
                      </div>
                    ) : null}
                    {(!stats || (stats.income === 0 && stats.expense === 0)) && (
                      <div className="text-slate-300 dark:text-slate-700 text-[8px] italic leading-[10px]">
                        -
                      </div>
                    )}
                  </div>

                  {/* Desktop View: Full amounts */}
                  <div className="hidden sm:block space-y-0.5 mt-1 text-[10px] font-mono">
                    {stats && stats.income > 0 ? (
                      <div className="text-emerald-600 dark:text-emerald-400 truncate font-semibold" title={`Masuk: ${formatIDR(stats.income)}`}>
                        +{formatIDR(stats.income)}
                      </div>
                    ) : null}
                    {stats && stats.expense > 0 ? (
                      <div className="text-rose-600 dark:text-rose-400 truncate font-semibold" title={`Keluar: ${formatIDR(stats.expense)}`}>
                        -{formatIDR(stats.expense)}
                      </div>
                    ) : null}
                    {(!stats || (stats.income === 0 && stats.expense === 0)) && (
                      <div className="text-slate-300 dark:text-slate-700 text-[9px] italic">
                        -
                      </div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* WALLETS AND CATEGORIES ROW */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="p-6 rounded-3xl bg-white dark:bg-[#0e111a] border border-slate-200 dark:border-white/5 shadow-md">
            <h3 className="text-sm font-bold uppercase tracking-wider font-mono text-slate-700 dark:text-slate-300 mb-4 flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
              <span>Dompet & Rekening</span>
            </h3>
            <div className="space-y-3">
              {wallets.map(w => (
                <div key={w.name} className="p-3.5 rounded-2xl bg-slate-50 dark:bg-white/[0.02] border border-slate-200/80 dark:border-white/5 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-white dark:bg-white/5 text-slate-700 dark:text-slate-300 shadow-sm">
                      {w.name === 'Kas Tunai' && <Banknote className="w-4 h-4 text-amber-500" />}
                      {w.name === 'Rekening Bank' && <CreditCard className="w-4 h-4 text-blue-500" />}
                      {w.name === 'E-Wallet' && <Smartphone className="w-4 h-4 text-emerald-500" />}
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-900 dark:text-white">{w.name}</div>
                      <div className="text-[11px] text-slate-500 font-mono">Masuk: {formatIDR(w.income)}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-bold font-mono text-slate-900 dark:text-white">{formatIDR(w.balance)}</div>
                    <div className="text-[10px] text-rose-500 dark:text-rose-400 font-mono">Keluar: {formatIDR(w.expense)}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="lg:col-span-2 p-6 rounded-3xl bg-white dark:bg-[#0e111a] border border-slate-200 dark:border-white/5 shadow-md">
            <h3 className="text-sm font-bold uppercase tracking-wider font-mono text-slate-700 dark:text-slate-300 mb-4 flex items-center gap-2">
              <PieChart className="w-4 h-4 text-purple-500 dark:text-purple-400" />
              <span>Distribusi Pengeluaran Berdasarkan Kategori</span>
            </h3>

            {categoryStats.length === 0 ? (
              <div className="h-40 flex items-center justify-center text-xs text-slate-400 font-mono">
                Belum ada data pengeluaran
              </div>
            ) : (
              <div className="space-y-3.5">
                {categoryStats.slice(0, 5).map(cat => {
                  const percent = summary.totalExpense > 0 
                    ? Math.round((cat.total / summary.totalExpense) * 100) 
                    : 0;
                  return (
                    <div key={cat.category}>
                      <div className="flex items-center justify-between text-xs font-mono mb-1.5">
                        <span className="text-slate-700 dark:text-slate-300 font-semibold">{cat.category}</span>
                        <span className="text-slate-900 dark:text-white font-bold">{formatIDR(cat.total)} ({percent}%)</span>
                      </div>
                      <div className="w-full bg-slate-100 dark:bg-white/5 h-2.5 rounded-full overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-500"
                          style={{ width: `${percent}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* TRANSACTIONS TABLE SECTION WITH PAGINATION (MAX 10) */}
        <div className="bg-white dark:bg-[#0e111a] border border-slate-200 dark:border-white/5 rounded-3xl p-6 shadow-xl space-y-5">
          
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">Riwayat Catatan Kas</h2>
                {selectedCalendarDate && (
                  <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 font-semibold">
                    Filter Tanggal: {selectedCalendarDate}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-mono mt-0.5">
                Total {filteredTransactions.length} transaksi • Halaman {currentPage} dari {totalPages}
              </p>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap items-center gap-2.5">
              <div className="relative">
                <Search className="w-3.5 h-3.5 text-slate-400 dark:text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Cari transaksi..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8 pr-3 py-1.5 text-xs rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white outline-none focus:border-emerald-500"
                />
              </div>

              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-3 py-1.5 text-xs rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 outline-none"
              >
                <option value="all">Semua Tipe</option>
                <option value="income">Pemasukan</option>
                <option value="expense">Pengeluaran</option>
              </select>

              <select
                value={filterWallet}
                onChange={(e) => setFilterWallet(e.target.value)}
                className="px-3 py-1.5 text-xs rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 outline-none"
              >
                <option value="all">Semua Dompet</option>
                <option value="Kas Tunai">Kas Tunai</option>
                <option value="Rekening Bank">Rekening Bank</option>
                <option value="E-Wallet">E-Wallet</option>
              </select>

              <a
                href="/api/export"
                download
                className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-white/5 hover:bg-slate-200 dark:hover:bg-white/10 border border-slate-200 dark:border-white/10 text-xs font-mono text-slate-700 dark:text-slate-300 flex items-center gap-1.5 transition-all"
              >
                <Download className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />
                <span>Export CSV</span>
              </a>
            </div>
          </div>

          {/* Table */}
          {filteredTransactions.length === 0 ? (
            <div className="py-16 text-center text-slate-400 dark:text-slate-500 text-sm font-mono">
              Tidak ada data transaksi yang sesuai filter.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-100 dark:border-white/5 text-[11px] font-mono text-slate-400 uppercase tracking-wider">
                    <th className="pb-3 pl-2">Tanggal</th>
                    <th className="pb-3">Kategori</th>
                    <th className="pb-3">Deskripsi</th>
                    <th className="pb-3">Dompet</th>
                    <th className="pb-3 text-right">Nominal</th>
                    <th className="pb-3 text-right pr-2">Aksi</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-white/[0.03]">
                  {paginatedTransactions.map((tx) => (
                    <tr key={tx.id} className="hover:bg-slate-50 dark:hover:bg-white/[0.02] transition-colors group">
                      <td className="py-3.5 pl-2 font-mono text-xs text-slate-500 dark:text-slate-400 whitespace-nowrap">
                        {tx.date}
                      </td>
                      <td className="py-3.5">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-100 dark:bg-white/5 text-slate-700 dark:text-slate-300 border border-slate-200/50 dark:border-white/5">
                          {tx.category}
                        </span>
                      </td>
                      <td className="py-3.5 text-slate-700 dark:text-slate-300 max-w-xs truncate">
                        {tx.description || '-'}
                      </td>
                      <td className="py-3.5 text-xs font-mono text-slate-500 dark:text-slate-400">
                        {tx.wallet}
                      </td>
                      <td className="py-3.5 text-right font-mono font-bold whitespace-nowrap">
                        {tx.type === 'income' ? (
                          <span className="text-emerald-600 dark:text-emerald-400">+{formatIDR(tx.amount)}</span>
                        ) : (
                          <span className="text-rose-600 dark:text-rose-400">-{formatIDR(tx.amount)}</span>
                        )}
                      </td>
                      <td className="py-3.5 text-right pr-2 whitespace-nowrap">
                        <button
                          onClick={() => openEditModal(tx)}
                          title="Edit Transaksi"
                          className="opacity-100 sm:opacity-0 sm:group-hover:opacity-100 p-1.5 rounded-lg hover:bg-slate-200 dark:hover:bg-white/10 text-slate-400 dark:text-slate-500 hover:text-slate-700 dark:hover:text-white transition-all mr-1"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => setDeleteCandidate(tx)}
                          title="Hapus Transaksi"
                          className="opacity-100 sm:opacity-0 sm:group-hover:opacity-100 p-1.5 rounded-lg hover:bg-rose-500/20 text-slate-400 dark:text-slate-500 hover:text-rose-500 transition-all"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* PAGINATION CONTROLS (MAX 10 DATA) */}
          {filteredTransactions.length > 0 && (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-4 border-t border-slate-100 dark:border-white/5 text-xs font-mono">
              <div className="text-slate-500 dark:text-slate-400">
                Menampilkan <span className="text-slate-900 dark:text-white font-bold">{(currentPage - 1) * PAGE_SIZE + 1}</span> -{' '}
                <span className="text-slate-900 dark:text-white font-bold">
                  {Math.min(currentPage * PAGE_SIZE, filteredTransactions.length)}
                </span>{' '}
                dari <span className="text-slate-900 dark:text-white font-bold">{filteredTransactions.length}</span> transaksi (Maks 10 per halaman)
              </div>

              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] text-slate-700 dark:text-slate-300 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-white/5 transition-all flex items-center gap-1"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                  <span>Sebelumnya</span>
                </button>

                {Array.from({ length: totalPages }, (_, i) => i + 1)
                  .filter((p) => p === 1 || p === totalPages || Math.abs(p - currentPage) <= 1)
                  .map((p, idx, arr) => {
                    const prevP = arr[idx - 1];
                    return (
                      <React.Fragment key={p}>
                        {prevP && p - prevP > 1 && <span className="px-1 text-slate-400">...</span>}
                        <button
                          onClick={() => setCurrentPage(p)}
                          className={`w-8 h-8 rounded-xl text-xs font-mono font-bold transition-all ${
                            currentPage === p
                              ? 'bg-emerald-500 text-white dark:text-black shadow-md shadow-emerald-500/20'
                              : 'border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5'
                          }`}
                        >
                          {p}
                        </button>
                      </React.Fragment>
                    );
                  })}

                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/[0.02] text-slate-700 dark:text-slate-300 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-white/5 transition-all flex items-center gap-1"
                >
                  <span>Berikutnya</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

        </div>

      </main>

      {/* 1. CUSTOM MODAL: TAMBAH TRANSAKSI */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-md bg-white dark:bg-[#0e111a] border border-slate-200 dark:border-white/10 rounded-3xl p-6 shadow-2xl relative animate-in zoom-in-95 duration-200">
            
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">Tambah Catatan Transaksi</h3>
              <button onClick={() => setIsAddModalOpen(false)} className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 p-1 bg-slate-100 dark:bg-white/[0.03] rounded-2xl border border-slate-200 dark:border-white/5 mb-5">
              <button
                type="button"
                onClick={() => {
                  setFormType('expense');
                  setFormCategory(categories.expense[0]);
                }}
                className={`py-2 text-xs font-bold font-mono rounded-xl transition-all ${
                  formType === 'expense'
                    ? 'bg-rose-500 text-white shadow-md shadow-rose-500/25'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Pengeluaran
              </button>
              <button
                type="button"
                onClick={() => {
                  setFormType('income');
                  setFormCategory(categories.income[0]);
                }}
                className={`py-2 text-xs font-bold font-mono rounded-xl transition-all ${
                  formType === 'income'
                    ? 'bg-emerald-500 text-white dark:text-black shadow-md shadow-emerald-500/25'
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                Pemasukan
              </button>
            </div>

            <form onSubmit={handleAddTransaction} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 font-mono">
                  Nominal (Rp) *
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  step="any"
                  value={formAmount}
                  onChange={(e) => setFormAmount(e.target.value)}
                  placeholder="Contoh: 50000"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white font-mono text-sm outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 font-mono">
                    Kategori *
                  </label>
                  <select
                    value={formCategory}
                    onChange={(e) => setFormCategory(e.target.value)}
                    className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white text-xs outline-none focus:border-emerald-500"
                  >
                    {categories[formType].map((c) => (
                      <option key={c} value={c} className="dark:bg-[#0e111a]">
                        {c}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 font-mono">
                    Dompet / Akun *
                  </label>
                  <select
                    value={formWallet}
                    onChange={(e) => setFormWallet(e.target.value)}
                    className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white text-xs outline-none focus:border-emerald-500"
                  >
                    <option value="Kas Tunai" className="dark:bg-[#0e111a]">Kas Tunai</option>
                    <option value="Rekening Bank" className="dark:bg-[#0e111a]">Rekening Bank</option>
                    <option value="E-Wallet" className="dark:bg-[#0e111a]">E-Wallet</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 font-mono">
                  Tanggal *
                </label>
                <input
                  type="date"
                  required
                  value={formDate}
                  onChange={(e) => setFormDate(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white font-mono text-xs outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 font-mono">
                  Deskripsi / Keterangan (Opsional)
                </label>
                <input
                  type="text"
                  value={formDesc}
                  onChange={(e) => setFormDesc(e.target.value)}
                  placeholder="Contoh: Makan siang bareng tim"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white text-xs outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 text-xs font-medium"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-white dark:text-black font-bold text-xs shadow-lg shadow-emerald-500/20"
                >
                  {submitting ? 'Menyimpan...' : 'Simpan Transaksi'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 2. CUSTOM MODAL: EDIT TRANSAKSI */}
      {isEditModalOpen && editingTx && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-md bg-white dark:bg-[#0e111a] border border-slate-200 dark:border-white/10 rounded-3xl p-6 shadow-2xl relative animate-in zoom-in-95 duration-200">
            
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">Edit Transaksi #{editingTx.id}</h3>
              <button onClick={() => setIsEditModalOpen(false)} className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUpdateTransaction} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 font-mono">
                  Nominal (Rp) *
                </label>
                <input
                  type="number"
                  required
                  min="1"
                  step="any"
                  value={editingTx.amount}
                  onChange={(e) => setEditingTx({ ...editingTx, amount: parseFloat(e.target.value) || 0 })}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white font-mono text-sm outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 font-mono">
                    Kategori *
                  </label>
                  <select
                    value={editingTx.category}
                    onChange={(e) => setEditingTx({ ...editingTx, category: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white text-xs outline-none focus:border-emerald-500"
                  >
                    {categories[editingTx.type].map((c) => (
                      <option key={c} value={c} className="dark:bg-[#0e111a]">
                        {c}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 font-mono">
                    Dompet *
                  </label>
                  <select
                    value={editingTx.wallet}
                    onChange={(e) => setEditingTx({ ...editingTx, wallet: e.target.value })}
                    className="w-full px-3 py-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white text-xs outline-none focus:border-emerald-500"
                  >
                    <option value="Kas Tunai" className="dark:bg-[#0e111a]">Kas Tunai</option>
                    <option value="Rekening Bank" className="dark:bg-[#0e111a]">Rekening Bank</option>
                    <option value="E-Wallet" className="dark:bg-[#0e111a]">E-Wallet</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 font-mono">
                  Tanggal *
                </label>
                <input
                  type="date"
                  required
                  value={editingTx.date}
                  onChange={(e) => setEditingTx({ ...editingTx, date: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white font-mono text-xs outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1.5 font-mono">
                  Deskripsi
                </label>
                <input
                  type="text"
                  value={editingTx.description || ''}
                  onChange={(e) => setEditingTx({ ...editingTx, description: e.target.value })}
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-white/[0.03] border border-slate-200 dark:border-white/10 text-slate-900 dark:text-white text-xs outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setIsEditModalOpen(false)}
                  className="px-4 py-2.5 rounded-xl border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 text-xs font-medium"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-white dark:text-black font-bold text-xs shadow-lg shadow-emerald-500/20"
                >
                  {submitting ? 'Memperbarui...' : 'Simpan Perubahan'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 3. CUSTOM MODAL: KONFIRMASI HAPUS */}
      {deleteCandidate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 dark:bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-sm bg-white dark:bg-[#0e111a] border border-slate-200 dark:border-white/10 rounded-3xl p-6 shadow-2xl text-center relative animate-in zoom-in-95 duration-200">
            <div className="w-12 h-12 rounded-2xl bg-rose-500/10 text-rose-500 flex items-center justify-center mx-auto mb-4">
              <Trash2 className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-900 dark:text-white mb-1">
              Hapus Transaksi Ini?
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-5">
              Tindakan ini tidak dapat dibatalkan. Transaksi sebesar{' '}
              <span className="font-mono font-bold text-slate-900 dark:text-white">{formatIDR(deleteCandidate.amount)}</span> ({deleteCandidate.category}) akan dihapus permanen.
            </p>
            <div className="flex items-center justify-center gap-3">
              <button
                type="button"
                onClick={() => setDeleteCandidate(null)}
                className="px-4 py-2.5 rounded-xl border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 text-xs font-medium"
              >
                Batal
              </button>
              <button
                type="button"
                onClick={handleDeleteConfirmed}
                disabled={deleting}
                className="px-5 py-2.5 rounded-xl bg-rose-500 hover:bg-rose-600 text-white font-bold text-xs shadow-lg shadow-rose-500/20"
              >
                {deleting ? 'Menghapus...' : 'Ya, Hapus'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
