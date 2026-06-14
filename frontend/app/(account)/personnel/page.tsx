import Logout from "@/components/auth/Logout";
import UpdateEmailForm from "@/components/personnel/UpdateEmailForm";
import UpdateInfoForm from "@/components/personnel/UpdateInfoForm";

export default function PersonnelPage() {
  return (
    <>
      <UpdateInfoForm />
      <UpdateEmailForm />
      <Logout />
    </>
  );
}
