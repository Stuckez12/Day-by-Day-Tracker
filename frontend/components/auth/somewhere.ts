import CredentialsProvider from "next-auth/providers/credentials";

import { personnelLoginQuery } from "@/lib/queries/auth";

import { PersonnelLogin } from "@/lib/interfaces/personnel";

export const authOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",

      credentials: {
        email: {},
        password: {},
      },

      async authorize(credentials) {
        const response = await personnelLoginQuery(
          credentials as PersonnelLogin,
        );

        if (!response.ok) {
          return null;
        }

        const data = await response.json();

        return {
          id: data.user.id,
          name: data.user.name,
          email: data.user.email,

          accessToken: data.accessToken,
          refreshToken: data.refreshToken,
        };
      },
    }),
  ],

  session: {
    strategy: "jwt",
  },

  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.accessToken;
        token.refreshToken = user.refreshToken;
      }

      return token;
    },

    async session({ session, token }) {
      session.accessToken = token.accessToken;

      return session;
    },
  },
};
