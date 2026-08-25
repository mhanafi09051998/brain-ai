import { NextResponse } from 'next/server';
import { getMovieBySlug } from '@/lib/movies';

export const dynamic = 'force-dynamic';

export async function GET(request, { params }) {
  const { slug } = params;
  const movie = getMovieBySlug(slug);
  if (!movie) {
    return NextResponse.json({ success: false, error: 'Film tidak ditemukan' }, { status: 404 });
  }
  return NextResponse.json({ success: true, data: movie });
}
