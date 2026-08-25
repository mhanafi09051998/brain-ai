import { NextResponse } from 'next/server';
import { getAuthUserFromHeader } from '@/lib/auth';

export const dynamic = 'force-dynamic';

export async function GET(request) {
  const authHeader = request.headers.get('authorization');
  const user = getAuthUserFromHeader(authHeader);

  if (!user) {
    return NextResponse.json({ success: false, error: 'Unauthorized' }, { status: 401 });
  }

  return NextResponse.json({
    success: true,
    user: { id: user.id, name: user.name, email: user.email }
  });
}
