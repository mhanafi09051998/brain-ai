import { NextResponse } from 'next/server';
import { getAllMovies } from '@/lib/movies';

export const dynamic = 'force-dynamic';

export async function GET() {
  const movies = getAllMovies();
  return NextResponse.json({ success: true, data: movies }, {
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate'
    }
  });
}
