// Most pages are now implemented individually
// This file is kept for the 404 page only

export function NotFound() {
  return (
    <div className="text-center py-12">
      <h2 className="text-2xl font-bold text-gray-900">404 - Page Not Found</h2>
      <p className="text-gray-500 mt-2">The page you're looking for doesn't exist.</p>
      <a href="/dashboard" className="mt-4 inline-block btn btn-primary">
        Go to Dashboard
      </a>
    </div>
  );
}