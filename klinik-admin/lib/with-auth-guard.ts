import type { GetServerSideProps, GetServerSidePropsContext, GetServerSidePropsResult } from "next";

import { fetchMe, type Me } from "@/lib/auth";

export type AuthedProps<P> = P & { me: Me };

/**
 * Wraps a page's getServerSideProps with the auth guard that used to live in
 * app/(app)/layout.tsx: redirects to /login if there's no session, otherwise
 * merges the current user into props alongside whatever getProps returns.
 */
export function withAuthGuard<P extends object = Record<string, never>>(
  getProps?: (ctx: GetServerSidePropsContext, me: Me) => Promise<GetServerSidePropsResult<P>>,
): GetServerSideProps<AuthedProps<P>> {
  return async (ctx) => {
    const me = await fetchMe(ctx.req);
    if (!me) {
      return { redirect: { destination: "/login", permanent: false } };
    }

    if (!getProps) {
      return { props: { me } as AuthedProps<P> };
    }

    const result = await getProps(ctx, me);
    if ("redirect" in result || "notFound" in result) {
      return result;
    }
    const props = await result.props;
    return { props: { ...props, me } };
  };
}
