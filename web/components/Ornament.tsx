export function Ornament({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      width="48"
      height="24"
      viewBox="0 0 48 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d="M24 2c2.4 4.2 6.8 7 12 8-5.2 1-9.6 3.8-12 8-2.4-4.2-6.8-7-12-8 5.2-1 9.6-3.8 12-8Z"
        stroke="currentColor"
        strokeWidth="1.2"
      />
      <circle cx="24" cy="12" r="1.4" fill="currentColor" />
    </svg>
  );
}
