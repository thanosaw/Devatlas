"use client";

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { fetchDeveloperById } from '@/lib/api';
import DeveloperCard from '@/components/DeveloperCard';
import BackButton from '@/components/BackButton';

export default function DeveloperProfilePage() {
  const params = useParams();
  const [developer, setDeveloper] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDeveloper() {
      try {
        setLoading(true);
        const id = params.id as string;
        const data = await fetchDeveloperById(id);
        
        if (!data) {
          setError('Developer not found');
          return;
        }
        
        setDeveloper(data);
      } catch (err) {
        setError('Failed to load developer profile');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    if (params.id) {
      loadDeveloper();
    }
  }, [params.id]);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6 flex space-x-4">
        <BackButton destination="/developers" label="Back to all developers" />
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
      ) : developer ? (
        <div className="max-w-2xl mx-auto">
          <DeveloperCard developer={developer} />
          
          <div className="mt-8 border-t pt-6">
            <h2 className="text-xl font-bold text-navy mb-4">Team Members</h2>
            <p className="text-gray-600">Other members in the {developer.team} team will be shown here.</p>
          </div>
          
          <div className="mt-8 border-t pt-6">
            <h2 className="text-xl font-bold text-navy mb-4">Repository Activity</h2>
            <div className="space-y-3">
              {developer.repos.map((repo: string) => (
                <div key={repo} className="border p-4 rounded-lg">
                  <h3 className="font-semibold">{repo}</h3>
                  <p className="text-sm text-gray-600">Recent commits and PR activity will be shown here.</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-500">Developer not found</p>
        </div>
      )}
    </div>
  );
} 