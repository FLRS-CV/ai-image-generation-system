import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Extract user info from headers (set by middleware)
    const userEmail = request.headers.get('x-user-email');
    const quotaRemaining = request.headers.get('x-quota-remaining');
    
    // Get the form data from the request
    const formData = await request.formData();
    
    // Forward the request to the Flask backend
    const backendUrl = process.env.FLASK_BACKEND_URL || 'http://localhost:5000/generate';
    
    // Create a new FormData object to forward to Flask
    const forwardFormData = new FormData();
    
    // Copy all form fields to the new FormData
    for (const [key, value] of formData.entries()) {
      forwardFormData.append(key, value);
    }
    
    // Make request to Flask backend
    // this goes to flask backend
    const flaskResponse = await fetch(backendUrl, {
      method: 'POST',
      body: forwardFormData,
    });
    
    if (!flaskResponse.ok) {
      const errorData = await flaskResponse.json().catch(() => ({}));
      throw new Error(errorData.error || `Flask backend error: ${flaskResponse.status}`);
    }
    
    const result = await flaskResponse.json();
    
    // Add user context to response
    return NextResponse.json({
      ...result,
      user_info: {
        email: userEmail,
        quota_remaining: quotaRemaining,
      }
    });
    
  } catch (error: any) {
    console.error('API route error:', error);
    
    return NextResponse.json(
      { 
        error: 'Image generation failed',
        message: error.message || 'Unknown error occurred'
      },
      { status: 500 }
    );
  }
}
