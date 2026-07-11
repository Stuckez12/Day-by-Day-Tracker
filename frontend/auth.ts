import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import { personnelLoginQuery } from "@/lib/queries/auth";
import { PersonnelLogin } from "@/lib/interfaces/personnel";


export const { handlers, signIn, signOut, auth } = NextAuth({
    providers : [
        CredentialsProvider({
      id: "password-login",
      name: "Email & Password Login",
      credentials: {
        email: {},
        password: {},
      }, 
    
      authorize: async (credentials) => {
        const response = await personnelLoginQuery(credentials as PersonnelLogin);

        if (!response.ok) {
          return null;
        }

        return null
      },
    ),
    ]
})