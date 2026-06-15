import Logout from "@/components/auth/Logout";
import UpdateEmailForm from "@/components/personnel/UpdateEmailForm";
import UpdateInfoForm from "@/components/personnel/UpdateInfoForm";
import UpdatePasswordForm from "@/components/personnel/UpdatePasswordForm";

export default function PersonnelPage() {
  return (
    <>
      <UpdateInfoForm />
      <UpdateEmailForm />
      <UpdatePasswordForm />
      <Logout />
    </>
  );
}
