import { useState } from "react";

import CreatePersonnel from "components/personnel/CreatePersonnel";
import PersonnelList from "components/personnel/PersonnelList";

import { ContextRefreshList } from "contexts/ContextRefreshList";

function ContextPersonnelList() {
  const [refreshList, setRefreshList] = useState(true);

  return (
    <ContextRefreshList.Provider value={{ refreshList, setRefreshList }}>
      <CreatePersonnel />
      <PersonnelList />
    </ContextRefreshList.Provider>
  );
}

export default ContextPersonnelList;
