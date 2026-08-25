import { NextResponse } from 'next/server';
import { getUsersDB, saveUsersDB, hashPassword, generateToken } from '@/lib/auth';

export const dynamic = 'force-dynamic';

export async function POST(request) {
  try {
    const { name, email, password } = await request.json();
    if (!name || !email || !password) {
      return NextResponse.json({ success: false, error: 'Semua kolom wajib diisi' }, { status: 400 });
    }
    if (password.length < 6) {
      return NextResponse.json({ success: false, error: 'Kata sandi minimal 6 karakter' }, { status: 400 });
    }

    const users = getUsersDB();
    const cleanEmail = email.toLowerCase().trim();
    if (users.some(u => (u.email || '').toLowerCase() === cleanEmail)) {
      return NextResponse.json({ success: false, error: 'Email sudah terdaftar' }, { status: 400 });
    }

    const newUser = {
      id: 'usr_' + Date.now().toString(36),
      name: name.trim(),
      email: cleanEmail,
      passwordHash: hashPassword(password),
      role: 'member',
      createdAt: new Date().toISOString()
    };

    users.push(newUser);
    saveUsersDB(users);

    const token = generateToken(newUser);
    return NextResponse.json({
      success: true,
      token,
      user: { id: newUser.id, name: newUser.name, email: newUser.email }
    });
  } catch (e) {
    return NextResponse.json({ success: false, error: 'Gagal membuat akun' }, { status: 500 });
  }
}
