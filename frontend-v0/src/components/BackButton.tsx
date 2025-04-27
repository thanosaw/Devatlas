"use client";

import { useRouter } from 'next/navigation';

interface BackButtonProps {
  destination: string;
  label: string;
  className?: string;
}

export default function BackButton({ destination, label, className = "" }: BackButtonProps) {
  const router = useRouter();

  const handleClick = () => {
    try {
      if (destination === '/') {
        // Force a full page navigation for home route to avoid any potential caching or client-side routing issues
        window.location.href = '/';
      } else {
        router.push(destination);
      }
    } catch (error) {
      console.error("Navigation error:", error);
      // Fallback to direct URL navigation if router fails
      window.location.href = destination;
    }
  };

  return (
    <button
      onClick={handleClick}
      className={`text-blue-600 hover:underline flex items-center ${className}`}
      aria-label={label}
    >
      <span className="mr-1">←</span> {label}
    </button>
  );
} 