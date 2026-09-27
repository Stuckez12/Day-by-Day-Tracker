import LoginForm from "@/components/auth/loginForm";
import PageWrapper from "@/components/common/PageWrapper";

export default function LoginPage() {
  const isTestProd = process.env.IS_TEST_PROD === "true";

  return (
    <PageWrapper>
      <LoginForm isTestProd={isTestProd} />
    </PageWrapper>
  );
}
