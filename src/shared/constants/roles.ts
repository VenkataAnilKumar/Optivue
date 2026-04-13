export const COGNITO_GROUPS = [
  "finops-analyst",
  "engineering-manager",
  "finance",
  "leadership",
] as const;

export type CognitoGroup = (typeof COGNITO_GROUPS)[number];

export const ROLE_PERMISSIONS: Record<CognitoGroup, {
  canApprove: boolean;
  canExecute: boolean;
  canViewAllRecommendations: boolean;
  canViewAccountNumbers: boolean;
  isReadOnly: boolean;
}> = {
  "finops-analyst": {
    canApprove: true,
    canExecute: true,
    canViewAllRecommendations: true,
    canViewAccountNumbers: true,
    isReadOnly: false,
  },
  "engineering-manager": {
    canApprove: true,
    canExecute: true,
    canViewAllRecommendations: false,
    canViewAccountNumbers: true,
    isReadOnly: false,
  },
  finance: {
    canApprove: false,
    canExecute: false,
    canViewAllRecommendations: true,
    canViewAccountNumbers: false,
    isReadOnly: true,
  },
  leadership: {
    canApprove: false,
    canExecute: false,
    canViewAllRecommendations: true,
    canViewAccountNumbers: false,
    isReadOnly: true,
  },
};
