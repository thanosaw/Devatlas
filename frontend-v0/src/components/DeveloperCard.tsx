"use client";

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';

interface Developer {
  id: string;
  name: string;
  image: string;
  organization: string;
  team: string;
  manager: string;
  repos: string[];
  history: string;
  tech: string;
  connect: string;
}

interface DeveloperCardProps {
  developer: Developer;
  compact?: boolean;
}

export default function DeveloperCard({ developer, compact = false }: DeveloperCardProps) {
  const [imageError, setImageError] = useState(false);
  
  // Generate initials for fallback avatar
  const initials = developer.name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);
  
  // Handle image loading errors
  const handleImageError = () => {
    setImageError(true);
  };
  
  // Render avatar - either the image or a fallback with initials
  const renderAvatar = (size: number) => {
    if (imageError) {
      return (
        <div 
          className="rounded-full flex items-center justify-center text-white font-bold"
          style={{ 
            width: size, 
            height: size, 
            backgroundColor: getColorFromName(developer.name),
            fontSize: size / 2.5
          }}
        >
          {initials}
        </div>
      );
    }
    
    return (
      <Image 
        src={developer.image} 
        alt={developer.name}
        width={size}
        height={size}
        className="rounded-full"
        onError={handleImageError}
      />
    );
  };

  // Generate a consistent color based on name
  const getColorFromName = (name: string) => {
    const colors = ['#4285F4', '#EA4335', '#FBBC05', '#34A853', '#0F9D58', '#673AB7'];
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
      hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
  };

  if (compact) {
    return (
      <Link href={`/developer/${developer.id}`}>
        <div className="flex items-center p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
          <div className="h-12 w-12 relative mr-4">
            {renderAvatar(48)}
          </div>
          <div>
            <h3 className="font-semibold text-navy">{developer.name}</h3>
            <p className="text-sm text-gray-600">{developer.team} • {developer.organization}</p>
          </div>
        </div>
      </Link>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden shadow-sm">
      <div className="p-6">
        <div className="flex items-center mb-4">
          <div className="h-16 w-16 relative mr-4">
            {renderAvatar(64)}
          </div>
          <div>
            <h2 className="text-xl font-bold text-navy">{developer.name}</h2>
            <p className="text-gray-600">{developer.organization} • {developer.team}</p>
          </div>
        </div>
        
        <div className="space-y-3 mt-6">
          <div>
            <h3 className="text-sm font-semibold text-gray-500">Manager</h3>
            <p>{developer.manager}</p>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-500">Repositories</h3>
            <div className="flex flex-wrap gap-2 mt-1">
              {developer.repos.map((repo) => (
                <span key={repo} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                  {repo}
                </span>
              ))}
            </div>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-500">Recent Activity</h3>
            <p className="text-sm">{developer.history}</p>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-500">Tech Stack</h3>
            <p>{developer.tech}</p>
          </div>
          
          <div>
            <h3 className="text-sm font-semibold text-gray-500">Best Way to Connect</h3>
            <p className="text-sm">{developer.connect}</p>
          </div>
        </div>
      </div>
    </div>
  );
} 