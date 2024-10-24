import { useMutation, useQueryClient } from '@tanstack/react-query';

import { APIError, errorCauses, fetchAPI } from '@/api';
import { User } from '@/core/auth';
import {
  Access,
  Doc,
  KEY_LIST_DOC,
  Role,
} from '@/features/docs/doc-management';
import { KEY_LIST_DOC_ACCESSES } from '@/features/docs/members/members-list';
import { ContentLanguage } from '@/i18n/types';

import { OptionType } from '../types';

import { KEY_LIST_USER } from './useUsers';

interface CreateDocAccessParams {
  role: Role;
  docId: Doc['id'];
  memberId: User['id'];
  contentLanguage: ContentLanguage;
}

export const createDocAccess = async ({
  memberId,
  role,
  docId,
  contentLanguage,
}: CreateDocAccessParams): Promise<Access> => {
  const response = await fetchAPI(`documents/${docId}/accesses/`, {
    method: 'POST',
    headers: {
      'Content-Language': contentLanguage,
    },
    body: JSON.stringify({
      user_id: memberId,
      role,
    }),
  });

  if (!response.ok) {
    throw new APIError(
      `Failed to add the member in the doc.`,
      await errorCauses(response, {
        type: OptionType.NEW_MEMBER,
      }),
    );
  }

  return response.json() as Promise<Access>;
};

export function useCreateDocAccess() {
  const queryClient = useQueryClient();
  return useMutation<Access, APIError, CreateDocAccessParams>({
    mutationFn: createDocAccess,
    onSuccess: () => {
      void queryClient.resetQueries({
        queryKey: [KEY_LIST_DOC],
      });
      void queryClient.resetQueries({
        queryKey: [KEY_LIST_USER],
      });
      void queryClient.resetQueries({
        queryKey: [KEY_LIST_DOC_ACCESSES],
      });
    },
  });
}
