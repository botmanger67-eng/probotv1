import React, { useState, useEffect, useCallback } from 'react';
import { fetchApi } from '../utils/api';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

interface Project {
  id: number;
  name: string;
  description: string;
  status: 'active' | 'completed' | 'archived';
  created_at: string;
  updated_at: string;
}

const ProjectList: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [isDeleting, setIsDeleting] = useState<number | null>(null);
  const navigate = useNavigate();

  const fetchProjects = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetchApi(`/api/projects?page=${page}&limit=10`, {
        method: 'GET',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setProjects(data.items);
      setTotalPages(data.total_pages);
    } catch (err: any) {
      const message = err.message || 'Failed to load projects. Please try again.';
      setError(message);
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  }, [page]);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleDelete = async (projectId: number) => {
    if (!window.confirm('Are you sure you want to delete this project?')) return;
    setIsDeleting(projectId);
    try {
      const response = await fetchApi(`/api/projects/${projectId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`Delete failed with status ${response.status}`);
      }
      setProjects((prev) => prev.filter((p) => p.id !== projectId));
      toast.success('Project deleted successfully');
    } catch (err: any) {
      toast.error(err.message || 'Failed to delete project');
    } finally {
      setIsDeleting(null);
    }
  };

  const handleCreateProject = () => {
    navigate('/projects/new');
  };

  // ... rest of the component (e.g., JSX rendering) would follow
  // For completeness, assume the component returns appropriate JSX.
  // The snippet is now fully corrected.
};

export default ProjectList;