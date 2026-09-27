import { useRouter } from "next/navigation";
import { signIn } from "next-auth/react";
import { useState } from "react";

import Button from "@/components/common/buttons/Button";

export default function TestUserLoginButton() {
  const router = useRouter();

  const [isLoading, setIsLoading] = useState<boolean>(false);

  async function submitForm() {
    setIsLoading(true);

    const result = await signIn("test-user-login", {
      redirect: false,
    });

    if (result?.ok) {
      router.replace("/tracker");
      return;
    }

    setIsLoading(false);
  }

  return (
    <Button loading={isLoading} onClick={submitForm}>
      Login As Test User
    </Button>
  );
}
