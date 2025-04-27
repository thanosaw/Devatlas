'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="bg-white shadow py-4 px-6">
      <div className="container mx-auto flex items-center justify-between">
        <Link href="/" className="text-xl font-bold text-blue-600">
          DevAtlas
        </Link>
        
        <div className="flex space-x-6">
          <Link 
            href="/" 
            className={`${pathname === '/' ? 'text-blue-600 font-semibold' : 'text-gray-600 hover:text-blue-600'} transition-colors`}
          >
            Home
          </Link>
          <Link 
            href="/slacks" 
            className={`${pathname === '/slacks' ? 'text-blue-600 font-semibold' : 'text-gray-600 hover:text-blue-600'} transition-colors`}
          >
            Slack Messages
          </Link>
        </div>
      </div>
    </nav>
  );
} 