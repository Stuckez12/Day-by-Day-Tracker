"use client";

import LoginForm from "@/components/auth/loginForm";
import PageWrapper from "@/components/common/PageWrapper";
import "@/styles/common/form.scss";

export default function LoginPage() {
  return (
    <PageWrapper>
      <LoginForm />
    </PageWrapper>
  );
}
