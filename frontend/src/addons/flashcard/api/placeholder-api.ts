// Placeholder API until external dependencies are available
// This file provides mock implementations for tRPC and external APIs

// Placeholder types
interface MutationOptions<T = unknown> {
  onSuccess?: (data?: T) => void;
  onError?: (error?: unknown) => void;
}

interface StudySetData {
  id?: string;
  title?: string;
  description?: string;
  flashcards?: Array<{ id: string; term: string; definition: string }>;
}

interface QueryParams {
  id?: string;
}

interface CombineData {
  id?: string;
  studySetIds?: string[];
  studySets?: string[];
  title?: string;
}

export const api = {
  studySet: {
    delete: {
      useMutation: (options?: MutationOptions<void>) => ({
        mutate: async (id: { id: string }) => {
          console.log('Delete study set:', id);
          options?.onSuccess?.();
          return Promise.resolve();
        },
        mutateAsync: async (id: { id: string }) => {
          console.log('Delete study set:', id);
          options?.onSuccess?.();
          return Promise.resolve();
        },
        isPending: false
      })
    },
    update: {
      useMutation: (options?: MutationOptions<StudySetData>) => ({
        mutate: async (data: StudySetData) => {
          console.log('Update study set:', data);
          options?.onSuccess?.();
          return Promise.resolve(data);
        },
        mutateAsync: async (data: StudySetData) => {
          console.log('Update study set:', data);
          options?.onSuccess?.();
          return Promise.resolve(data);
        },
        isPending: false
      })
    },
    create: {
      useMutation: (options?: MutationOptions<StudySetData>) => ({
        mutate: async (data: StudySetData) => {
          console.log('Create study set:', data);
          options?.onSuccess?.();
          return Promise.resolve({ ...data, id: Math.random().toString() });
        },
        mutateAsync: async (data: StudySetData) => {
          console.log('Create study set:', data);
          options?.onSuccess?.();
          return Promise.resolve({ ...data, id: Math.random().toString() });
        },
        isPending: false
      })
    },
    byId: {
      useQuery: (query: QueryParams, options?: { initialData?: unknown }) => ({
        data: query?.id ? {
          id: query.id,
          title: `Study Set ${query.id}`,
          description: `Description for study set ${query.id}`,
          user: { id: '1', name: 'Test User', image: null },
          flashcards: [
            { id: '1', term: 'Sample Term 1', definition: 'Sample Definition 1' },
            { id: '2', term: 'Sample Term 2', definition: 'Sample Definition 2' }
          ]
        } : options?.initialData || null,
        isLoading: false,
        error: null
      })
    },
    allByUser: {
      useQuery: (params?: { userId?: string }) => ({
        data: [
          { id: '1', title: 'Study Set 1' },
          { id: '2', title: 'Study Set 2' }
        ],
        isLoading: false,
        error: null
      })
    },
    getById: {
      useQuery: (id: string) => ({
        data: id ? {
          id,
          title: `Study Set ${id}`,
          description: `Description for study set ${id}`,
          user: { id: '1', name: 'Test User', image: null },
          flashcards: [
            { id: '1', term: 'Sample Term 1', definition: 'Sample Definition 1' },
            { id: '2', term: 'Sample Term 2', definition: 'Sample Definition 2' }
          ]
        } : null,
        isLoading: false,
        error: null
      })
    },
    combine: {
      useMutation: (options?: MutationOptions<{ id: string; title: string }>) => ({
        mutate: async (data: CombineData) => {
          console.log('Combine study sets:', data);
          const combinedSet = { id: Math.random().toString(), title: 'Combined Study Set' };
          options?.onSuccess?.(combinedSet);
          return Promise.resolve(combinedSet);
        },
        mutateAsync: async (data: CombineData) => {
          console.log('Combine study sets:', data);
          const combinedSet = { id: Math.random().toString(), title: 'Combined Study Set' };
          options?.onSuccess?.(combinedSet);
          return Promise.resolve(combinedSet);
        },
        isPending: false
      })
    }
  },
  useUtils: () => ({
    studySet: {
      invalidate: () => Promise.resolve(),
      byId: {
        getData: (params: QueryParams) => ({
          id: params.id,
          title: `Study Set ${params.id}`,
          description: `Description for study set ${params.id}`,
          user: { id: '1', name: 'Test User', image: null },
          flashcards: [
            { id: '1', term: 'Sample Term 1', definition: 'Sample Definition 1' },
            { id: '2', term: 'Sample Term 2', definition: 'Sample Definition 2' }
          ]
        })
      }
    }
  })
};

// Placeholder types
export type RouterOutputs = {
  studySet: {
    byId: {
      user: {
        id: string;
        name: string | null;
        image: string | null;
      } | null;
    };
  };
};