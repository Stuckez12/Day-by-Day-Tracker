import PageWrapper from "components/common/PageWrapper";
import PersonnelList from "components/personnel/PersonnelList";
import CreatePersonnel from "components/personnel/CreatePersonnel";

function PersonnelPage() {
  return (
    <PageWrapper>
      <PersonnelList />
      <CreatePersonnel />
    </PageWrapper>
  );
}

export default PersonnelPage;
