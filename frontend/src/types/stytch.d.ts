declare module '@stytch/react' {
  export interface StytchClient {
    oauth: {
      google: {
        start: (options: {
          login_redirect_url: string;
          signup_redirect_url: string;
        }) => Promise<void>;
      };
      authenticate: (token: string, options: {
        session_duration_minutes: number;
      }) => Promise<void>;
    };
    session: {
      revoke: () => Promise<void>;
    };
  }

  export function useStytch(): StytchClient;
  export function StytchProvider(props: { children: React.ReactNode; stytch: any }): JSX.Element;
  export function StytchHeadlessClient(publicToken: string): StytchClient;
}

declare module '@stytch/vanilla-js' {
  export class StytchUIClient {
    constructor(publicToken: string, options?: {
      cookieOptions?: {
        opaqueTokenCookieName?: string;
        jwtCookieName?: string;
        path?: string;
        availableToSubdomains?: boolean;
        domain?: string;
      }
    });
  }
}
