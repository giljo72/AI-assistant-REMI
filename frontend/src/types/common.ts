/**
 * Common type definitions for the application
 * This file provides shared types to ensure consistency across components
 */

// Type definition for Project ID
export type ProjectId = string | null;

// Type guard to check if a value is a valid ProjectId
export function isValidProjectId(value: unknown): value is ProjectId {
  // A valid project ID is either a non-empty string or null
  return value === null || (typeof value === 'string' && value.length > 0);
}

// Helper function to normalize project ID values
export function normalizeProjectId(value: unknown): ProjectId {
  if (value === null || value === undefined || value === '') {
    return null;
  }
  
  if (typeof value === 'string') {
    return value;
  }
  
  // Handle 'null' string case
  if (value === 'null') {
    return null;
  }
  
  // For object type nulls (caused by JSON parsing)
  if (value && typeof value === 'object') {
    return null;
  }
  
  // Default fallback
  console.warn(`Unexpected project ID value type: ${typeof value}, value:`, value);
  return null;
}

// Robust function to check if a file is linked to a project
export function isFileLinkedToProject(fileProjectId: unknown): boolean {
  const normalizedId = normalizeProjectId(fileProjectId);
  return normalizedId !== null;
}

// Function to safely compare project IDs
export function areProjectIdsEqual(id1: unknown, id2: unknown): boolean {
  const normalizedId1 = normalizeProjectId(id1);
  const normalizedId2 = normalizeProjectId(id2);
  
  return normalizedId1 === normalizedId2;
}