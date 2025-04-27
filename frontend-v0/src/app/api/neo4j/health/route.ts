import { NextResponse } from 'next/server';
import { testNeo4jConnection } from '@/lib/neo4j';

export async function GET() {
  try {
    const result = await testNeo4jConnection();
    
    if (result.success) {
      return NextResponse.json(result, { status: 200 });
    } else {
      return NextResponse.json(result, { status: 500 });
    }
  } catch (error: any) {
    return NextResponse.json(
      { 
        success: false, 
        message: `Error checking Neo4j health: ${error.message}` 
      }, 
      { status: 500 }
    );
  }
} 