'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

// Mock data for class information
const mockClassData = {
  title: 'Introduction to Computer Science',
  code: 'CS101',
  instructor: 'Dr. Jane Smith',
  schedule: 'Mon, Wed, Fri 10:00 AM - 11:30 AM',
  location: 'Building A, Room 203',
  description: 'An introductory course covering the fundamentals of computer science, algorithms, and programming.',
  announcements: [
    { id: 1, date: '2023-05-01', title: 'Midterm Exam Date', content: 'The midterm exam will be held on May 15th.' },
    { id: 2, date: '2023-04-25', title: 'Assignment 3 Due Date Extended', content: 'The due date for Assignment 3 has been extended to May 5th.' },
  ],
  assignments: [
    { id: 1, title: 'Programming Assignment 1', dueDate: '2023-05-10', status: 'Pending' },
    { id: 2, title: 'Programming Assignment 2', dueDate: '2023-05-20', status: 'Not Started' },
    { id: 3, title: 'Final Project Proposal', dueDate: '2023-05-15', status: 'Completed' },
  ],
  grades: [
    { id: 1, title: 'Quiz 1', score: 85, maxScore: 100 },
    { id: 2, title: 'Programming Assignment 1', score: 92, maxScore: 100 },
    { id: 3, title: 'Midterm Exam', score: 78, maxScore: 100 },
  ]
};

export default function ClassDashboard() {
  const [classData, setClassData] = useState(mockClassData);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // This would be replaced with an actual API call in a real application
    const fetchData = async () => {
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));
        setClassData(mockClassData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching class data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading class dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white shadow-sm rounded-lg p-6 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{classData.title}</h1>
              <p className="text-gray-500 mt-1">{classData.code}</p>
            </div>
            <div className="mt-4 md:mt-0">
              <Link href="/class" className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
                Back to Classes
              </Link>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            <div className="border-t border-gray-200 pt-4">
              <p className="text-sm font-medium text-gray-500">Instructor</p>
              <p className="mt-1">{classData.instructor}</p>
            </div>
            <div className="border-t border-gray-200 pt-4">
              <p className="text-sm font-medium text-gray-500">Schedule</p>
              <p className="mt-1">{classData.schedule}</p>
            </div>
            <div className="border-t border-gray-200 pt-4">
              <p className="text-sm font-medium text-gray-500">Location</p>
              <p className="mt-1">{classData.location}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Announcements */}
          <div className="bg-white shadow-sm rounded-lg p-6 col-span-1 lg:col-span-2">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Announcements</h2>
            {classData.announcements.length > 0 ? (
              <div className="space-y-4">
                {classData.announcements.map((announcement) => (
                  <div key={announcement.id} className="border-b border-gray-200 pb-4">
                    <div className="flex justify-between items-start">
                      <h3 className="text-lg font-medium text-gray-900">{announcement.title}</h3>
                      <span className="text-sm text-gray-500">{announcement.date}</span>
                    </div>
                    <p className="mt-2 text-gray-600">{announcement.content}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No announcements at this time.</p>
            )}
          </div>

          {/* Course Info */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Course Information</h2>
            <p className="text-gray-600">{classData.description}</p>
            
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Resources</h3>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-blue-600 hover:underline">Syllabus</a>
                </li>
                <li>
                  <a href="#" className="text-blue-600 hover:underline">Course Schedule</a>
                </li>
                <li>
                  <a href="#" className="text-blue-600 hover:underline">Office Hours</a>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          {/* Assignments */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Assignments</h2>
            {classData.assignments.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead>
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assignment</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {classData.assignments.map((assignment) => (
                      <tr key={assignment.id}>
                        <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-blue-600 hover:underline">
                          <a href="#">{assignment.title}</a>
                        </td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">{assignment.dueDate}</td>
                        <td className="px-4 py-4 whitespace-nowrap text-sm">
                          <span className={`px-2 py-1 text-xs rounded-full ${
                            assignment.status === 'Completed' 
                              ? 'bg-green-100 text-green-800' 
                              : assignment.status === 'Pending' 
                                ? 'bg-yellow-100 text-yellow-800' 
                                : 'bg-gray-100 text-gray-800'
                          }`}>
                            {assignment.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-500">No assignments at this time.</p>
            )}
          </div>

          {/* Grades */}
          <div className="bg-white shadow-sm rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Grades</h2>
            {classData.grades.length > 0 ? (
              <div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead>
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assessment</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {classData.grades.map((grade) => (
                        <tr key={grade.id}>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">{grade.title}</td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                            {grade.score}/{grade.maxScore} ({Math.round((grade.score / grade.maxScore) * 100)}%)
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="mt-4 p-4 bg-gray-50 rounded-md">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-500">Overall Grade</span>
                    <span className="text-lg font-semibold text-gray-900">
                      {Math.round(
                        classData.grades.reduce((acc, grade) => acc + (grade.score / grade.maxScore), 0) / 
                        classData.grades.length * 100
                      )}%
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No grades available.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 