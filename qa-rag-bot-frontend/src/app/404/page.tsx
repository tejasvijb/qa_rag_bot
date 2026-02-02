'use client';

import Link from 'next/link';

export default function NotFoundPage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-linear-to-br from-slate-50 to-slate-100">
      <div className="text-center space-y-6 px-4">
        <div className="space-y-2">
          <h1 className="text-6xl font-bold text-slate-900">404</h1>
          <h2 className="text-2xl font-semibold text-slate-700">URL Not Found</h2>
        </div>

        <p className="text-slate-600 max-w-md mx-auto">
          The URL you&apos;re looking for doesn&apos;t exist .
          It may have been deleted or the link is incorrect.
        </p>

        <div className="space-y-3 pt-4">
          <Link
            href="/"
            className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go to Home
          </Link>
          <p className="text-sm text-slate-500">
            <Link href="/dashboard" className="text-blue-600 hover:underline">
              Back to Dashboard
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
