import Logout from "@/components/auth/Logout";
import UpdateEmailForm from "@/components/personnel/UpdateEmailForm";
import UpdateInfoForm from "@/components/personnel/UpdateInfoForm";
import UpdatePasswordForm from "@/components/personnel/UpdatePasswordForm";
import PageWrapper from "@/components/common/PageWrapper";

export default function PersonnelPage() {
  return (
    <PageWrapper>
      <UpdateInfoForm />
      <UpdateEmailForm />
      <UpdatePasswordForm />
      <Logout />
    </PageWrapper>
  );
}
