import type { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

import { personnelLoginQuery } from "@/lib/queries/auth";

export const authOptions: NextAuthOptions = {
  secret: process.env.NEXTAUTH_SECRET ?? process.env.AUTH_SECRET,
  pages: {
    signIn: "/login",
  },
  session: {
    strategy: "jwt",
  },
  providers: [
    CredentialsProvider({
      id: "credentials",
      name: "Email and password",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials.password) {
          return null;
        }

        const result = await personnelLoginQuery({
          email: credentials.email,
          password: credentials.password,
        });

        if (!result.ok) {
          return null;
        }

        const { personnel, access_token: accessToken } = result.data;

        return {
          id: personnel.id,
          email: personnel.email,
          name: `${personnel.first_name} ${personnel.last_name}`.trim(),
          accessToken,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.personnelId = user.id;
        token.accessToken = user.accessToken;
      }

      return token;
    },
    async session({ session, token }) {
      if (session.user && token.personnelId) {
        session.user.id = token.personnelId as string;
      }

      session.accessToken = token.accessToken;

      return session;
    },
  },
};
