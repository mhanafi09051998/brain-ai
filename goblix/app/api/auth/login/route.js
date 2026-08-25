import { NextResponse } from 'next/server';
import { getUsersDB, hashPassword, generateToken } from '@/lib/auth';

export const dynamic = 'force-dynamic';

export async function POST(request) {
  try {
    const { email, password } = await request.json();
    if (!email || !password) {
      return NextResponse.json({ success: false, error: 'Email dan kata sandi wajib diisi' }, { status: 400 });
    }

    const users = getUsersDB();
    const user = users.find(u => (u.email || '').toLowerCase() === email.toLowerCase().trim());
    if (!user || user.passwordHash !== hashPassword(password)) {
      return NextResponse.json({ success: false, error: 'Email atau kata sandi salah' }, { status: 401 });
    }

    const token = generateToken(user);
    return NextResponse.json({
      success: true,
      token,
      user: { id: user.id, name: user.name, email: user.email }
    });
  } catch (e) {
    return NextResponse.json({ success: false, error: 'Terjadi kesalahan server' }, { status: 500 });
  }
}
