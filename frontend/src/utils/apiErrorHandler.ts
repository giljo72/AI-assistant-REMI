import { AxiosError } from 'axios';

/**
 * Standard error message for API errors
 */
export interface ApiError {
  message: string;
  details?: string;
  statusCode?: number;
}

/**
 * Standardized error handler for API errors
 * @param error The error from the API call
 * @param defaultMessage Default message to show if error can't be parsed
 * @returns Standardized ApiError object
 */
export function handleApiError(error: unknown, defaultMessage = 'An error occurred'): ApiError {
  // Default error structure
  const apiError: ApiError = {
    message: defaultMessage,
  };

  // Handle axios errors
  if (error instanceof Error) {
    apiError.details = error.message;
    
    // Extract more info from Axios errors
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      apiError.statusCode = axiosError.response?.status;
      
      // Try to get the error from response data
      if (axiosError.response?.data) {
        const responseData = axiosError.response.data as any;
        
        // Check for standardized error format
        if (responseData.detail) {
          apiError.details = responseData.detail;
        } else if (responseData.message) {
          apiError.details = responseData.message;
        } else if (typeof responseData === 'string') {
          apiError.details = responseData;
        }
      }
      
      // Set specific messages for common status codes
      if (apiError.statusCode === 404) {
        apiError.message = 'Resource not found';
      } else if (apiError.statusCode === 401) {
        apiError.message = 'Unauthorized access';
      } else if (apiError.statusCode === 403) {
        apiError.message = 'Permission denied';
      } else if (apiError.statusCode === 400) {
        apiError.message = 'Invalid request format';
      } else if (apiError.statusCode === 500) {
        apiError.message = 'Server error';
      }
    }
  } else if (typeof error === 'string') {
    apiError.details = error;
  }
  
  // Log for debugging
  console.error('API Error:', apiError);
  
  return apiError;
}

// Re-export axios to avoid importing it again in consumer files
import axios from 'axios';
export { axios };