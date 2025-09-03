import { NextRequest, NextResponse } from 'next/server';
import { apiKeyManager } from './lib/api-key-client';

// Routes that require API key validation
const PROTECTED_ROUTES = ['/api/generate'];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if this is a protected route
  const isProtectedRoute = PROTECTED_ROUTES.some(route => pathname.startsWith(route));
  
  if (!isProtectedRoute) {
    return NextResponse.next();
  }

  // Extract API key from headers
  const apiKey = request.headers.get('x-api-key') || 
                 request.headers.get('authorization')?.replace('Bearer ', '') ||
                 request.nextUrl.searchParams.get('api_key');

  if (!apiKey) {
    return new NextResponse(
      JSON.stringify({ 
        error: 'API key required',
        message: 'Please provide a valid API key in the x-api-key header, Authorization header, or api_key query parameter.' 
      }),
      { 
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }

  try {
    // Validate the API key against the API Key Manager
    const validation = await apiKeyManager.validateAPIKey(apiKey);
    
    if (!validation.valid) {
      return new NextResponse(
        JSON.stringify({ 
          error: 'Invalid API key',
          message: validation.message 
        }),
        { 
          status: 403,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }

    // API key is valid, add user info to headers for downstream use
    const response = NextResponse.next();
    
    if (validation.key_info) {
      response.headers.set('x-user-email', validation.key_info.user_email);
      response.headers.set('x-user-org', validation.key_info.organization || '');
      response.headers.set('x-quota-remaining', String(validation.remaining_quota || 0));
      response.headers.set('x-rate-limit-remaining', String(validation.rate_limit_remaining || 0));
    }

    return response;

  } catch (error) {
    console.error('Error validating API key:', error);
    
    return new NextResponse(
      JSON.stringify({ 
        error: 'Validation service unavailable',
        message: 'Unable to validate API key. Please try again later.' 
      }),
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Configure which paths the middleware runs on
export const config = {
  matcher: [
    // Match all API routes except Next.js internals
    '/api/:path*',
    // You can add more patterns here as needed
  ]
};
