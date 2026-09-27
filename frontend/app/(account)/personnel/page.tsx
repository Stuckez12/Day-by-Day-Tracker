import Logout from "@/components/auth/Logout";
import PageWrapper from "@/components/common/PageWrapper";
import UpdateEmailForm from "@/components/personnel/UpdateEmailForm";
import UpdateInfoForm from "@/components/personnel/UpdateInfoForm";
import UpdatePasswordForm from "@/components/personnel/UpdatePasswordForm";

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
