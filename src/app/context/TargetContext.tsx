'use client';

import { createContext, useContext, useState } from 'react';
import { api } from '../services/api';

interface Target {
  id: string;
  name: string;
  description: string;
  imageUrl?: string;
  backendId?: string;
}

interface TargetContextType {
  targets: Target[];
  addTarget: (target: Target) => Promise<void>;
  deleteTarget: (id: string) => void;
  updateTarget: (id: string, updates: Partial<Target>) => void;
  searchTargets: (videoIds: string[], targetIds: string[]) => Promise<void>;
  getResults: (videoId: string, targetId: string) => Promise<void>;
  searchResults: { [key: string]: any };
}

const TargetContext = createContext<TargetContextType | undefined>(undefined);

export function TargetProvider({ children }: { children: React.ReactNode }) {
  const [targets, setTargets] = useState<Target[]>([]);
  const [searchResults, setSearchResults] = useState<{ [key: string]: any }>({});

  const addTarget = async (target: Target) => {
    try {
      // Add target to backend
      const type = target.imageUrl ? 'image' : 'text';
      const data = target.imageUrl || target.description;
      const result = await api.addTarget(type, data, target.name);

      // Add target to state with backend ID
      setTargets((prev) => [...prev, {
        ...target,
        backendId: result.target_id,
      }]);
    } catch (error) {
      console.error('Error adding target:', error);
      throw error;
    }
  };

  const deleteTarget = (id: string) => {
    setTargets((prev) => prev.filter((target) => target.id !== id));
  };

  const updateTarget = (id: string, updates: Partial<Target>) => {
    setTargets((prev) =>
      prev.map((target) =>
        target.id === id ? { ...target, ...updates } : target
      )
    );
  };

  const searchTargets = async (videoIds: string[], targetIds: string[]) => {
    try {
      const backendTargetIds = targets
        .filter((target) => targetIds.includes(target.id))
        .map((target) => target.backendId!)
        .filter(Boolean);

      if (backendTargetIds.length === 0) {
        console.warn('No valid backend target IDs found');
        return;
      }

      const results = await api.searchTargets(videoIds, backendTargetIds);
      setSearchResults(results);
    } catch (error) {
      console.error('Error searching targets:', error);
      throw error;
    }
  };

  const getResults = async (videoId: string, targetId: string) => {
    try {
      const target = targets.find((t) => t.id === targetId);
      if (!target?.backendId) {
        console.warn('No valid backend target ID found');
        return;
      }

      const results = await api.getResults(videoId, target.backendId);
      setSearchResults((prev) => ({
        ...prev,
        [`${videoId}_${targetId}`]: results,
      }));
    } catch (error) {
      console.error('Error getting results:', error);
      throw error;
    }
  };

  return (
    <TargetContext.Provider value={{ targets, addTarget, deleteTarget, updateTarget, searchTargets, getResults, searchResults }}>
      {children}
    </TargetContext.Provider>
  );
}

export function useTargetContext() {
  const context = useContext(TargetContext);
  if (context === undefined) {
    throw new Error('useTargetContext must be used within a TargetProvider');
  }
  return context;
} 