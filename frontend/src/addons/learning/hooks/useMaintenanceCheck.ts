import { useMemo } from 'react';
import { isMaintenanceError, isEmptyContent, getContentTypeName } from '../utils/contentValidation';

interface MaintenanceCheckResult {
  isMaintenance: boolean;
  contentTypeName: string;
  shouldShowMaintenance: boolean;
}

interface UseMaintenanceCheckOptions {
  error?: any;
  data?: any;
  contentType: string;
  forceCheck?: boolean;
}

/**
 * Custom hook to check if content should show maintenance message
 * @param options - Configuration options
 * @returns Object with maintenance status and helper information
 */
export function useMaintenanceCheck({
  error,
  data,
  contentType,
  forceCheck = false
}: UseMaintenanceCheckOptions): MaintenanceCheckResult {
  
  return useMemo(() => {
    const contentTypeName = getContentTypeName(contentType);
    
    // If force check is enabled, always show maintenance
    if (forceCheck) {
      return {
        isMaintenance: true,
        contentTypeName,
        shouldShowMaintenance: true
      };
    }
    
    // Check if there's an explicit maintenance error
    const hasMaintenanceError = error && isMaintenanceError(error);
    
    // Only check for empty content if there's no error and data exists
    // This prevents false positives when data is loading or valid
    const hasEmptyContent = !error && data && isEmptyContent(data);
    
    const isMaintenance = hasMaintenanceError || hasEmptyContent;
    
    return {
      isMaintenance,
      contentTypeName,
      shouldShowMaintenance: isMaintenance
    };
  }, [error, data, contentType, forceCheck]);
}

export default useMaintenanceCheck;