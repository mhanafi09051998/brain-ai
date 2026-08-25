import { getMovieBySlug } from '@/lib/movies';
import VideoPlayer from '@/components/VideoPlayer';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

export async function generateMetadata({ params }) {
  const movie = getMovieBySlug(params.slug);
  if (!movie) return { title: 'Film Tidak Ditemukan - Goblix' };
  return {
    title: `Nonton ${movie.title} Subtitle Indonesia - Goblix`,
    description: movie.synopsis
  };
}

export default async function WatchPage({ params }) {
  const { slug } = params;
  const movie = getMovieBySlug(slug);

  if (!movie) {
    return (
      <div className="w-screen h-screen bg-[#141414] text-white flex flex-col items-center justify-center space-y-4 p-6 text-center">
        <i className="fa-solid fa-triangle-exclamation text-red-600 text-5xl"></i>
        <h1 className="text-2xl font-bold">Film Tidak Ditemukan</h1>
        <p className="text-gray-400 text-sm max-w-md">
          Maaf, film yang Anda cari tidak tersedia dalam katalog kami.
        </p>
        <Link href="/" className="bg-red-600 hover:bg-red-700 text-white font-bold px-6 py-2.5 rounded text-sm transition">
          Kembali ke Beranda
        </Link>
      </div>
    );
  }

  return <VideoPlayer movie={movie} />;
}
