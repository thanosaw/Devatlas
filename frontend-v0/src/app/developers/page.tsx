"use client";

import { useState, useEffect } from 'react';
import { fetchAllDevelopers, searchDevelopers } from '@/lib/api';
import DeveloperCard from '@/components/DeveloperCard';
import BackButton from '@/components/BackButton';

export default function DevelopersPage() {
  const [developers, setDevelopers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDevelopers() {
      try {
        setLoading(true);
        const data = await fetchAllDevelopers();
        setDevelopers(data);
      } catch (err) {
        setError('Failed to load developers');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    loadDevelopers();
  }, []);

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.trim() === '') {
      const allDevs = await fetchAllDevelopers();
      setDevelopers(allDevs);
      return;
    }

    const results = await searchDevelopers(query);
    setDevelopers(results);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-navy">Developers</h1>
      </div>
      
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search by name, team, tech..."
          className="w-full p-3 border rounded-lg"
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-[60vh]">
          <div 
            className="animate-pulse"
            style={{
              borderRadius: "100px",
              background: "#EFEFEF",
              width: "300px",
              height: "10px"
            }}
          ></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 text-red-700 p-4 rounded-lg">{error}</div>
      ) : developers.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No developers found</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {developers.map((developer: any) => (
            <DeveloperCard key={developer.id} developer={developer} compact={true} />
          ))}
        </div>
      )}
    </div>
  );
} 